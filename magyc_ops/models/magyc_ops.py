from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycOps(models.AbstractModel):
    _name = "magyc.ops"
    _description = "MAGYC Abläufe (Cron)"

    # ------------------------------------------------- Akquisiteur-Abrechnung
    @api.model
    def _cron_akquisiteur_bills(self):
        """Monatsrechnung je Akquisiteur über die im Vormonat übergebenen Kioske."""
        today = fields.Date.context_today(self)
        first_this_month = today.replace(day=1)
        period_end = fields.Date.subtract(first_this_month, days=1)
        period_start = period_end.replace(day=1)
        label = period_start.strftime("%m/%Y")

        pickings = self.env["stock.picking"].search([
            ("magyc_handover_confirmed", "=", True),
            ("magyc_handover_date", ">=", period_start),
            ("magyc_handover_date", "<=", period_end),
            ("partner_id.akquisiteur_id", "!=", False),
        ])
        by_partner = {}
        for picking in pickings:
            kiosk = picking.partner_id
            by_partner.setdefault(kiosk.akquisiteur_id, []).append(kiosk)

        created = self.env["account.move"]
        for akquisiteur, kiosks in by_partner.items():
            company = akquisiteur.company_id or self.env.company
            product = company.magyc_akquisiteur_product_id
            if not product:
                continue
            origin = "Akquisiteur %s" % label
            if self.env["account.move"].search_count([
                ("partner_id", "=", akquisiteur.id),
                ("move_type", "=", "in_invoice"),
                ("invoice_origin", "=", origin),
            ]):
                continue
            fee = akquisiteur.magyc_akquisiteur_fee or company.magyc_akquisiteur_fee
            seen = []
            for kiosk in kiosks:
                if kiosk not in seen:
                    seen.append(kiosk)
            move = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": akquisiteur.id,
                "invoice_date": period_end,
                "invoice_origin": origin,
                "ref": "Provision %s Kioske %s" % (len(seen), label),
                "invoice_line_ids": [(0, 0, {
                    "product_id": product.id,
                    "name": "%s %s" % (kiosk.kiosk_id or kiosk.name, label),
                    "quantity": 1,
                    "price_unit": kiosk.magyc_akquisiteur_fee or fee,
                    "tax_ids": [(6, 0, product.supplier_taxes_id.ids)],
                }) for kiosk in seen],
            })
            created |= move
        return created

    # -------------------------------------------------- 6-Monats-Rücknahme
    @api.model
    def _cron_six_month_returns(self):
        """Unverkaufte Ware nach Ablauf der Frist in die Qualitätssperre zurücknehmen."""
        company = self.env.company
        months = company.magyc_return_months or 6
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), months=months)
        quality = company._magyc_default_quality_location()
        created = self.env["stock.picking"]
        kiosks = self.env["res.partner"].search([
            ("kundentyp", "=", "kiosk"),
            ("commission_location_id", "!=", False),
        ])
        for kiosk in kiosks:
            quants = self.env["stock.quant"].search([
                ("location_id", "=", kiosk.commission_location_id.id),
                ("quantity", ">", 0),
                ("in_date", "<=", cutoff),
            ])
            if not quants:
                continue
            origin = "6M-Rücknahme %s" % (kiosk.kiosk_id or kiosk.name)
            if self.env["stock.picking"].search_count([
                ("origin", "=", origin), ("state", "not in", ("cancel",)),
            ]):
                continue
            lines = {}
            for quant in quants:
                lines[quant.product_id] = lines.get(quant.product_id, 0.0) + quant.quantity
            created |= self.env["stock.picking"]._magyc_create_return(
                kiosk, list(lines.items()), origin, quality)
        return created
