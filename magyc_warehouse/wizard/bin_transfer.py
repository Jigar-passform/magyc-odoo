from odoo import api, fields, models
from odoo.exceptions import UserError


class MagycBinTransfer(models.TransientModel):
    """Umlagerung per Scanner: von Stellplatz, Menge, auf Stellplatz."""

    _name = "magyc.bin.transfer"
    _description = "Umlagerung Stellplatz"

    source_bin = fields.Char(string="Von Stellplatz", required=True)
    dest_bin = fields.Char(string="Auf Stellplatz", required=True)
    product_id = fields.Many2one("product.product", string="Artikel", required=True)
    lot_id = fields.Many2one("stock.lot", string="Charge")
    qty = fields.Float(string="Menge", required=True, default=1.0)

    def _find_location(self, code):
        loc = self.env["stock.location"].search([
            ("magyc_bin_code", "=", code), ("usage", "=", "internal"),
        ], limit=1)
        if not loc:
            raise UserError("Stellplatz %s ist nicht angelegt." % code)
        return loc

    def action_transfer(self):
        self.ensure_one()
        source = self._find_location(self.source_bin)
        dest = self._find_location(self.dest_bin)
        if source == dest:
            raise UserError("Quelle und Ziel sind identisch.")
        self.env["stock.picking"]._magyc_transfer(
            source, dest, [(self.product_id, self.qty)],
            "Umlagerung %s -> %s" % (self.source_bin, self.dest_bin))
        return {"type": "ir.actions.act_window_close"}
