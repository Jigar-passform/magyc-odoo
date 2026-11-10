from odoo import api, fields, models


class MagycAbverkauf(models.Model):
    _inherit = "magyc.abverkauf"

    placement_rows = fields.Integer(
        string="Kühlschrankreihen", default=0,
        help="Vom SSM beim Kiosk gezählte Reihen. Vorgabe: mindestens 2.",
    )
    placement_ok = fields.Boolean(
        string="Platzierung ok", compute="_compute_placement_ok", store=True,
    )
    placement_photo = fields.Image(
        string="Foto Platzierung", max_width=1024, max_height=1024, attachment=True,
    )

    @api.depends("placement_rows")
    def _compute_placement_ok(self):
        for rec in self:
            rec.placement_ok = rec.placement_rows >= 2

    def action_confirm(self):
        for rec in self:
            if rec.placement_rows and rec.placement_rows < 2:
                rec.message_post(body=(
                    "Platzierung unter 2 Reihen (%s). Bitte beim Kiosk nachplatzieren."
                    % rec.placement_rows))
        return super().action_confirm()
