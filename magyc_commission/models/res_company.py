from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    magyc_quality_location_id = fields.Many2one(
        "stock.location", string="Qualitätssperre Rückgaben",
        domain="[('usage', '=', 'internal')]",
        help="Zielort für zurückgenommene Kommissionsware, z. B. RAN/QS.",
    )

    def _magyc_default_quality_location(self):
        """Qualitätssperre der Firma, wird beim ersten Bedarf angelegt."""

        self.ensure_one()
        if self.magyc_quality_location_id:
            return self.magyc_quality_location_id
        quality = self.env["stock.location"].search(
            [("usage", "=", "internal"), ("name", "ilike", "QS")], limit=1)
        if not quality:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.id)], limit=1)
            quality = self.env["stock.location"].create({
                "name": "QS Qualitätssperre",
                "usage": "internal",
                "location_id": warehouse.view_location_id.id,
            })
        self.magyc_quality_location_id = quality
        return quality
