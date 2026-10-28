from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    pfand_product_id = fields.Many2one(
        "product.product", string="Pfandartikel",
        help="Artikel, der als Pfandzeile auf Aufträgen ergänzt wird.",
    )
    pfand_auto_add = fields.Boolean(
        string="Pfand automatisch ergänzen",
        help="Beim Bestätigen eines Auftrags je Getränkezeile eine Pfandzeile in gleicher Menge anlegen.",
    )
