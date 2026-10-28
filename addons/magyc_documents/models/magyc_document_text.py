from odoo import fields, models


class MagycDocumentText(models.Model):
    _name = "magyc.document.text"
    _description = "Belegtext"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    doc_type = fields.Selection(
        [
            ("sale", "Angebot (B2B)"),
            ("order", "Auftragsbestätigung"),
            ("invoice", "Rechnung B2B"),
            ("invoice_kiosk", "Rechnung Kiosk (Abverkauf)"),
            ("invoice_shop", "Rechnung Onlineshop"),
            ("credit", "Gutschrift / Storno"),
            ("delivery", "Lieferschein"),
        ],
        string="Belegtyp", required=True,
    )
    intro = fields.Html(string="Einleitungstext", translate=True)
    outro = fields.Html(string="Schlusstext", translate=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    active = fields.Boolean(default=True)

    def _get_text(self, doc_type):
        return self.search([("doc_type", "=", doc_type), ("company_id", "=", self.env.company.id)], limit=1)
