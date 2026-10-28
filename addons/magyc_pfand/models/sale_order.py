from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _magyc_pfand_qty(self):
        """Sum of deposit-bearing units per deposit product."""
        self.ensure_one()
        company = self.company_id
        if not (company.pfand_auto_add and company.pfand_product_id):
            return 0.0
        pfand = company.pfand_product_id
        qty = 0.0
        for line in self.order_line:
            if line.product_id == pfand or line.display_type:
                continue
            if line.product_id.is_pfand:
                continue
            qty += line.product_uom_qty
        return qty

    def _magyc_sync_pfand_line(self):
        self.ensure_one()
        company = self.company_id
        if not (company.pfand_auto_add and company.pfand_product_id):
            return
        pfand = company.pfand_product_id
        qty = self._magyc_pfand_qty()
        pfand_lines = self.order_line.filtered(lambda l: l.product_id == pfand)
        if qty <= 0:
            pfand_lines.unlink()
            return
        vals = {
            "product_id": pfand.id,
            "product_uom_qty": qty,
            "price_unit": pfand.lst_price,
            "tax_ids": [(6, 0, pfand.taxes_id.ids)],
            "name": pfand.display_name,
        }
        if pfand_lines:
            pfand_lines[0].write(vals)
            (pfand_lines - pfand_lines[0]).unlink()
        else:
            self.write({"order_line": [(0, 0, vals)]})

    @api.onchange("order_line")
    def _onchange_order_line_pfand(self):
        for order in self:
            if order.state in ("draft", "sent"):
                order._magyc_sync_pfand_line()

    def action_confirm(self):
        for order in self:
            if order.state in ("draft", "sent"):
                order._magyc_sync_pfand_line()
        return super().action_confirm()
