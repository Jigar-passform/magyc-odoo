from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycTransferWizard(models.TransientModel):
    _name = "magyc.transfer.wizard"
    _description = "Speditionstransfer zwischen Lägern"

    source_warehouse_id = fields.Many2one(
        "stock.warehouse", string="Quelle", required=True,
        default=lambda self: self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1))
    dest_warehouse_id = fields.Many2one(
        "stock.warehouse", string="Ziel", required=True)
    pallets = fields.Integer(string="Paletten", default=1, required=True)
    trays_per_pallet = fields.Integer(
        string="Trays je Palette",
        default=lambda self: self.env.company.magyc_trays_per_pallet or 12)
    note = fields.Char(string="Speditionsreferenz")

    def action_create_transfer(self):
        self.ensure_one()
        if self.source_warehouse_id == self.dest_warehouse_id:
            raise UserError("Quelle und Ziel müssen verschiedene Läger sein.")
        if self.pallets <= 0:
            raise UserError("Bitte mindestens eine Palette angeben.")
        products = self.env.company._magyc_drink_products()
        if not products:
            raise UserError("Keine MAGYC-Getränkeartikel hinterlegt.")
        cans = self.pallets * self.trays_per_pallet * 24
        picking = self.env["stock.picking"]._magyc_transfer(
            self.source_warehouse_id.lot_stock_id,
            self.dest_warehouse_id.lot_stock_id,
            [(product, cans) for product in products],
            self.note or "Spedition %s" % self.source_warehouse_id.name,
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Speditionstransfer",
            "res_model": "stock.picking",
            "res_id": picking.id,
            "view_mode": "form",
            "target": "current",
        }
