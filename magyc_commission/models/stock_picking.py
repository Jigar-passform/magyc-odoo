from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    magyc_is_handover = fields.Boolean(
        string="Übergabeprotokoll",
        compute="_compute_magyc_is_handover", store=True,
        help="Kommissionslieferung an einen Kiosk, für die ein Protokoll gedruckt wird.",
    )
    magyc_first_fill_trays = fields.Integer(
        string="Erstbefüllung Trays", default=8,
        help="Anzahl Trays bei der Erstbefüllung, je 24 Dosen.",
    )
    magyc_vehicle_location_id = fields.Many2one(
        "stock.location", string="Fahrzeuglager",
        domain="[('usage', '=', 'internal')]",
        help="Lagerort des Fahrzeugs, aus dem die Ware ausgegeben wird.",
    )
    magyc_signer_name = fields.Char(string="Name bei Übergabe")
    magyc_photo = fields.Image(string="Foto Übergabe", max_width=1024, max_height=1024,
                               attachment=True)
    magyc_signature = fields.Image(string="Unterschrift", max_width=1024, max_height=1024,
                                   attachment=True)
    magyc_handover_note = fields.Text(string="Anmerkung Übergabe")

    @api.depends("partner_id.kundentyp", "picking_type_code")
    def _compute_magyc_is_handover(self):
        for picking in self:
            picking.magyc_is_handover = bool(
                picking.partner_id.kundentyp == "kiosk"
                and picking.picking_type_code == "outgoing"
            )
