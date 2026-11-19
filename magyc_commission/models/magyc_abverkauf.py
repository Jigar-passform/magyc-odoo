from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycAbverkauf(models.Model):
    _name = "magyc.abverkauf"
    _description = "Abverkaufsmeldung Kiosk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    partner_id = fields.Many2one(
        "res.partner", string="Kiosk", required=True, tracking=True,
        domain="[('kundentyp', '=', 'kiosk')]",
    )
    location_id = fields.Many2one(
        "stock.location", string="Kommissionslager", required=True, tracking=True,
        domain="[('usage', '=', 'internal')]",
        help="Lagerort beim Kiosk, an dem die Kommissionsware liegt.",
    )
    date_from = fields.Date(string="Zeitraum von", required=True)
    date_to = fields.Date(string="Zeitraum bis", required=True)
    line_ids = fields.One2many("magyc.abverkauf.line", "abverkauf_id", string="Positionen")
    state = fields.Selection(
        [("draft", "Entwurf"), ("review", "Prüfung Differenz"),
         ("done", "Bestätigt"), ("invoiced", "Abgerechnet")],
        string="Status", default="draft", tracking=True, copy=False,
    )
    invoice_id = fields.Many2one("account.move", string="Rechnung", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()
    qty_sold_total = fields.Float(string="Abverkauf gesamt", compute="_compute_totals", store=True)
    qty_returned_total = fields.Float(string="Rückgabe gesamt", compute="_compute_totals", store=True)
    qty_shortfall_total = fields.Float(string="Differenz gesamt", compute="_compute_totals", store=True)
    shortfall_cleared = fields.Boolean(string="Differenz geklärt", tracking=True, copy=False,
                                       help="Ohne Klärung wird keine Rechnung erstellt.")
    amount_untaxed = fields.Monetary(string="Betrag netto", compute="_compute_totals", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")

    @api.depends("line_ids.qty_sold", "line_ids.qty_returned", "line_ids.qty_shortfall",
                 "line_ids.price_unit")
    def _compute_totals(self):
        for rec in self:
            rec.qty_sold_total = sum(rec.line_ids.mapped("qty_sold"))
            rec.qty_returned_total = sum(rec.line_ids.mapped("qty_returned"))
            rec.qty_shortfall_total = sum(rec.line_ids.mapped("qty_shortfall"))
            rec.amount_untaxed = sum(l.qty_sold * l.price_unit for l in rec.line_ids)

    @api.depends("partner_id", "date_from", "date_to")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s–%s" % (
                rec.partner_id.kiosk_id or rec.partner_id.display_name or "",
                rec.date_from or "", rec.date_to or "",
            )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise UserError("Der Zeitraum ist ungültig: 'von' liegt nach 'bis'.")

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            if rec.partner_id.commission_location_id and not rec.location_id:
                rec.location_id = rec.partner_id.commission_location_id

    def _get_customer_location(self):
        return self.env.ref("stock.stock_location_customers")

    def _get_warehouse_location(self):
        return self.env["stock.warehouse"].search(
            [("company_id", "=", self.company_id.id)], limit=1
        ).lot_stock_id

    def _get_return_location(self):
        """Rückgaben gehen in die Qualitätssperre, nicht direkt in den Verkauf."""

        company = self.company_id
        quality = company._magyc_default_quality_location()
        if quality:
            return quality
        return self._get_warehouse_location()

    def _magyc_allocate_lots(self, product, qty):
        """Split a quantity across the lots at the kiosk location, FEFO first."""
        self.ensure_one()
        quants = self.env["stock.quant"].search([
            ("product_id", "=", product.id),
            ("location_id", "=", self.location_id.id),
            ("lot_id", "!=", False),
            ("quantity", ">", 0),
        ])
        # MHD sitzt am Los, nicht am Quant (Odoo 20 kennt kein quant.removal_date).
        quants = quants.sorted(lambda q: (q.lot_id.removal_date or datetime.max, q.id))
        allocation, remaining = [], qty
        for quant in quants:
            if remaining <= 0:
                break
            take = min(quant.quantity, remaining)
            allocation.append((quant.lot_id, take))
            remaining -= take
        if remaining > 0:
            base = "%s-%s" % (product.default_code or product.id, fields.Date.context_today(self))
            name, counter = base, 1
            while self.env["stock.lot"].search_count([
                    ("name", "=", name), ("product_id", "=", product.id)], limit=1):
                counter += 1
                name = "%s-%s" % (base, counter)
            allocation.append((self.env["stock.lot"].create({
                "name": name,
                "product_id": product.id,
                "company_id": self.company_id.id,
            }), remaining))
        return allocation

    def _create_picking(self, rec, lines, dest_location, origin_suffix):
        moves, allocations = [], {}
        for line, qty in lines:
            if qty <= 0:
                continue
            product = line.product_id
            moves.append({
                "product_id": product.id,
                "product_uom_qty": qty,
                "location_id": rec.location_id.id,
                "location_dest_id": dest_location.id,
            })
            if product.tracking != "none":
                allocations[product.id] = rec._magyc_allocate_lots(product, qty)
        if not moves:
            return None
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("warehouse_id.company_id", "=", rec.company_id.id)], limit=1
        )
        picking = self.env["stock.picking"].create({
            "picking_type_id": picking_type.id,
            "partner_id": rec.partner_id.id,
            "location_id": rec.location_id.id,
            "location_dest_id": dest_location.id,
            "origin": "%s %s" % (rec.name, origin_suffix),
            "move_ids": [(0, 0, m) for m in moves],
        })
        for move in picking.move_ids:
            allocation = allocations.get(move.product_id.id)
            if not allocation:
                continue
            move.move_line_ids.unlink()
            self.env["stock.move.line"].create([{
                "move_id": move.id,
                "product_id": move.product_id.id,
                "lot_id": lot.id,
                "quantity": allocated,
                "location_id": rec.location_id.id,
                "location_dest_id": dest_location.id,
            } for lot, allocated in allocation])
        picking.action_confirm()
        picking.move_ids.picked = True
        picking.with_context(skip_sms=True).button_validate()
        return picking

    @api.model
    def _cron_missing_counts(self):
        """Kioske ohne Abverkaufsmeldung für den Vormonat erinnern."""

        today = fields.Date.context_today(self)
        first_this_month = today.replace(day=1)
        last_month_end = fields.Date.subtract(first_this_month, days=1)
        last_month_start = last_month_end.replace(day=1)
        kiosks = self.env["res.partner"].search([
            ("kundentyp", "=", "kiosk"), ("kiosk_status", "=", "aktiv")])
        for kiosk in kiosks:
            exists = self.search_count([
                ("partner_id", "=", kiosk.id),
                ("date_from", "<=", last_month_end),
                ("date_to", ">=", last_month_start),
            ])
            if exists:
                continue
            self.env["mail.activity"].create({
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "summary": "Abverkauf %s fehlt" % last_month_start.strftime("%m/%Y"),
                "note": "Für diesen Kiosk liegt keine Bestandsaufnahme vor.",
                "res_model_id": self.env["ir.model"]._get_id("res.partner"),
                "res_id": kiosk.id,
                "user_id": (kiosk.user_id.id or self.env.user.id),
            })

    def action_flag_shortfall(self):
        """Differenz der Bestandsaufnahme als Prüfaufgabe beim Kiosk anlegen."""
        for rec in self:
            if not rec.qty_shortfall_total:
                continue
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Bestandsdifferenz prüfen",
                note="Gezählter Bestand ist höher als der Systembestand. Vor der Rechnung klären.",
                user_id=(rec.partner_id.user_id.id or self.env.user.id),
            )
            rec.state = "review"
            rec.message_post(body="Differenz von %.0f Stück erkannt, Rechnung gesperrt." % rec.qty_shortfall_total)

    def action_clear_shortfall(self):
        for rec in self:
            rec.shortfall_cleared = True
            rec.state = "draft" if rec.state == "review" else rec.state
            rec.activity_feedback(["mail.mail_activity_data_todo"], feedback="Differenz geklärt.")

    def action_confirm(self):
        """Book sold quantities out to the kiosk and returns back to the warehouse."""
        for rec in self:
            if rec.state not in ("draft",):
                raise UserError("Nur Entwürfe können bestätigt werden. Zuerst die Differenz klären.")
            if rec.qty_shortfall_total and not rec.shortfall_cleared:
                raise UserError("Bestandsdifferenz offen. Bitte zuerst prüfen und freigeben.")
            self._create_picking(rec, [(l, l.qty_sold) for l in rec.line_ids],
                                 rec._get_customer_location(), "Abverkauf")
            self._create_picking(rec, [(l, l.qty_returned) for l in rec.line_ids],
                                 rec._get_return_location(), "Rückgabe")
            rec.state = "done"

    def action_create_invoice(self):
        for rec in self:
            if rec.state != "done":
                raise UserError("Nur bestätigte Abverkaufsmeldungen können abgerechnet werden.")
            if rec.invoice_id:
                raise UserError("Für diese Meldung existiert bereits eine Rechnung.")
            if rec.qty_shortfall_total and not rec.shortfall_cleared:
                raise UserError("Bestandsdifferenz ist noch nicht geklärt.")
            if rec.qty_sold_total < 24:
                raise UserError(
                    "Rechnung erst ab 24 Dosen. Aktuell sind %.0f Stück erfasst, "
                    "die Meldung bleibt offen." % rec.qty_sold_total
                )
            lines = []
            for line in rec.line_ids:
                if line.qty_sold <= 0:
                    continue
                lines.append((0, 0, {
                    "product_id": line.product_id.id,
                    "name": line.product_id.display_name,
                    "quantity": line.qty_sold,
                    "price_unit": line.price_unit,
                    "tax_ids": [(6, 0, line.product_id.taxes_id.ids)],
                }))
            pfand = rec.company_id.pfand_product_id
            if (rec.partner_id.kundentyp == "kiosk" and rec.company_id.pfand_auto_add and pfand):
                lines.append((0, 0, {
                    "product_id": pfand.id,
                    "name": pfand.display_name,
                    "quantity": rec.qty_sold_total,
                    "price_unit": pfand.lst_price,
                    "tax_ids": [(6, 0, pfand.taxes_id.ids)],
                }))
            if not lines:
                raise UserError("Keine Abverkaufsmenge erfasst.")
            move = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": rec.partner_id.id,
                "invoice_date": fields.Date.context_today(rec),
                "invoice_origin": rec.name,
                "invoice_line_ids": lines,
            })
            move.action_post()
            rec.invoice_id = move
            rec.state = "invoiced"


