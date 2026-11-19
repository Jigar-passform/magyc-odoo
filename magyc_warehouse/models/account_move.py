from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _magyc_clear_customer_stock(self):
        """Verkaufte Kundenware aus dem Kundenlager ausbuchen (Ablauf Warenannahme)."""
        for move in self.filtered(lambda m: m.move_type == "out_invoice" and m.state == "posted"):
            partner = move.partner_id
            location = partner.commission_location_id
            if not location:
                continue
            quants = self.env["stock.quant"].search([
                ("location_id", "=", location.id), ("quantity", ">", 0),
            ])
            if not quants:
                continue
            lines = {}
            for quant in quants:
                lines[quant.product_id] = lines.get(quant.product_id, 0.0) + quant.quantity
            self.env["stock.picking"]._magyc_create_return(
                partner, list(lines.items()),
                "Rechnung %s" % move.name, self.env.company._magyc_default_quality_location(),
                source_location=location)
        return True

    def action_post(self):
        res = super().action_post()
        self._magyc_clear_customer_stock()
        return res
