company = env.company
if not env["account.account"].search_count([("company_ids", "in", company.id)]):
    company.write({"country_id": env.ref("base.de").id})
    try:
        env["account.chart.template"].try_loading("de_skr04", company=company, install_demo=False)
    except TypeError:
        env["account.chart.template"].try_loading("de_skr04", company)
    env.cr.commit()
print("ACCOUNTS:", env["account.account"].search_count([("company_ids", "in", company.id)]))

partner = env["res.partner"].create({"name": "Test Kiosk", "kundentyp": "kiosk"})
wh = env["stock.warehouse"].search([], limit=1)
root = wh.view_location_id
loc = env["stock.location"].create({"name": "KOMM-TEST 1", "location_id": root.id, "usage": "internal"})
tax = env["account.tax"].search([("amount", "=", 19), ("type_tax_use", "=", "sale")], limit=1)
drink = env["product.product"].create({
    "name": "Test Drink 0,25 l", "is_storable": True, "list_price": 0.75,
    "taxes_id": [(6, 0, tax.ids)],
})
env["stock.quant"]._update_available_quantity(drink, loc, 100)

av = env["magyc.abverkauf"].create({
    "partner_id": partner.id, "location_id": loc.id,
    "date_from": "2026-09-01", "date_to": "2026-09-30",
    "line_ids": [(0, 0, {"product_id": drink.id, "qty_sold": 24, "price_unit": 0.75})],
})
av.action_confirm()
print("STATE:", av.state)
print("STOCK AT KIOSK AFTER SALE:", env["stock.quant"]._get_available_quantity(drink, loc))
av.action_create_invoice()
print("INVOICE:", av.invoice_id.name, "TOTAL:", av.invoice_id.amount_total, "STATE:", av.state)

pfand = env["product.product"].create({
    "name": "Test Pfand 0,25", "type": "service", "is_pfand": True, "list_price": 0.25,
    "taxes_id": [(6, 0, tax.ids)],
})
env.company.write({"pfand_auto_add": True, "pfand_product_id": pfand.id})
so = env["sale.order"].create({
    "partner_id": partner.id,
    "order_line": [(0, 0, {"product_id": drink.id, "product_uom_qty": 10, "price_unit": 0.75})],
})
so.action_confirm()
print("SO:", so.name, "LINES:", [(l.product_id.name, l.product_uom_qty) for l in so.order_line])

env.cr.rollback()
print("OK (rolled back)")
