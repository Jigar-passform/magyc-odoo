from odoo import api, fields, models
from odoo.exceptions import UserError


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    magyc_carrier_kind = fields.Selection(
        [("dsv", "DSV (UPS)"), ("ups", "UPS direkt"), ("dpd", "DPD"), ("dhl", "DHL")],
        string="MAGYC Versender",
    )
    magyc_api_user = fields.Char(string="API Benutzer")
    magyc_api_key = fields.Char(string="API Schluessel", password=True)
    magyc_customer_number = fields.Char(string="Kundennummer beim Versender")

    def magyc_create_label(self, picking):
        """Etikett anfordern. Ohne Zugangsdaten bewusst harter Fehler."""
        self.ensure_one()
        if not (self.magyc_api_user and self.magyc_api_key and self.magyc_customer_number):
            raise UserError(
                "Versender %s ist nicht konfiguriert: API Benutzer, Schluessel und "
                "Kundennummer fehlen. Ohne diese Daten kein Etikett." % self.name)
        raise UserError(
            "Etikettenabruf fuer %s ist noch nicht angebunden. Die Schnittstelle "
            "erwartet die DSV/UPS Auftragsbestaetigung als PDF." % self.name)
