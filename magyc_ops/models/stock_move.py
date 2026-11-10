from odoo import fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    magyc_loss_approved_by = fields.Many2one(
        "res.users", string="Verlust freigegeben von", copy=False, readonly=True,
        help="Odoo 20 bucht Verluste als Stock Move. Freigabe wird beim Scrap gesetzt.")

    def _magyc_is_damage_loss(self):
        self.ensure_one()
        return any("SCHADEN" in (tag.name or "").upper()
                   for tag in self.scrap_reason_tag_ids)

    def _action_scrap(self):
        # Schäden (RAN/SCHADEN) nur mit Freigabe der Lagerleitung/Geschäftsführung.
        for move in self:
            if move._magyc_is_damage_loss() and not self.env.user.has_group(
                    "stock.group_stock_manager"):
                raise UserError(
                    "Schäden (RAN/SCHADEN) dürfen nur von der Lagerleitung bzw. der "
                    "Geschäftsführung freigegeben werden.")
        result = super()._action_scrap()
        for move in self:
            if move.is_scrap:
                move.magyc_loss_approved_by = self.env.user
        return result
