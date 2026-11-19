from odoo import api, fields, models


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
