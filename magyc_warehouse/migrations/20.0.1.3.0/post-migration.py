from odoo import SUPERUSER_ID, api

from odoo.addons.magyc_warehouse.hooks import _route_deliveries_from_pick_zone


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouse = env["stock.warehouse"].search([], limit=1)
    pick = env["stock.location"].search([("magyc_zone", "=", "pick"), ("usage", "=", "view")], limit=1)
    if warehouse and pick:
        _route_deliveries_from_pick_zone(env, warehouse, pick)
