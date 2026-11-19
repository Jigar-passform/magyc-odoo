from odoo import api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def magyc_write_off_consumption(self, product, qty, location=None, reason=None):
        """Verbrauch abschreiben: Ware verlaesst das Lager ohne Wert."""
        consumption = self.env["stock.location"].search(
            [("magyc_zone", "=", "consumption"), ("usage", "=", "internal")], limit=1)
        if not consumption:
            raise UserError("Kein Verbrauchslager definiert.")
        source = location or self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1).lot_stock_id
        move = self.create({
            "product_id": product.id,
            "product_uom_qty": qty,
            "uom_id": product.uom_id.id,
            "location_id": source.id,
            "location_dest_id": consumption.id,
            "origin": reason or "Verbrauch %s" % product.display_name,
        })
        move._action_confirm()
        if product.tracking == "none":
            move.quantity = qty
        else:
            move.move_line_ids.unlink()
            for lot, part in self.env["stock.picking"]._magyc_lot_lines(product, source, qty):
                self.env["stock.move.line"].create({
                    "move_id": move.id, "product_id": product.id, "lot_id": lot.id,
                    "quantity": part, "location_id": source.id,
                    "location_dest_id": consumption.id,
                })
        move.picked = True
        move._action_done()
        return move
