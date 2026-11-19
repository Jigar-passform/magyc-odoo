from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _magyc_clear_customer_stock(self):
        """Verkaufte Kundenware aus dem Kundenlager ausbuchen (Ablauf Warenannahme).

        Nur die fakturierte Menge verlaesst das Kundenlager, nie der Restbestand.
        Kioske sind ausgenommen: ihre verkaufte Menge ist mit der bestaetigten
        Abverkaufsmeldung bereits ausgebucht, der Rest gehoert weiter MAGYC.
        """
        pfand = self.env.company.pfand_product_id
        for move in self.filtered(lambda m: m.move_type == "out_invoice" and m.state == "posted"):
            partner = move.partner_id
            location = partner.commission_location_id
            if not location or partner.kundentyp == "kiosk":
                continue
            wanted = {}
            for line in move.invoice_line_ids:
                product = line.product_id
                if not product or product == pfand or product.type != "consu":
                    continue
                wanted[product] = wanted.get(product, 0.0) + line.quantity
            lines = []
            for product, qty in wanted.items():
                stock = sum(self.env["stock.quant"].search([
                    ("location_id", "=", location.id), ("product_id", "=", product.id),
                    ("quantity", ">", 0)]).mapped("quantity"))
                take = min(qty, stock)
                if take > 0:
                    lines.append((product, take))
            if lines:
                self.env["stock.picking"]._magyc_create_return(
                    partner, lines, "Rechnung %s" % move.name,
                    self.env.company._magyc_default_quality_location(),
                    source_location=location)
        return True

    def action_post(self):
        res = super().action_post()
        self._magyc_clear_customer_stock()
        return res
