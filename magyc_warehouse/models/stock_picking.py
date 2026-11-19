from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    magyc_tray_count = fields.Integer(string="Verpackte Trays")
    magyc_pick_from_zone = fields.Boolean(
        string="Aus Pickzone", copy=False,
        help="Ware wird aus der Pickzone kommissioniert.",
    )

    def action_magyc_open_receipt(self):
        self.ensure_one()
        if self.picking_type_code != "incoming" or not self.origin:
            return False
        po = self.env["purchase.order"].search([("name", "=", self.origin)], limit=1)
        if not po:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": "Wareneingang buchen",
            "res_model": "magyc.receipt.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_picking_id": self.id, "default_purchase_id": po.id},
        }

    def button_validate(self):
        """Tray-Bestaetigung gegen die bewegte Menge pruefen."""
        for picking in self:
            if picking.picking_type_code != "outgoing" or not picking.magyc_tray_count:
                continue
            cans = sum(picking.move_ids.mapped("product_uom_qty"))
            trays_per = picking.company_id.magyc_first_fill_trays_per_product or 4
            expected = picking.magyc_tray_count * 24
            if abs(cans - expected) > 0.01:
                raise UserError(
                    "Tray-Bestaetigung passt nicht zur Menge: %s Trays sind %s Dosen, "
                    "bewegt werden %s. Bitte Trays oder Menge korrigieren."
                    % (picking.magyc_tray_count, expected, cans)
                )
        return super().button_validate()
