from odoo import api, fields, models
from odoo.exceptions import ValidationError

ZONES = [
    ("general", "Allgemeinlager"),
    ("quarantine", "Quarantaenelager"),
    ("pick", "Pickzone"),
    ("customer", "Kundenlager"),
    ("consumption", "Verbrauchslager"),
]


class StockLocation(models.Model):
    _inherit = "stock.location"

    magyc_zone = fields.Selection(ZONES, string="Lagerzone", index=True)
    magyc_bin_code = fields.Char(
        string="Stellplatz", index=True,
        help="Regal-Fach-Hoehe, z. B. R08-01-20. Wird auf dem Etikett gescannt.",
    )
    magyc_blocked_zone = fields.Boolean(
        string="Gesperrte Zone", compute="_compute_blocked_zone", store=True,
    )

    @api.depends("magyc_zone", "usage")
    def _compute_blocked_zone(self):
        for loc in self:
            loc.magyc_blocked_zone = loc.magyc_zone == "quarantine"

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
