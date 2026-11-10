from odoo import fields, models


class MagycTour(models.Model):
    _name = "magyc.tour"
    _description = "Tour"
    _order = "date desc, id desc"

    name = fields.Char(required=True, default="/")
    date = fields.Date(default=fields.Date.context_today, required=True)
    area = fields.Selection([("BER", "Berlin"), ("KOE", "Köln")], required=True)
    driver_id = fields.Many2one("res.users", string="Fahrer")
    vehicle_location_id = fields.Many2one("stock.location", string="Fahrzeuglager")
    picking_ids = fields.Many2many("stock.picking", string="Stopps")
    note = fields.Text()
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    stop_count = fields.Integer(compute="_compute_stop_count")

    def _compute_stop_count(self):
        for tour in self:
            tour.stop_count = len(tour.picking_ids)

    def action_fill_open_pickings(self):
        """Offene Kiosk-Lieferungen des Gebiets in die Tour übernehmen."""
        picking = self.env["stock.picking"]
        for tour in self:
            domain = [
                ("picking_type_code", "=", "outgoing"),
                ("state", "not in", ("done", "cancel")),
                ("partner_id.kundentyp", "=", "kiosk"),
            ]
            if tour.area:
                domain.append(("partner_id.gebiet", "ilike", dict(
                    self._fields["area"].selection)[tour.area]))
            stops = picking.search(domain)
            # Geografische Reihenfolge: Postleitzahl aufsteigend, dann ID.
            stops = stops.sorted(lambda p: (p.partner_id.zip or "99999", p.partner_id.name or ""))
            tour.picking_ids = [(6, 0, stops.ids)]
            for number, stop in enumerate(stops, start=1):
                stop.write({"magyc_tour_id": tour.id, "magyc_stop_sequence": number * 10})
        return True

    def action_mark_done(self):
        self.write({"picking_ids": [(6, 0, [])]})
        return True
