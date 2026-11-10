from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycDeliveryWizard(models.TransientModel):
    _name = "magyc.delivery.wizard"
    _description = "Erstbestückung oder Nachschub"

    partner_id = fields.Many2one(
        "res.partner", string="Kiosk", required=True,
        domain="[('kundentyp', '=', 'kiosk')]",
    )
    mode = fields.Selection(
        [("first_fill", "Erstbestückung"), ("refill", "Nachschub")],
        default="refill", required=True,
    )
    lemon_trays = fields.Integer(string="Trays Lemon", default=4)
    berry_trays = fields.Integer(string="Trays Berry", default=4)
    vehicle_location_id = fields.Many2one(
        "stock.location", string="Fahrzeuglager", domain="[('usage', '=', 'internal')]",
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    min_trays = fields.Integer(related="company_id.magyc_refill_min_trays")

    @api.onchange("mode")
    def _onchange_mode(self):
        per_product = self.company_id.magyc_first_fill_trays_per_product or 4
        if self.mode == "first_fill":
            self.lemon_trays = per_product
            self.berry_trays = per_product
        else:
            half = max((self.company_id.magyc_refill_min_trays or 4) // 2, 1)
            self.lemon_trays = half
            self.berry_trays = half

    def action_create(self):
        self.ensure_one()
        company = self.company_id
        partner = self.partner_id
        total = (self.lemon_trays or 0) + (self.berry_trays or 0)
        if total <= 0:
            raise UserError("Bitte mindestens ein Tray angeben.")
        if self.mode == "refill" and total < (company.magyc_refill_min_trays or 4):
            raise UserError(
                "Nachschub erst ab %s Trays. Aktuell %s."
                % (company.magyc_refill_min_trays or 4, total))
        if partner._magyc_overdue_invoices():
            raise UserError("Liefersperre: offene überfällige Rechnung bei %s." % partner.display_name)
        if partner.open_shortfall_count:
            raise UserError(
                "Offene Bestandsdifferenz bei %s. Zuerst klären, dann nachliefern."
                % partner.display_name)

        products = company._magyc_drink_products()
        if len(products) < 2:
            raise UserError("Es sind nicht zwei Getränkeartikel hinterlegt.")
        lines = [
            (products[0], self.lemon_trays * 24),
            (products[1], self.berry_trays * 24),
        ]
        label = "Erstbestückung" if self.mode == "first_fill" else "Nachschub"
        picking = partner._magyc_deliver(
            lines,
            "%s %s" % (label, partner.kiosk_id or partner.name),
            vehicle_location=self.vehicle_location_id,
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "res_id": picking.id,
            "view_mode": "form",
            "target": "current",
        }
