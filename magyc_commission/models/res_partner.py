from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_location_id = fields.Many2one(
        "stock.location",
        string="Kommissionslager",
        domain="[('usage', '=', 'internal')]",
        help="Lagerort beim Kiosk, an dem die Kommissionsware bis zum Abverkauf liegt.",
    )
