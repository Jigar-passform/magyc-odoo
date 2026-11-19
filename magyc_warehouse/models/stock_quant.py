from odoo import fields, models
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    magyc_bin_code = fields.Char(related="location_id.magyc_bin_code", string="Stellplatz")
    magyc_zone = fields.Selection(related="location_id.magyc_zone", string="Zone")
    magyc_expiry_date = fields.Datetime(related="lot_id.removal_date", string="MHD")
    magyc_lot_name = fields.Char(related="lot_id.name", string="Charge")

    def action_magyc_move_to_quarantine(self):
        quarantine = self.env["stock.location"].search(
            [("magyc_zone", "=", "quarantine"), ("usage", "=", "internal")], limit=1)
        if not quarantine:
            raise UserError("Kein Quarantänelager definiert.")
        lines = [(q.product_id, q.quantity) for q in self if q.quantity > 0]
        if not lines:
            return True
        self.env["stock.picking"]._magyc_transfer(
            self[0].location_id, quarantine, lines,
            "Quarantäne %s" % fields.Date.context_today(self))
        return True
