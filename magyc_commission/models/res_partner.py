from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    commission_location_id = fields.Many2one(
        "stock.location",
        string="Kommissionslager",
        domain="[('usage', '=', 'internal')]",
        help="Lagerort beim Kiosk, an dem die Kommissionsware bis zum Abverkauf liegt.",
    )

    @api.model
    def _magyc_komm_parent(self):
        """Parent location for per-kiosk consignment stock."""
        parent = self.env["stock.location"].search(
            [("name", "=", "Kommissionsware Kunden"), ("usage", "=", "view")], limit=1)
        if parent:
            return parent
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "in", (self.env.company.id, False))], limit=1)
        return self.env["stock.location"].create({
            "name": "Kommissionsware Kunden",
            "usage": "view",
            "location_id": (warehouse.view_location_id.location_id or warehouse.view_location_id).id,
        })

    def _magyc_ensure_commission_location(self):
        for partner in self:
            if partner.kundentyp != "kiosk" or partner.commission_location_id:
                continue
            name = partner.kiosk_id or partner.name or ("Kiosk %s" % partner.id)
            existing = self.env["stock.location"].search(
                [("name", "=", name), ("usage", "=", "internal")], limit=1)
            partner.commission_location_id = existing or self.env["stock.location"].create({
                "name": name,
                "usage": "internal",
                "location_id": self._magyc_komm_parent().id,
            })

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._magyc_ensure_commission_location()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if "kundentyp" in vals or "kiosk_id" in vals:
            self._magyc_ensure_commission_location()
        return res
