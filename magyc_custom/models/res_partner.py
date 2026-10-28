from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    kiosk_id = fields.Char(
        string="Kiosk-ID",
        index=True,
        copy=False,
        help="Interne Kundennummer, z. B. K-BER-0001.",
    )
    kundentyp = fields.Selection(
        selection=[
            ("kiosk", "Kiosk (Kommission)"),
            ("b2b", "B2B"),
            ("online", "Onlineshop"),
        ],
        string="Kundentyp",
    )
    gebiet = fields.Char(string="Gebiet", help="Vertriebsgebiet, z. B. Berlin-Mitte.")
    akquisiteur = fields.Char(string="Akquisiteur")
    store_success_manager = fields.Char(string="Store Success Manager")
