from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycPfandProvision(models.TransientModel):
    """Rückstellung fuer noch nicht zurueckgenommenes Pfand (TU Steuer, 13.11.2026).

    Bildung netto: 4000 Bestandsveränderung Pfandverbindlichkeiten an
    3071 Offene Pfandrücknahmen. Die Umsatzsteuer wird erst bei tatsaechlicher
    Rueckgabe gemindert, deshalb netto.
    """

    _name = "magyc.pfand.provision"
    _description = "Pfand-Rückstellung buchen"

    date = fields.Date(required=True, default=fields.Date.context_today)
    period_label = fields.Char(string="Periode", help="z. B. 11/2026")
    issued_cans = fields.Integer(string="In Verkehr gebracht (Dosen)")
    returned_cans = fields.Integer(string="Zurückgenommen (Dosen)")
    deposit_per_can = fields.Monetary(
        string="Pfand je Dose brutto", default=0.25, currency_field="currency_id",
    )
    tax_rate = fields.Float(string="USt-Satz %", default=19.0)
    currency_id = fields.Many2one("res.company", string="Währung",
                                  compute="_compute_currency")
    gross_open = fields.Monetary(compute="_compute_amounts", currency_field="currency_id")
    net_open = fields.Monetary(compute="_compute_amounts", currency_field="currency_id")
    account_liability_id = fields.Many2one(
        "account.account", string="Offene Pfandrücknahmen (3071 SKR04)", required=True,
        help="TU Treuhand: 3071 Offene Pfandrücknahmen. Kontonummer haengt am "
             "Kontenrahmen, deshalb keine feste Auswahl.",
    )
    account_change_id = fields.Many2one(
        "account.account", string="Bestandsveränderung Pfand (4000 SKR04)", required=True,
        help="TU Treuhand: 4000 Bestandsveränderung Pfandverbindlichkeiten. "
             "Saldo muss dem Konto 4401 entsprechen.",
    )
    journal_id = fields.Many2one(
        "account.journal", string="Journal", required=True,
        domain="[('type', '=', 'general')]",
    )

    @api.depends("issued_cans", "returned_cans", "deposit_per_can", "tax_rate")
    def _compute_amounts(self):
        for rec in self:
            open_cans = max((rec.issued_cans or 0) - (rec.returned_cans or 0), 0)
            rec.gross_open = open_cans * (rec.deposit_per_can or 0.0)
            rec.net_open = rec.gross_open / (1.0 + (rec.tax_rate or 0.0) / 100.0)

    @api.depends("date")
    def _compute_currency(self):
        for rec in self:
            rec.currency_id = self.env.company

    def action_book(self):
        self.ensure_one()
        if self.net_open <= 0:
            raise UserError("Keine offene Pfandrückstellung fuer diese Periode.")
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "date": self.date,
            "ref": "Pfandrückstellung %s" % (self.period_label or self.date),
            "line_ids": [
                (0, 0, {
                    "name": "Bestandsveränderung Pfandverbindlichkeiten %s" % (self.period_label or ""),
                    "account_id": self.account_change_id.id,
                    "debit": self.net_open,
                    "credit": 0.0,
                }),
                (0, 0, {
                    "name": "Offene Pfandrücknahmen %s" % (self.period_label or ""),
                    "account_id": self.account_liability_id.id,
                    "debit": 0.0,
                    "credit": self.net_open,
                }),
            ],
        })
        move.action_post()
        return {"type": "ir.actions.act_window", "res_model": "account.move",
                "res_id": move.id, "view_mode": "form", "target": "current"}
