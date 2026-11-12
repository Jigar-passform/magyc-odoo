import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Pflichtfelder, die Flixcheck mit jeder unterschriebenen Vertragsmail liefert.
MANDATORY = ("phone", "street", "zip", "city")


class MagycKioskApplication(models.Model):
    """Eingang des Kiosk-Postfachs (kiosk@).

    Flixcheck schickt nach jeder Unterschrift eine Mail mit Vertrag, Fotos und
    den Kioskdaten. Odoo legt daraus den Kiosk, das Kommissionslager und den
    Lieferauftrag fuer die Erstbestueckung an (Stufe 1). Gebucht wird erst mit
    dem unterschriebenen Uebergabeprotokoll (Stufe 2, stock.picking).
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
    duplicate_partner_id = fields.Many2one(
        "res.partner", string="Dublette von", readonly=True, copy=False,
    )
    iban = fields.Char(string="IBAN")
    tax_id = fields.Char(string="Steuernummer / USt-IdNr.")
    small_business = fields.Boolean(string="Kleinunternehmer")
    contract_date = fields.Date(string="Datum der Unterschrift")
    salesperson = fields.Char(string="Vertriebler (Flixcheck)")
    akquisiteur_id = fields.Many2one(
        "res.partner", string="Akquisiteur", domain="[('is_akquisiteur', '=', True)]",
    )
    state = fields.Selection(
        selection=[
            ("new", "Neu"),
            ("check", "Prüfen"),
            ("converted", "Kiosk angelegt"),
            ("rejected", "Abgelehnt"),
        ],
        string="Status",
        default="new",
        tracking=True,
        required=True,
    )

    # ---------------------------------------------------------------- intake
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        record = super().message_new(msg_dict, custom_values=custom_values)
        try:
            record._magyc_auto_process()
        except Exception:
            _logger.exception("Kiosk-Postfach: automatische Anlage fehlgeschlagen")
            record._magyc_check_task("Automatische Anlage fehlgeschlagen")
        return record

    def _magyc_auto_process(self):
        """Stufe 1: Kiosk, Kommissionslager und Erstbestueckung anlegen."""
        self.ensure_one()
        if self.state != "new":
            return False
        missing = [self._fields[f].string for f in MANDATORY if not self[f]]
        if missing:
            return self._magyc_check_task("Pflichtfelder fehlen: %s" % ", ".join(missing))
        duplicate = self._magyc_find_duplicate()
        if duplicate:
            self.write({"duplicate_partner_id": duplicate.id})
            return self._magyc_check_task(
                "Dublette zu %s (%s)" % (duplicate.display_name, duplicate.kiosk_id or "-")
            )
        partner = self.env["res.partner"].create(self._magyc_partner_vals())
        self._magyc_copy_attachments(partner)
        partner.action_plan_first_fill()
        self.write({"partner_id": partner.id, "state": "converted"})
        return True

    def _magyc_find_duplicate(self):
        self.ensure_one()
        partner = self.env["res.partner"]
        if self.email_from:
            found = partner.search([
                ("kundentyp", "=", "kiosk"), ("email", "=", self.email_from),
            ], limit=1)
            if found:
                return found
        if self.zip and self.name:
            return partner.search([
                ("kundentyp", "=", "kiosk"), ("zip", "=", self.zip), ("name", "=", self.name),
            ], limit=1)
        return partner

    def _magyc_partner_vals(self):
        self.ensure_one()
        company = self.env.company
        akquisiteur = self.akquisiteur_id or company.magyc_akquisiteur_partner_id
        vals = {
            "name": self.name,
            "kundentyp": "kiosk",
            "email": self.email_from,
            "phone": self.phone,
            "street": self.street,
            "zip": self.zip,
            "city": self.city,
            "kiosk_iban": self.iban,
            "kiosk_status": "vertrag_eingegangen",
            "contract_signed_on": self.contract_date,
            "company_id": company.id,
        }
        if akquisiteur:
            vals["akquisiteur_id"] = akquisiteur.id
        return vals

    def _magyc_copy_attachments(self, partner):
        self.ensure_one()
        for message in self.message_ids:
            for attachment in message.attachment_ids:
                attachment.copy({"res_model": "res.partner", "res_id": partner.id})

    def _magyc_check_task(self, summary):
        self.ensure_one()
        company = self.env.company
        self.env["mail.activity"].create({
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": summary[:120],
            "note": "Kiosk-Postfach: %s" % (self.name or self.email_from or ""),
            "res_model_id": self.env["ir.model"]._get_id(self._name),
            "res_id": self.id,
            "user_id": (company.magyc_finance_user_id or self.env.user).id,
        })
        self.write({"state": "check"})
        return False

    # ---------------------------------------------------------------- manual
    def action_create_kiosk(self):
        self.ensure_one()
        if self.partner_id:
            return self._magyc_open_partner()
        if not self.akquisiteur_id:
            self.akquisiteur_id = self.env.company.magyc_akquisiteur_partner_id
        self._magyc_auto_process()
        if self.partner_id:
            return self._magyc_open_partner()
        return True

    def _magyc_open_partner(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.partner_id.id,
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
