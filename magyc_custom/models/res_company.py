from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    magyc_delivery_block = fields.Boolean(
        string="Liefersperre bei überfälligen Rechnungen",
        default=True,
        help="Bestätigen eines Auftrags wird blockiert, wenn der Kunde überfällige Rechnungen hat.",
    )
    magyc_delivery_block_days = fields.Integer(
        string="Toleranz in Tagen",
        default=0,
        help="Anzahl Tage nach Fälligkeit, bevor die Liefersperre greift.",
    )
