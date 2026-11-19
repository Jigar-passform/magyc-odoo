from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    magyc_pick_location_id = fields.Many2one(
        "stock.location", string="Pickplatz",
        domain="[('magyc_zone', '=', 'pick')]",
        help="Fester Stellplatz in der Pickzone. Wird beim Kommissionieren bevorzugt.",
    )
