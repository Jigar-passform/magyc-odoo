from odoo import api, fields, models
from odoo.exceptions import ValidationError

ZONES = [
    ("general", "Allgemeinlager"),
    ("quarantine", "Quarantänelager"),
    ("pick", "Pickzone"),
    ("customer", "Kundenlager"),
    ("consumption", "Verbrauchslager"),
]


class StockLocation(models.Model):
    _inherit = "stock.location"

    magyc_zone = fields.Selection(ZONES, string="Lagerzone", index=True)
    magyc_bin_code = fields.Char(
        string="Stellplatz", index=True,
        help="Regal-Fach-Höhe, z. B. R08-01-20. Wird auf dem Etikett gescannt.",
    )
    magyc_blocked_zone = fields.Boolean(
        string="Gesperrte Zone", compute="_compute_blocked_zone", store=True,
    )

    @api.depends("magyc_zone", "usage")
    def _compute_blocked_zone(self):
        for loc in self:
            loc.magyc_blocked_zone = loc.magyc_zone == "quarantine"

    @api.model_create_multi
    def create(self, vals_list):
        # Der Stellplatzcode ist zugleich der Barcode fuer die Barcode-App.
        for vals in vals_list:
            if vals.get("magyc_bin_code") and not vals.get("barcode"):
                vals["barcode"] = vals["magyc_bin_code"]
        locations = super().create(vals_list)
        locations.filtered(lambda l: l.magyc_bin_code and not l.barcode).write(
            {"barcode": False})
        for loc in locations.filtered("magyc_bin_code"):
            if not loc.barcode:
                loc.barcode = loc.magyc_bin_code
        return locations

    @api.constrains("magyc_bin_code")
    def _check_bin_code(self):
        for loc in self.filtered("magyc_bin_code"):
            twin = self.search_count([
                ("id", "!=", loc.id),
                ("magyc_bin_code", "=", loc.magyc_bin_code),
                ("company_id", "in", (loc.company_id.id, False)),
            ])
            if twin:
                raise ValidationError("Stellplatz %s ist doppelt vergeben." % loc.magyc_bin_code)

    def action_magyc_print_labels(self):
        return self.env.ref("magyc_warehouse.action_report_bin_label").report_action(
            self, data={})
