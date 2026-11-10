from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    # Soll-Ablauf 01.11.2026: GLN und GTIN getrennt, Vertragslaufzeit, IBAN, Status
    kiosk_gln = fields.Char(
        string="GLN Kiosk",
        size=13,
        help="13-stellige GLN des Kiosks. Die GTIN der Artikel steht am Produkt, nicht hier.",
    )
    kiosk_iban = fields.Char(string="IBAN Kiosk", help="IBAN für die Auszahlung des Signing Bonus.")
    contract_start = fields.Date(string="Vertragsbeginn")
    contract_term_months = fields.Integer(string="Vertragslaufzeit (Monate)", default=12)
    contract_signed = fields.Boolean(string="Vertrag unterschrieben")
    contract_signed_on = fields.Date(string="Vertragsdatum")
    contract_end = fields.Date(string="Vertragsende", compute="_compute_contract_end", store=True)
    kiosk_status = fields.Selection(
        selection=[
            ("interessent", "Interessent"),
            ("vertrag_eingegangen", "Vertrag eingegangen"),
            ("erstbestueckung_geplant", "Erstbestückung geplant"),
            ("aktiv", "Aktiv"),
            ("inaktiv", "Inaktiv"),
        ],
        string="Kiosk-Status",
        default="interessent",
        tracking=True,
        copy=False,
        help="Wird über die Aktionen im MAGYC-Tab geführt, nicht berechnet.",
    )

    @api.depends("contract_start", "contract_term_months")
    def _compute_contract_end(self):
        for partner in self:
            if partner.contract_start and partner.contract_term_months:
                partner.contract_end = fields.Date.add(
                    partner.contract_start, months=partner.contract_term_months
                )
            else:
                partner.contract_end = False

    def write(self, vals):
        res = super().write(vals)
        # Vertragsflag hält den Status nach, ohne die Pipeline-Stufen zu überspringen.
        if "kiosk_status" not in vals and "contract_signed" in vals:
            if vals["contract_signed"]:
                self.filtered(
                    lambda p: p.kiosk_status in ("interessent", "vertrag_eingegangen")
                ).write({"kiosk_status": "aktiv"})
            else:
                self.filtered(lambda p: p.kiosk_status != "interessent").write(
                    {"kiosk_status": "interessent"})
        return res

    @api.constrains("kundentyp", "phone")
    def _check_kiosk_phone(self):
        for partner in self:
            if partner.kundentyp == "kiosk" and not partner.phone:
                raise ValidationError(
                    "Für Kioske ist eine Telefonnummer Pflicht (Vorgabe aus dem Soll-Ablauf)."
                )

    @api.onchange("contract_signed")
    def _onchange_contract_signed(self):
        for partner in self:
            if partner.contract_signed and not partner.contract_signed_on:
                partner.contract_signed_on = fields.Date.context_today(partner)
