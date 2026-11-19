from odoo import fields, models


class MagycLabelWizard(models.TransientModel):
    """Anzahl Stellplatz-Etiketten drucken (Barcode = Stellplatz oder Kiosk-ID)."""

    _name = "magyc.label.wizard"
    _description = "Etiketten drucken"

    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    label_count = fields.Integer(string="Anzahl", default=1, required=True)
    label_kind = fields.Selection(
        [("bin", "Stellplatz"), ("product", "Artikel")],
        string="Etikett", default="bin", required=True,
    )
    start_number = fields.Integer(string="Ab Nummer", default=1)

    def action_print(self):
        self.ensure_one()
        return self.env.ref("magyc_warehouse.action_report_bin_label").report_action(
            self, data={"count": self.label_count, "kind": self.label_kind,
                        "start": self.start_number})
