"""Demo-/Testdaten für MAGYC auf einer Entwicklungsdatenbank.

Aufruf:
    odoo-bin shell -c odoo.conf -d <db> --no-http < tools/demo_seed.py

Legt an: Lager Köln (Platzhalteradresse), Akquisiteur, Kioske Berlin/Köln,
Erstbestückung + Nachschub, Abverkauf mit Rechnung, DATEV-Konfiguration und
einen DATEV-DTVF-Export unter /tmp (Pfad wird ausgegeben).
Idempotent: vorhandene Datensätze werden wiederverwendet.
"""
import os
import zipfile

from datetime import timedelta

from odoo import fields

company = env.company  # noqa: F821
Partner = env["res.partner"]
Picking = env["stock.picking"]

customer_sequence = env["ir.sequence"].search(
    [("code", "=", "datev.customer")], limit=1) or env["ir.sequence"].create({
        "name": "DATEV Debitorennummer", "code": "datev.customer",
        "prefix": "10", "padding": 4, "company_id": company.id})
supplier_sequence = env["ir.sequence"].search(
    [("code", "=", "datev.supplier")], limit=1) or env["ir.sequence"].create({
        "name": "DATEV Kreditorennummer", "code": "datev.supplier",
        "prefix": "70", "padding": 4, "company_id": company.id})

company.write({
    "datev_consultant_number": "9999999",
    "datev_client_number": "99999",
    "datev_account_code_length": 4,
    "datev_partner_numbering": "sequence",
    "datev_customer_sequence_id": customer_sequence.id,
    "datev_supplier_sequence_id": supplier_sequence.id,
})

# ---------------------------------------------------------------- Lager Köln
koeln = env["stock.warehouse"].search([("code", "=", "KOE")], limit=1)
if not koeln:
    koeln_partner = Partner.create({
        "name": "MAGYC Köln (Platzhalter)",
        "is_company": True,
        "street": "Platzhalterstraße 1 (Adresse offen)",
        "zip": "50999",
        "city": "Köln",
    })
    koeln = env["stock.warehouse"].create({
        "name": "MAGYC Köln (Platzhalter)",
        "code": "KOE",
        "company_id": company.id,
        "partner_id": koeln_partner.id,
    })
env["stock.quant"]._update_available_quantity(
    company._magyc_drink_products()[0], koeln.lot_stock_id, 500.0)

# Wareneingang sicherstellen, damit Erstbestückung buchbar ist
main_stock = env["stock.warehouse"].search(
    [("company_id", "=", company.id)], limit=1).lot_stock_id
for product in company._magyc_drink_products():
    available = sum(env["stock.quant"].search([
        ("product_id", "=", product.id),
        ("location_id", "child_of", main_stock.id),
    ]).mapped("quantity"))
    if available < 1500:
        lot = env["stock.lot"].create({
            "name": "DEMO-%s" % product.default_code,
            "product_id": product.id,
            "company_id": company.id,
            "removal_date": fields.Datetime.now() + timedelta(days=180),
        })
        env["stock.quant"]._update_available_quantity(
            product, main_stock, 1500 - available, lot_id=lot)

# ------------------------------------------------------------ Akquisiteur
akquisiteur = Partner.search([("name", "=", "Primewave Media UG")], limit=1)
if not akquisiteur:
    akquisiteur = Partner.create({
        "name": "Primewave Media UG",
        "is_akquisiteur": True,
        "supplier_rank": 1,
        "street": "Demo-Straße 1",
        "zip": "10115",
        "city": "Berlin",
    })

# ------------------------------------------------------------------- Kioske
kiosks = []
for index, (name, zip_code, area, street) in enumerate([
    ("Späti Alexanderplatz", "10178", "BER", "Alexanderstraße 3"),
    ("Kiosk Prenzlauer Berg", "10405", "BER", "Kastanienallee 12"),
    ("Trinkhalle Kreuzberg", "10961", "BER", "Gneisenaustraße 44"),
    ("Kiosk Rodenkirchen", "50996", "KOE", "Hauptstraße 8"),
], start=1):
    kiosk = Partner.search([("name", "=", name)], limit=1)
    if not kiosk:
        kiosk = Partner.create({
            "name": name,
            "kundentyp": "kiosk",
            "phone": "+49 30 100000%d" % index,
            "kiosk_area": area,
            "kiosk_iban": "DE02120300000000202051",
            "akquisiteur_id": akquisiteur.id,
            "street": street,
            "zip": zip_code,
            "city": "Berlin" if area == "BER" else "Köln",
        })
    kiosks.append(kiosk)

# --------------------------------------- Erstbestückung, Nachschub, Abverkauf
for kiosk in kiosks:
    if kiosk.kiosk_status == "interessent":
        kiosk.action_mark_contract_received()
        kiosk.action_plan_first_fill()
        kiosk.action_activate()
    picking = Picking.search([
        ("partner_id", "=", kiosk.id),
        ("magyc_is_first_fill", "=", True),
        ("state", "!=", "done"),
    ], limit=1)
    if picking:
        picking.action_assign()
        picking.move_ids.picked = True
        picking.with_context(skip_backorder=True, cancel_backorder=True).button_validate()

for kiosk in kiosks[:2]:
    kiosk.action_create_refill()

# ------------------------------------------------------------------ Rechnung
order = env["sale.order"].search([("partner_id", "=", kiosks[0].id)], limit=1)
if not order:
    product = company._magyc_drink_products()[0]
    order = env["sale.order"].create({
        "partner_id": kiosks[0].id,
        "order_line": [(0, 0, {"product_id": product.id, "product_uom_qty": 48})],
    })
    order.action_confirm()
invoice = order.invoice_ids[:1]
if not invoice:
    invoice = order._create_invoices()
invoice.action_post()

# --------------------------------------------------------------- DATEV-Export
date_range_type = env["date.range.type"].search([("name", "=", "Geschäftsjahr")], limit=1)
if not date_range_type:
    date_range_type = env["date.range.type"].create({"name": "Geschäftsjahr"})
year = fields.Date.today().year
date_range = env["date.range"].search(
    [("type_id", "=", date_range_type.id), ("date_start", "=", "%s-01-01" % year)], limit=1)
if not date_range:
    date_range = env["date.range"].create({
        "name": str(year),
        "type_id": date_range_type.id,
        "date_start": "%s-01-01" % year,
        "date_end": "%s-12-31" % year,
    })
export = env["datev_export_dtvf.export"].create({
    "fiscalyear_id": date_range.id,
    "period_ids": [(6, 0, date_range.ids)],
    "name": "MAGYC Demo %s" % year,
})
export.action_generate()
export.invalidate_recordset()

target = os.path.join(os.environ.get("TMPDIR") or os.environ.get("TEMP") or ".", "magyc_datev_demo.zip")
with open(target, "wb") as handle:
    handle.write(export.file_data.content)
with zipfile.ZipFile(target) as archive:
    names = archive.namelist()

print("KIOSKE", [(k.kiosk_id, k.name, k.kiosk_status) for k in kiosks])
print("LAGER", koeln.name, koeln.lot_stock_id.display_name)
print("EXPORT", target, export.state, len(names), names[:6])
env.cr.commit()
