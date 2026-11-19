from odoo import SUPERUSER_ID, api

from odoo.addons.magyc_warehouse.hooks import _route_deliveries_from_pick_zone, _set_shelf_life


def migrate(cr, version):
    """Haltbarkeit 270 Tage, sonst gilt jede Charge ohne MHD sofort als abgelaufen."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _set_shelf_life(env)
    warehouse = env["stock.warehouse"].search([], limit=1)
    pick = env["stock.location"].search([("magyc_zone", "=", "pick"), ("usage", "=", "view")], limit=1)
    if warehouse and pick:
        _route_deliveries_from_pick_zone(env, warehouse, pick)
