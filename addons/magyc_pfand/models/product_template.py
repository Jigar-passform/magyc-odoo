from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_pfand = fields.Boolean(
        string="Pfandartikel",
        help="Einwegpfand: wird auf Verkaufsbelegen als eigene Zeile geführt.",
    )
