from odoo import api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _magyc_check_pick_zone(self):
        """Nur Pickzone oder Kundenlager als Quelle fuer Kundenlieferungen."""
        for line in self:
            picking = line.picking_id
            if picking.picking_type_code != "outgoing" or not picking.partner_id:
                continue
            source = line.location_id
            if source.magyc_zone in ("pick", "customer"):
                continue
            if picking.location_id.magyc_zone == "customer":
                continue
            raise UserError(
                "Lieferung nur aus der Pickzone. %s liegt in %s. "
                "Bitte zuerst umlagern." % (line.product_id.display_name, source.complete_name)
            )

    def _magyc_check_expired(self):
        for line in self:
            lot = line.lot_id
            removal = lot.removal_date if lot else False
            if not removal or line.location_dest_id.usage != "customer":
                continue
            if removal < fields.Datetime.now() and line.location_id.magyc_zone != "quarantine":
                raise UserError(
                    "Charge %s ist am %s abgelaufen und darf nicht ausgeliefert werden. "
                    "Bitte ins Quarantaenelager umlagern." % (lot.name, removal.date())
                )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._magyc_check_pick_zone()
        lines._magyc_check_expired()
        return lines
