from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycReceiptWizard(models.TransientModel):
    """Wareneingang aus der Bestellung: Zeilen vorbelegt, je Charge duplizierbar."""

    _name = "magyc.receipt.wizard"
    _description = "Wareneingang buchen"

    picking_id = fields.Many2one("stock.picking", string="Wareneingang", required=True)
    purchase_id = fields.Many2one("purchase.order", string="Bestellung", required=True)
    line_ids = fields.One2many("magyc.receipt.line", "wizard_id", string="Positionen")
    label_count = fields.Integer(
        string="Etiketten drucken", default=0,
        help="Anzahl Stellplatz-Etiketten nach der Buchung (ohne Charge und MHD).",
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    @api.onchange("purchase_id")
    def _onchange_purchase(self):
        self.line_ids = [(5, 0, 0)]
        for po_line in self.purchase_id.order_line.filtered(lambda l: not l.display_type):
            default_bin = self.env.company.magyc_quarantine_location_id or self.env["stock.location"].search(
                [("magyc_zone", "=", "general"), ("magyc_bin_code", "!=", False)], limit=1)
            self.line_ids = [(0, 0, {
                "product_id": po_line.product_id.id,
                "qty": po_line.product_qty - po_line.qty_received,
                "po_line_id": po_line.id,
                "location_dest_id": default_bin.id,
            })]

    def action_book(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Keine Positionen erfasst.")
        picking = self.picking_id
        used = self.env["stock.move.line"]  # je Position eine eigene Bewegungszeile
        for line in self.line_ids:
            if line.qty <= 0:
                continue
            lot = line.lot_id
            if not lot and line.lot_name:
                lot = self.env["stock.lot"].create({
                    "name": line.lot_name,
                    "product_id": line.product_id.id,
                    "company_id": self.company_id.id,
                    "expiration_date": line.expiry_date,
                })
                line.lot_id = lot  # Charge an der Position halten, sonst fehlt sie in der Buchung
            move = picking.move_ids.filtered(lambda m: m.product_id == line.product_id)[:1]
            if not move:
                move = self.env["stock.move"].create({
                    "name": line.product_id.display_name,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty,
                    "uom_id": line.product_id.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": line.location_dest_id.id,
                })
            # Bestehende Reservierungszeile weiterverwenden, sonst entsteht eine
            # zweite Zeile ohne Charge und die Buchung scheitert.
            move_lines = (move.move_line_ids - used).filtered(lambda ml: ml.quantity > 0)[:1]
            vals = {
                "product_id": line.product_id.id,
                "quantity": line.qty,
                "lot_id": lot.id if lot else False,
                "location_id": picking.location_id.id,
                "location_dest_id": line.location_dest_id.id,
            }
            if move_lines:
                move_lines.write(vals)
            else:
                move_lines = self.env["stock.move.line"].create(dict(vals, move_id=move.id))
            used |= move_lines
        picking.move_ids.picked = True
        picking.with_context(skip_backorder=True, cancel_backorder=True, skip_sms=True).button_validate()
        if self.label_count:
            return {
                "type": "ir.actions.act_window",
                "name": "Etiketten",
                "res_model": "magyc.label.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_picking_id": picking.id,
                    "default_label_count": self.label_count,
                },
            }
        return {"type": "ir.actions.act_window_close"}


class MagycReceiptLine(models.TransientModel):
    _name = "magyc.receipt.line"
    _description = "Wareneingang Position"

    wizard_id = fields.Many2one("magyc.receipt.wizard", required=True, ondelete="cascade")
    po_line_id = fields.Many2one("purchase.order.line", string="Bestellposition")
    product_id = fields.Many2one("product.product", string="Artikel", required=True)
    lot_id = fields.Many2one("stock.lot", string="Charge", domain="[('product_id', '=', product_id)]")
    lot_name = fields.Char(string="Charge neu")
    expiry_date = fields.Datetime(string="MHD")
    qty = fields.Float(string="Menge (Stk)", default=0.0)
    location_dest_id = fields.Many2one(
        "stock.location", string="Stellplatz", required=True,
        domain="[('magyc_bin_code','!=',False),('usage','=','internal')]",
        help="Fach, in das die Ware eingeräumt wird. Bei unklarer Ware das Quarantänelager.",
    )
