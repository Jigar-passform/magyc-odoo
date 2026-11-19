from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    magyc_label_printer = fields.Char(
        string="Etikettendrucker",
        help="Name des Etikettendruckers am Arbeitsplatz Wareneingang.",
    )
    magyc_quarantine_location_id = fields.Many2one(
        "stock.location", string="Quarantänelager",
        domain="[('magyc_zone', '=', 'quarantine')]",
    )
