from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    magyc_first_fill_trays = fields.Integer(
        string="Erstbestückung Trays", default=8,
        help="Trays bei der Erstbestückung, je 24 Dosen, hälftig auf die Sorten verteilt.",
    )
    magyc_first_fill_trays_per_product = fields.Integer(
        string="Erstbestückung Trays je Sorte", default=4,
    )
    magyc_refill_min_trays = fields.Integer(
        string="Mindestmenge Nachschub (Trays)", default=4,
    )
    magyc_return_months = fields.Integer(
        string="Rücknahme unverkaufter Ware (Monate)", default=6,
    )
    magyc_akquisiteur_fee = fields.Monetary(
        string="Akquisiteur-Provision je Kiosk", default=50.0,
        currency_field="currency_id",
    )
    magyc_akquisiteur_product_id = fields.Many2one(
        "product.product", string="Artikel Akquisiteur-Provision",
        help="Wird als Position auf der Monatsrechnung des Akquisiteurs verwendet.",
    )
    magyc_bonus_amount = fields.Monetary(
        string="Startprämie Kiosk", default=50.0, currency_field="currency_id",
    )
    magyc_trays_per_pallet = fields.Integer(
        string="Trays je Palette", default=12,
        help="Für den Speditionstransfer. ponytail: Annahme 12 Trays; von MAGYC bestätigen lassen.",
    )
    magyc_pfand_shop_price = fields.Monetary(
        string="Pfand Onlineshop (brutto)", default=0.25, currency_field="currency_id",
        help="Bruttopreis im Onlineshop. Kiosk und B2B rechnen 0,25 EUR netto ab.",
    )
    magyc_finance_user_id = fields.Many2one(
        "res.users", string="Zuständig für Auszahlungen",
        help="Erhält Aufgaben für Startprämie und Akquisiteur-Abrechnung.",
    )

    def _magyc_drink_products(self):
        """Die beiden Launch-Sorten. ponytail: über die ersten zwei Artikel
        ermittelt; bei mehr Sorten auf ein Firmenfeld umstellen."""
        return self.env["product.product"].search([
            ("product_tmpl_id.is_pfand", "=", False),
            ("type", "=", "consu"),
            ("sale_ok", "=", True),
        ], order="id", limit=2)

