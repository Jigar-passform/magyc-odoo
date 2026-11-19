from odoo import api, fields, models

ZONE_QUARANTINE = "quarantine"


class MagycOpsWarehouse(models.AbstractModel):
    _inherit = "magyc.ops"

    @api.model
    def _cron_expired_to_quarantine(self):
        """Abgelaufene Chargen aus dem Allgemeinlager in die Quarantäne."""
        company = self.env.company
        quarantine = self.env["stock.location"].search(
            [("magyc_zone", "=", ZONE_QUARANTINE), ("usage", "=", "internal")], limit=1)
        if not quarantine:
            return self.env["stock.picking"]
        quants = self.env["stock.quant"].search([
            ("quantity", ">", 0),
            ("lot_id.removal_date", "<=", fields.Datetime.now()),
            ("location_id.usage", "=", "internal"),
            ("location_id.magyc_zone", "in", ("general", "pick")),
        ])
        created = self.env["stock.picking"]
        by_location = {}
        for quant in quants:
            by_location.setdefault(quant.location_id, []).append(quant)
        for location, group in by_location.items():
            lines = [(q.product_id, q.quantity) for q in group]
            created |= self.env["stock.picking"]._magyc_transfer(
                location, quarantine, lines,
                "MHD-Sperre %s" % fields.Date.context_today(self))
        return created
