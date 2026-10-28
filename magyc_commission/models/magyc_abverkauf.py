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
        [("draft", "Entwurf"), ("done", "Bestätigt"), ("invoiced", "Abgerechnet")],
        default="draft", tracking=True, copy=False,
    )
    invoice_id = fields.Many2one("account.move", string="Rechnung", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    note = fields.Text()

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

    def action_confirm(self):
        """Move sold quantities out of the kiosk consignment location."""
        for rec in self:
            if rec.state != "draft":
                continue
            moves = []
            for line in rec.line_ids:
                if line.qty_sold <= 0:
                    continue
                moves.append({
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty_sold,
                    "location_id": rec.location_id.id,
                    "location_dest_id": rec._get_customer_location().id,
                })
            if moves:
                picking_type = self.env["stock.picking.type"].search(
                    [("code", "=", "outgoing"), ("warehouse_id.company_id", "=", rec.company_id.id)], limit=1
                )
                picking = self.env["stock.picking"].create({
                    "picking_type_id": picking_type.id,
                    "partner_id": rec.partner_id.id,
                    "location_id": rec.location_id.id,
                    "location_dest_id": rec._get_customer_location().id,
                    "origin": rec.name,
                    "move_ids": [(0, 0, m) for m in moves],
                })
                picking.action_confirm()
                picking.move_ids.picked = True
                picking.button_validate()
            rec.state = "done"

    def action_create_invoice(self):
        for rec in self:
            if rec.state != "done":
                raise UserError("Nur bestätigte Abverkaufsmeldungen können abgerechnet werden.")
            if rec.invoice_id:
                raise UserError("Für diese Meldung existiert bereits eine Rechnung.")
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
    qty_sold = fields.Float(string="Abverkauf (Stk)", default=0.0)
    qty_returned = fields.Float(string="Rückgabe (Stk)", default=0.0)
    price_unit = fields.Float(string="Preis netto")
    currency_id = fields.Many2one(related="abverkauf_id.company_id.currency_id")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.lst_price
