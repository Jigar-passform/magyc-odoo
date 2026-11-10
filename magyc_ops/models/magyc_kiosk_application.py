from odoo import api, fields, models


class MagycKioskApplication(models.Model):
    """Eingang des Kiosk-Postfachs (kiosk@): Bewerbungen und Rückfragen.

    Bewusst ohne automatische Kiosk-Anlage: die Telefonnummer ist Pflicht und
    steht selten in der Mail. Ein Klick öffnet das Partnerformular vorbefüllt.
    """

    _name = "magyc.kiosk.application"
    _description = "Kiosk-Bewerbung (Postfach)"
    _inherit = ["mail.thread", "mail.alias.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Betreff", required=True, default="Kiosk-Bewerbung")
    email_from = fields.Char(string="E-Mail")
    phone = fields.Char(string="Telefon")
    street = fields.Char(string="Straße")
    zip = fields.Char(string="PLZ")
    city = fields.Char(string="Ort")
    message = fields.Text(string="Nachricht")
    partner_id = fields.Many2one("res.partner", string="Kiosk", readonly=True, copy=False)
    state = fields.Selection(
        selection=[("new", "Neu"), ("converted", "Kiosk angelegt"), ("rejected", "Abgelehnt")],
        string="Status",
        default="new",
        tracking=True,
        required=True,
    )

    def action_create_kiosk(self):
        self.ensure_one()
        kiosk = self.env["res.partner"].create({
            "name": self.name or self.email_from or "Kiosk",
            "kundentyp": "kiosk",
            "email": self.email_from,
            "phone": self.phone,
            "street": self.street,
            "zip": self.zip,
            "city": self.city,
        })
        self.write({"partner_id": kiosk.id, "state": "converted"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": kiosk.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_reject(self):
        self.write({"state": "rejected"})

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env["ir.model"]._get_id(self._name)
        values["alias_defaults"] = {"state": "new"}
        return values
