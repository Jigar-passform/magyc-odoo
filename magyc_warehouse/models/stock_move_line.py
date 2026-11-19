from odoo import api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _magyc_is_customer_delivery(self, picking):
        """Nur echte Kundenlieferungen pruefen, nicht Kiosk-Kommission.

        Kiosk-Lieferungen gehen an ein Kommissionslager, nicht an einen Kunden
        mit Pickzone. Reservierungen beim Bestaetigen duerfen nicht scheitern.
        """
        return (
            picking.picking_type_code == "outgoing"
            and picking.partner_id.kundentyp in (False, "b2b", "online")
            and picking.location_dest_id.magyc_zone != "customer"
        )

    def _magyc_check_pick_zone(self):
        """Kundenlieferungen nur aus Pickzone oder Kundenlager kommissionieren."""
        for line in self:
            picking = line.picking_id
            if not picking or not self._magyc_is_customer_delivery(picking):
                continue
            source = line.location_id
            if source.magyc_zone in ("pick", "customer"):
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
                    "Bitte ins Quarantänelager umlagern." % (lot.name, removal.date())
                )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._magyc_check_pick_zone()
        lines._magyc_check_expired()
        return lines
