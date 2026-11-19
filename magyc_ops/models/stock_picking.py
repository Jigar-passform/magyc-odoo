from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    magyc_is_first_fill = fields.Boolean(string="Erstbestückung", copy=False)
    magyc_handover_confirmed = fields.Boolean(
        string="Übergabe bestätigt", copy=False, tracking=True,
        help="Unterschriebenes Übergabeprotokoll liegt vor. Löst Startprämie und "
             "Akquisiteur-Provision aus.",
    )
    magyc_handover_date = fields.Date(string="Übergabedatum", copy=False)
    magyc_tour_id = fields.Many2one("magyc.tour", string="Tour", copy=False, ondelete="set null")
    magyc_stop_sequence = fields.Integer(string="Stopp-Reihenfolge", copy=False)
    magyc_is_return_6m = fields.Boolean(string="6-Monats-Rücknahme", copy=False)

    # ------------------------------------------------------------------ build
    @api.model
    def _magyc_delivery_picking_type(self, warehouse, code="outgoing"):
        PickingType = self.env["stock.picking.type"]
        picking_type = PickingType.search(
            [("code", "=", code), ("warehouse_id", "=", warehouse.id)], limit=1)
        if not picking_type:
            # ponytail: Fallback auf einen Typ ohne Lagerzuordnung; Lager mit
            # eigenen Typen anlegen, sobald Köln produktiv geht.
            picking_type = PickingType.with_context(active_test=False).search(
                [("code", "=", code)], limit=1)
        if not picking_type:
            raise UserError("Kein Lagerbewegungstyp '%s' im Lager %s." % (code, warehouse.name))
        return picking_type

    @api.model
    def _magyc_lot_lines(self, product, location, qty):
        """FEFO: Charden mit frühestem MHD zuerst, Sortierung über das Los."""
        quants = self.env["stock.quant"].search([
            ("product_id", "=", product.id),
            ("location_id", "=", location.id),
            ("quantity", ">", 0),
        ])
        quants = quants.sorted(lambda q: (q.lot_id.removal_date or datetime.max, q.id))
        allocation, remaining = [], qty
        for quant in quants:
            if remaining <= 0:
                break
            take = min(quant.quantity, remaining)
            allocation.append((quant.lot_id, take))
            remaining -= take
        if remaining > 0:
            raise UserError(
                "Zu wenig Bestand für %s in %s: %.0f Stück fehlen. "
                "Bitte Wareneingang buchen oder Menge anpassen."
                % (product.display_name, location.complete_name, remaining)
            )
        return allocation

    @api.model
    def _magyc_create_kiosk_delivery(self, partner, lines, origin,
                                     vehicle_location=None, first_fill=False,
                                     validate=True):
        """Lieferung an einen Kiosk: Ware bleibt MAGYC-Bestand im Kommissionslager.

        validate=False laesst die Lieferung bestaetigt stehen. Sie wird erst mit
        dem unterschriebenen Uebergabeprotokoll gebucht (Stufe 2 des Ablaufs).
        """
        partner.ensure_one()
        company = partner.company_id or self.env.company
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1)
        if not warehouse:
            raise UserError("Kein Lager für %s eingerichtet." % company.name)
        dest = partner.commission_location_id
        if not dest:
            raise UserError("Für %s existiert kein Kommissionslager." % partner.display_name)
        source = vehicle_location or warehouse.lot_stock_id
        picking_type = self._magyc_delivery_picking_type(warehouse)

        moves = [(0, 0, {
            "product_id": product.id,
            "product_uom_qty": qty,
            "uom_id": product.uom_id.id,
            "location_id": source.id,
            "location_dest_id": dest.id,
        }) for product, qty in lines if qty > 0]
        if not moves:
            raise UserError("Keine Menge für die Lieferung angegeben.")
        picking = self.create({
            "picking_type_id": picking_type.id,
            "partner_id": partner.id,
            "location_id": source.id,
            "location_dest_id": dest.id,
            "origin": origin,
            "magyc_is_first_fill": first_fill,
            "magyc_vehicle_location_id": (vehicle_location or source).id,
            "move_ids": moves,
        })
        if validate:
            # Chargen erst beim Buchen ziehen: Stufe 1 plant nur den Auftrag.
            picking._magyc_allocate_missing_lots()
        picking.action_confirm()
        if validate:
            picking.move_ids.picked = True
            picking.with_context(skip_backorder=True, cancel_backorder=True, skip_sms=True).button_validate()
        return picking

    @api.model
    def _magyc_create_return(self, partner, lines, origin, dest_location, source_location=None):
        partner.ensure_one()
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", (partner.company_id or self.env.company).id)], limit=1)
        source = source_location or partner.commission_location_id
        picking_type = self._magyc_delivery_picking_type(warehouse, "internal")
        picking = self.create({
            "picking_type_id": picking_type.id,
            "partner_id": partner.id,
            "location_id": source.id,
            "location_dest_id": dest_location.id,
            "origin": origin,
            "move_ids": [(0, 0, {
                "product_id": product.id,
                "product_uom_qty": qty,
                "uom_id": product.uom_id.id,
                "location_id": source.id,
                "location_dest_id": dest_location.id,
            }) for product, qty in lines if qty > 0],
        })
        for move in picking.move_ids:
            if move.product_id.tracking == "none":
                continue
            move.move_line_ids.unlink()
            allocation = self._magyc_lot_lines(move.product_id, source, move.product_uom_qty)
            self.env["stock.move.line"].create([{
                "move_id": move.id,
                "product_id": move.product_id.id,
                "lot_id": lot.id,
                "quantity": qty,
                "location_id": source.id,
                "location_dest_id": dest_location.id,
            } for lot, qty in allocation])
        picking.action_confirm()
        picking.move_ids.picked = True
        picking.with_context(skip_backorder=True, cancel_backorder=True, skip_sms=True).button_validate()
        return picking

    @api.model
    def _magyc_transfer(self, source_location, dest_location, lines, origin):
        """Speditionstransfer zwischen zwei Lägern (z. B. Berlin -> Köln)."""
        warehouse = self.env["stock.warehouse"].search(
            [("lot_stock_id", "=", source_location.id)], limit=1)
        if not warehouse:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", source_location.company_id.id)], limit=1)
        picking_type = self._magyc_delivery_picking_type(warehouse, "internal")
        picking = self.create({
            "picking_type_id": picking_type.id,
            "location_id": source_location.id,
            "location_dest_id": dest_location.id,
            "origin": origin,
            "move_ids": [(0, 0, {
                "product_id": product.id,
                "product_uom_qty": qty,
                "uom_id": product.uom_id.id,
                "location_id": source_location.id,
                "location_dest_id": dest_location.id,
            }) for product, qty in lines if qty > 0],
        })
        for move in picking.move_ids:
            if move.product_id.tracking == "none":
                continue
            move.move_line_ids.unlink()
            allocation = self._magyc_lot_lines(move.product_id, source_location,
                                               move.product_uom_qty)
            self.env["stock.move.line"].create([{
                "move_id": move.id,
                "product_id": move.product_id.id,
                "lot_id": lot.id,
                "quantity": qty,
                "location_id": source_location.id,
                "location_dest_id": dest_location.id,
            } for lot, qty in allocation])
        picking.action_confirm()
        picking.move_ids.picked = True
        picking.with_context(skip_backorder=True, cancel_backorder=True, skip_sms=True).button_validate()
        return picking

    def _magyc_allocate_missing_lots(self):
        """FEFO-Chargen fuer alle Moves ohne Zeilen nachziehen."""
        for picking in self:
            for move in picking.move_ids:
                if move.product_id.tracking == "none" or move.move_line_ids:
                    continue
                allocation = self.env["stock.picking"]._magyc_lot_lines(
                    move.product_id, picking.location_id, move.product_uom_qty)
                self.env["stock.move.line"].create([{
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "lot_id": lot.id,
                    "quantity": qty,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                } for lot, qty in allocation])
        return True

    # --------------------------------------------------------------- handover
    def action_confirm_handover(self):
        for picking in self:
            if not picking.magyc_is_handover:
                raise UserError("Nur Kommissionslieferungen an Kioske haben ein Übergabeprotokoll.")
            if picking.magyc_handover_confirmed:
                continue
            if not picking.magyc_signature:
                raise UserError(
                    "Ohne Unterschrift im Uebergabeprotokoll wird nicht gebucht.")
            if not picking.magyc_photo:
                raise UserError(
                    "Foto des bestueckten Kuehlschranks fehlt im Uebergabeprotokoll.")
            picking.write({
                "magyc_handover_confirmed": True,
                "magyc_handover_date": fields.Date.context_today(picking),
            })
            # Erst die Unterschrift bucht die Ware vom Fahrzeug ins Kommissionslager.
            if picking.state not in ("done", "cancel"):
                picking._magyc_allocate_missing_lots()
                picking.move_ids.picked = True
                picking.with_context(skip_backorder=True, cancel_backorder=True, skip_sms=True).button_validate()
            kiosk = picking.partner_id
            kiosk.write({
                "kiosk_status": "aktiv",
                "magyc_activation_date": fields.Date.context_today(picking),
            })
            picking._magyc_trigger_bonus()
            picking._magyc_trigger_akquisiteur_bonus()
        return True

    def _magyc_trigger_akquisiteur_bonus(self):
        """Provision des Akquisiteurs (Primewave) je aktiviertem Kiosk."""
        self.ensure_one()
        kiosk = self.partner_id
        company = kiosk.company_id or self.env.company
        akquisiteur = kiosk.akquisiteur_id
        if not akquisiteur:
            return False
        fee = kiosk.magyc_akquisiteur_fee or company.magyc_akquisiteur_fee
        finance = company.magyc_finance_user_id or self.env.user
        self.env["mail.activity"].create({
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": "Akquisiteur-Provision buchen (%s)" % (kiosk.kiosk_id or kiosk.name),
            "note": "%.2f EUR fuer %s, Kiosk %s. Monatliche Sammelrechnung."
                    % (fee, akquisiteur.name, kiosk.kiosk_id or kiosk.name),
            "res_model_id": self.env["ir.model"]._get_id("res.partner"),
            "res_id": akquisiteur.id,
            "user_id": finance.id,
        })
        return True

    def _magyc_trigger_bonus(self):
        self.ensure_one()
        kiosk = self.partner_id
        company = kiosk.company_id or self.env.company
        if kiosk.kundentyp != "kiosk" or kiosk.magyc_bonus_state != "none":
            return
        finance = company.magyc_finance_user_id or self.env.user
        if kiosk.kiosk_iban:
            kiosk.magyc_bonus_state = "open"
            summary = "Startprämie zahlen (%s)" % kiosk.kiosk_id
            note = ("%.2f EUR zzgl. USt an %s, IBAN %s. Fällig mit unterschriebenem "
                    "Übergabeprotokoll." % (company.magyc_bonus_amount, kiosk.name, kiosk.kiosk_iban))
        else:
            summary = "IBAN für Startprämie fehlt (%s)" % (kiosk.kiosk_id or kiosk.name)
            note = "Ohne IBAN keine Auszahlung der Startprämie."
        self.env["mail.activity"].create({
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": summary,
            "note": note,
            "res_model_id": self.env["ir.model"]._get_id("res.partner"),
            "res_id": kiosk.id,
            "user_id": finance.id,
        })
