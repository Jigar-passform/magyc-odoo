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

    def _magyc_pfand_price(self, pfand):
        """Onlineshop: 0,25 EUR brutto. Kiosk/B2B: 0,25 EUR netto (Listenpreis)."""
        self.ensure_one()
        shop_price = self.company_id.magyc_pfand_shop_price or 0.0
        if self.partner_id.kundentyp != "online" or not shop_price:
            return pfand.lst_price
        rate = sum(pfand.taxes_id.mapped("amount")) / 100.0
        return shop_price / (1.0 + rate) if rate else shop_price

    def _magyc_sync_pfand_line(self):
        self.ensure_one()
        company = self.company_id
        if not (company.pfand_auto_add and company.pfand_product_id):
            return
        if self.partner_id.kundentyp == "kiosk":
            # Kioske zahlen Pfand mit der Abverkaufsrechnung, nicht auf dem Auftrag.
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
            "price_unit": self._magyc_pfand_price(pfand),
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
