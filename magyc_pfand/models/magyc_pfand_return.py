from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycPfandReturn(models.Model):
    _name = "magyc.pfand.return"
    _description = "Pfand-Rücknahme (Leergut)"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    partner_id = fields.Many2one("res.partner", string="Kunde / Kiosk", required=True, tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    line_ids = fields.One2many("magyc.pfand.return.line", "return_id", string="Positionen")
    state = fields.Selection([("draft", "Entwurf"), ("done", "Abgerechnet")],
                             default="draft", tracking=True, copy=False)
    credit_note_id = fields.Many2one("account.move", string="Gutschrift", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    qty_total = fields.Float(string="Menge gesamt", compute="_compute_totals", store=True)
    amount_untaxed = fields.Monetary(string="Betrag netto", compute="_compute_totals", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    note = fields.Text()

    @api.depends("partner_id", "date")
    def _compute_name(self):
        for rec in self:
            rec.name = "Pfand %s %s" % (rec.partner_id.display_name or "", rec.date or "")

    @api.depends("line_ids.qty", "line_ids.price_unit")
    def _compute_totals(self):
        for rec in self:
            rec.qty_total = sum(rec.line_ids.mapped("qty"))
            rec.amount_untaxed = sum(l.qty * l.price_unit for l in rec.line_ids)

    def action_create_credit_note(self):
        for rec in self:
            if rec.state != "draft":
                continue
            lines = [(0, 0, {
                "product_id": line.product_id.id,
                "name": line.product_id.display_name,
                "quantity": line.qty,
                "price_unit": line.price_unit,
                "tax_ids": [(6, 0, line.product_id.taxes_id.ids)],
            }) for line in rec.line_ids if line.qty > 0]
            if not lines:
                raise UserError("Keine Rückgabemenge erfasst.")
            move = self.env["account.move"].create({
                "move_type": "out_refund",
                "partner_id": rec.partner_id.id,
                "invoice_date": rec.date,
                "invoice_origin": rec.name,
                "invoice_line_ids": lines,
            })
            move.action_post()
            rec.credit_note_id = move
            rec.state = "done"

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        pfand = self.env.company.pfand_product_id
        if pfand and not self.line_ids:
            self.line_ids = [(0, 0, {"product_id": pfand.id, "price_unit": pfand.lst_price})]


class MagycPfandReturnLine(models.Model):
    _name = "magyc.pfand.return.line"
    _description = "Pfand-Rücknahme Position"

    return_id = fields.Many2one("magyc.pfand.return", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product", string="Pfandartikel", required=True,
        domain="[('is_pfand', '=', True)]",
    )
    qty = fields.Float(string="Menge (Stk)", default=0.0)
    price_unit = fields.Float(string="Pfand je Stk")
