from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycLabelWizard(models.TransientModel):
    """Stellplatz-Etiketten fuer eine Auswahl von Faechern drucken."""

    _name = "magyc.label.wizard"
    _description = "Etiketten drucken"

    picking_id = fields.Many2one("stock.picking", string="Wareneingang")
    filter_zone = fields.Selection(
        [("general", "Allgemeinlager"), ("pick", "Pickzone"), ("quarantine", "Quarantänelager")],
        string="Zone", default="general",
    )
    label_count = fields.Integer(string="Anzahl Etiketten", default=0,
                                 help="0 druckt alle Stellplaetze der Zone.")
    location_ids = fields.Many2many("stock.location", string="Stellplaetze")

    def action_print(self):
        self.ensure_one()
        locations = self.location_ids
        if not locations:
            locations = self.env["stock.location"].search([
                ("magyc_zone", "=", self.filter_zone), ("magyc_bin_code", "!=", False),
            ], limit=self.label_count or None)
        if not locations:
            raise UserError("Keine Stellplaetze fuer diese Auswahl.")
        return self.env.ref("magyc_warehouse.action_report_bin_label").report_action(locations)