class MagycAbverkaufLine(models.Model):
    _name = "magyc.abverkauf.line"
    _description = "Abverkaufszeile"

    abverkauf_id = fields.Many2one("magyc.abverkauf", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Artikel", required=True)
    qty_expected = fields.Float(string="Bestand laut System", default=0.0)
    qty_counted = fields.Float(
        string="Gezählt (SSM)", default=0.0,
        help="Bestand, den der Store Success Manager beim Kiosk gezählt hat.",
    )
    qty_sold = fields.Float(
        string="Abverkauf (Stk)", default=0.0,
        help="Menge, die in Rechnung gestellt wird. Basis ist die Bestandsaufnahme.",
    )
    qty_returned = fields.Float(string="Rückgabe (Stk)", default=0.0)
    qty_shortfall = fields.Float(
        string="Differenz", compute="_compute_shortfall", store=True,
        help="Ware, die weder gezählt noch abgerechnet noch zurückgemeldet ist.",
    )
    price_unit = fields.Float(string="Preis netto")
    currency_id = fields.Many2one(related="abverkauf_id.company_id.currency_id")

    @api.depends("qty_expected", "qty_counted", "qty_sold", "qty_returned")
    def _compute_shortfall(self):
        for line in self:
            line.qty_shortfall = max(
                (line.qty_expected or 0.0) - (line.qty_counted or 0.0)
                - (line.qty_sold or 0.0) - (line.qty_returned or 0.0), 0.0)

    @api.onchange("qty_expected", "qty_counted", "qty_returned")
    def _onchange_qty_counted(self):
        for line in self:
            if line.qty_counted:
                line.qty_sold = max(
                    (line.qty_expected or 0.0) - (line.qty_counted or 0.0)
                    - (line.qty_returned or 0.0), 0.0)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id:
                continue
            line.price_unit = line.product_id.lst_price
            location = line.abverkauf_id.location_id
            if location:
                quant = self.env["stock.quant"].search([
                    ("product_id", "=", line.product_id.id),
                    ("location_id", "=", location.id),
                ], limit=1)
                line.qty_expected = quant.quantity or 0.0
