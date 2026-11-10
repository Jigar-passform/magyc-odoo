from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

KIOSK_AREAS = [("BER", "Berlin"), ("KOE", "Köln")]


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Akquisiteur als Partner, damit die Monatsrechnung eindeutig zuordenbar ist.
    akquisiteur_id = fields.Many2one(
        "res.partner", string="Akquisiteur (Provision)",
        domain="[('is_akquisiteur', '=', True)]",
    )
    is_akquisiteur = fields.Boolean(string="Akquisiteur")
    magyc_akquisiteur_fee = fields.Monetary(
        string="Provision je Kiosk", currency_field="currency_id",
        help="Leer lassen, dann gilt der Firmenwert.",
    )
    kiosk_area = fields.Selection(
        KIOSK_AREAS, string="Gebiet (Kürzel)",
        help="Steuert die Kiosk-ID: K-BER-0001 bzw. K-KOE-0001.",
    )
    magyc_bonus_state = fields.Selection(
        [("none", "Keine"), ("open", "Offen"), ("paid", "Ausgezahlt")],
        string="Startprämie", default="none", copy=False, tracking=True,
    )
    magyc_bonus_paid_on = fields.Date(string="Startprämie ausgezahlt am", copy=False)
    placement_rows = fields.Integer(string="Kühlschrankreihen", default=0)
    placement_ok = fields.Boolean(
        string="Platzierung ok", compute="_compute_placement_ok", store=True,
    )
    placement_photo = fields.Image(
        string="Foto Platzierung", max_width=1024, max_height=1024, attachment=True,
    )
    open_shortfall_count = fields.Integer(
        string="Offene Differenzen", compute="_compute_open_shortfall",
    )

    @api.depends("placement_rows")
    def _compute_placement_ok(self):
        for partner in self:
            partner.placement_ok = partner.placement_rows >= 2

    def _compute_open_shortfall(self):
        abverkauf = self.env["magyc.abverkauf"]
        for partner in self:
            partner.open_shortfall_count = abverkauf.search_count([
                ("partner_id", "=", partner.id),
                ("qty_shortfall_total", ">", 0),
                ("shortfall_cleared", "=", False),
            ])

    # ---------------------------------------------------------------- Kiosk-ID
    @api.model
    def _magyc_area_code(self, vals):
        text = " ".join(
            str(vals.get(key) or "") for key in ("kiosk_area", "gebiet", "city", "state_id")
        ).lower()
        if vals.get("kiosk_area") in ("BER", "KOE"):
            return vals["kiosk_area"]
        if "köln" in text or "koeln" in text:
            return "KOE"
        return "BER"

    @api.model
    def _magyc_next_kiosk_id(self, vals):
        area = self._magyc_area_code(vals)
        # Bestehende, manuell vergebene IDs überspringen.
        while True:
            number = self.env["ir.sequence"].next_by_code("magyc.kiosk.%s" % area)
            kiosk_id = "K-%s-%s" % (area, number)
            if not self.search_count([("kiosk_id", "=", kiosk_id)]):
                return kiosk_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("kundentyp") == "kiosk" and not vals.get("kiosk_id"):
                vals["kiosk_id"] = self._magyc_next_kiosk_id(vals)
        return super().create(vals_list)

    @api.constrains("kiosk_id", "kundentyp")
    def _check_kiosk_id_unique(self):
        for partner in self.filtered(lambda p: p.kundentyp == "kiosk" and p.kiosk_id):
            twin = self.search([
                ("id", "!=", partner.id),
                ("kiosk_id", "=", partner.kiosk_id),
            ], limit=1)
            if twin:
                raise ValidationError("Die Kiosk-ID %s ist bereits vergeben." % partner.kiosk_id)

    # ------------------------------------------------------------ Pipeline
    def action_set_status(self, status):
        for partner in self:
            partner.kiosk_status = status
            if status == "erstbestueckung_geplant":
                partner._magyc_create_first_fill()
        return True

    def action_mark_contract_received(self):
        return self.action_set_status("vertrag_eingegangen")

    def action_plan_first_fill(self):
        return self.action_set_status("erstbestueckung_geplant")

    def action_activate(self):
        return self.action_set_status("aktiv")

    def _magyc_create_first_fill(self):
        """Erstbestückung als Lieferauftrag anlegen, 8 Trays (4 + 4)."""
        company = self.company_id or self.env.company
        picking = self.env["stock.picking"]
        for partner in self:
            if picking.search_count([
                ("partner_id", "=", partner.id),
                ("magyc_is_first_fill", "=", True),
                ("state", "not in", ("done", "cancel")),
            ]):
                continue
            trays = company.magyc_first_fill_trays_per_product or 4
            lines = [(product, trays * 24) for product in company._magyc_drink_products()]
            partner._magyc_deliver(
                lines, "Erstbestückung %s" % (partner.kiosk_id or partner.name),
                first_fill=True)
        return True

    def action_create_refill(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Nachschub anfordern",
            "res_model": "magyc.delivery.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_partner_id": self.id, "default_mode": "refill"},
        }

    def action_open_count(self):
        """Mobile Bestandsaufnahme: Abverkaufsmeldung mit Positionen je Sorte."""
        self.ensure_one()
        if not self.commission_location_id:
            raise UserError("Für diesen Kiosk existiert kein Kommissionslager.")
        today = fields.Date.context_today(self)
        record = self.env["magyc.abverkauf"].create({
            "partner_id": self.id,
            "location_id": self.commission_location_id.id,
            "date_from": today.replace(day=1),
            "date_to": today,
        })
        for product in self.env.company._magyc_drink_products():
            self.env["magyc.abverkauf.line"].create({
                "abverkauf_id": record.id,
                "product_id": product.id,
                "price_unit": product.lst_price,
            })
        return {
            "type": "ir.actions.act_window",
            "name": "Bestand zählen",
            "res_model": "magyc.abverkauf",
            "res_id": record.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_mark_bonus_paid(self):
        for partner in self:
            partner.write({
                "magyc_bonus_state": "paid",
                "magyc_bonus_paid_on": fields.Date.context_today(partner),
            })
        return True

    def _magyc_deliver(self, lines, origin, vehicle_location=None, first_fill=False):
        self.ensure_one()
        return self.env["stock.picking"]._magyc_create_kiosk_delivery(
            self, lines, origin, vehicle_location=vehicle_location,
            first_fill=first_fill,
        )
