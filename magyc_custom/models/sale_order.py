from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    magyc_delivery_block_override = fields.Boolean(
        string="Liefersperre ignorieren",
        help="Ausnahme: Aufträge dieses Kunden werden trotz überfälliger Rechnungen bestätigt.",
    )

    def _magyc_overdue_invoices(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        tolerance = self.env.company.magyc_delivery_block_days or 0
        limit = fields.Date.subtract(today, days=tolerance)
        return self.env["account.move"].search([
            ("partner_id", "=", self.id),
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "in", ("not_paid", "partial")),
            ("invoice_date_due", "!=", False),
            ("invoice_date_due", "<", limit),
        ])


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for order in self:
            company = order.company_id
            if not company.magyc_delivery_block:
                continue
            partner = order.partner_id
            if partner.magyc_delivery_block_override:
                continue
            overdue = partner._magyc_overdue_invoices()
            if overdue:
                raise UserError(
                    "Liefersperre: %s hat %s überfällige Rechnung(en), z. B. %s. "
                    "Bitte Zahlungseingang klären oder die Ausnahme am Kunden setzen."
                    % (partner.display_name, len(overdue), overdue[0].name)
                )
        return super().action_confirm()
