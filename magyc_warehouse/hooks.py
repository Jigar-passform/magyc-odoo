"""Lagerstruktur anlegen: Zonen und die 885 Stellplätze aus der Belegungsliste."""
import logging

_logger = logging.getLogger(__name__)

ROWS = {  # Regalreihe: (Stellplätze je Hoehe, Hoehen)
    "R08": (42, ("00", "10", "20")),
    "R07": (39, ("00", "10", "20")),
    "R06": (39, ("00", "10", "20")),
    "R05": (42, ("00", "10", "20")),
    "R04": (42, ("00", "10", "20")),
    "R03": (42, ("00", "10", "20")),
    "R02": (27, ("00", "10", "20")),
    "R01": (27, ("00", "10", "20")),
}
# R03 ab Platz 28 nur bis Hoehe 10 (Belegungsliste, Stand 2026-11).
R03_TOP_TO = 27


def _route_deliveries_from_pick_zone(env, warehouse, pick):
    """Kundenauftraege kommissionieren aus der Pickzone, nicht aus dem Allgemeinlager.

    Kioskauslieferungen geben ihre Quelle selbst vor und sind davon nicht betroffen.
    """
    rules = env["stock.rule"].search([
        ("location_src_id", "=", warehouse.lot_stock_id.id),
        ("location_dest_id.usage", "=", "customer"),
        ("picking_type_id.code", "=", "outgoing"),
    ])
    rules.write({"location_src_id": pick.id})


def _bin_codes():
    for row, (places, levels) in ROWS.items():
        for level in levels:
            upper = places
            if row == "R03" and level == "20":
                upper = R03_TOP_TO
            for place in range(1, upper + 1):
                yield "%s-%02d-%s" % (row, place, level)


def post_init_hook(env):
    Location = env["stock.location"]
    company = env.company
    warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
    if not warehouse:
        _logger.warning("MAGYC Lager: kein Lager vorhanden")
        return
    view = warehouse.view_location_id

    def ensure(name, zone, parent, usage="internal"):
        loc = Location.search([("name", "=", name), ("usage", "=", usage)], limit=1)
        if not loc:
            loc = Location.create({
                "name": name, "usage": usage, "location_id": parent.id,
                "magyc_zone": zone, "company_id": company.id,
            })
        elif zone and not loc.magyc_zone:
            loc.magyc_zone = zone
        return loc

    ensure("Quarantänelager", "quarantine", view)
    pick = ensure("Pickzone", "pick", view, usage="view")
    ensure("Verbrauchslager", "consumption", view)
    general = Location.search([("name", "=", "Lagerbestand")], limit=1) or view
    if general.magyc_zone != "general":
        general.magyc_zone = "general"
    customer = Location.search([("name", "=", "Kommissionsware Kunden")], limit=1)
    if customer and customer.magyc_zone != "customer":
        customer.magyc_zone = "customer"

    # Pickzone: je Sorte ein eigenes Fach (Vorgabe: "jeder Artikel bekommt eine eigene Pickzone")
    for product in env["product.template"].search([("sale_ok", "=", True), ("is_pfand", "=", False)]):
        if product.magyc_pick_location_id:
            continue
        code = product.default_code or product.name[:12]
        bin_loc = Location.search([
            ("name", "=", "PICK-%s" % code), ("usage", "=", "internal"),
        ], limit=1)
        if not bin_loc:
            bin_loc = Location.create({
                "name": "PICK-%s" % code, "usage": "internal", "location_id": pick.id,
                "magyc_zone": "pick", "company_id": company.id,
                "magyc_bin_code": "PICK-%s" % code, "barcode": "PICK-%s" % code,
            })
        elif not bin_loc.magyc_bin_code:
            bin_loc.write({"magyc_bin_code": bin_loc.name, "barcode": bin_loc.barcode or bin_loc.name})
        product.magyc_pick_location_id = bin_loc

    # Putaway: Wareneingang legt die Sorte direkt in ihr Pickfach
    for product in env["product.template"].search([("sale_ok", "=", True), ("is_pfand", "=", False)]):
        if not product.magyc_pick_location_id:
            continue
        rule = env["stock.putaway.rule"].search([
            ("product_id", "=", product.product_variant_id.id),
            ("location_out_id", "=", product.magyc_pick_location_id.id),
        ], limit=1)
        if not rule:
            env["stock.putaway.rule"].create({
                "product_id": product.product_variant_id.id,
                "location_in_id": warehouse.lot_stock_id.id,
                "location_out_id": product.magyc_pick_location_id.id,
            })

    _route_deliveries_from_pick_zone(env, warehouse, pick)

    existing = set(Location.search([("magyc_bin_code", "!=", False)]).mapped("magyc_bin_code"))
    vals = [{
        "name": code, "usage": "internal", "location_id": general.id,
        "magyc_bin_code": code, "magyc_zone": "general", "company_id": company.id,
    } for code in _bin_codes() if code not in existing]
    if vals:
        Location.create(vals)
    _logger.info("MAGYC Lager: %s Stellplätze angelegt, %s vorhanden", len(vals), len(existing))
