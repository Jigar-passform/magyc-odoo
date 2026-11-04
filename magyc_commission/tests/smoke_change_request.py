"""Smoke test for the MAGYC change request (Soll-Ablauf 01.11.2026)."""
from odoo.exceptions import UserError, ValidationError

results = []


def check(name, fn):
    try:
        fn()
        results.append((name, "PASS", ""))
    except AssertionError as exc:
        results.append((name, "FAIL", str(exc)))
    except Exception as exc:  # noqa: BLE001
        results.append((name, "FAIL", "%s: %s" % (type(exc).__name__, exc)))


env = env  # noqa: F821  (provided by odoo shell)

Kiosk = env["res.partner"]
kiosk = Kiosk.search([("kundentyp", "=", "kiosk")], limit=1)
company = env.company
pfand = company.pfand_product_id or env["product.product"].search([("is_pfand", "=", True)], limit=1)
drink = env["product.product"].search([("is_pfand", "=", False), ("type", "=", "consu")], limit=1)

assert kiosk, "no kiosk partner in the database"
assert pfand, "no deposit product"
assert drink, "no drink product"


def t_fields():
    for fname in ("kiosk_gln", "kiosk_iban", "contract_start", "contract_term_months",
                  "contract_signed", "kiosk_status", "contract_end"):
        assert fname in kiosk._fields, "missing partner field %s" % fname


def t_phone_required():
    try:
        Kiosk.create({"name": "Test Kiosk ohne Telefon", "kundentyp": "kiosk"})
    except ValidationError:
        return
    raise AssertionError("kiosk without phone was accepted")


def t_status():
    kiosk.write({"contract_signed": False})
    assert kiosk.kiosk_status == "interessent", kiosk.kiosk_status
    kiosk.write({"contract_signed": True, "contract_start": "2026-11-01"})
    assert kiosk.kiosk_status == "aktiv", kiosk.kiosk_status
    assert kiosk.contract_end, "contract end not computed"


def _new_abverkauf(expected, counted, sold, returned=0.0):
    location = kiosk.commission_location_id
    assert location, "kiosk has no consignment location"
    rec = env["magyc.abverkauf"].create({
        "partner_id": kiosk.id,
        "location_id": location.id,
        "date_from": "2026-11-01",
        "date_to": "2026-11-30",
    })
    env["magyc.abverkauf.line"].create({
        "abverkauf_id": rec.id,
        "product_id": drink.id,
        "qty_expected": expected,
        "qty_counted": counted,
        "qty_sold": sold,
        "qty_returned": returned,
        "price_unit": 0.75,
    })
    rec.invalidate_recordset()
    return rec


def t_shortfall():
    rec = _new_abverkauf(100, 90, 5)
    assert rec.qty_shortfall_total == 5, rec.qty_shortfall_total
    try:
        rec.action_confirm()
    except UserError:
        pass
    else:
        raise AssertionError("confirm allowed with open shortfall")
    rec.action_flag_shortfall()
    assert rec.state == "review", rec.state
    rec.action_clear_shortfall()
    assert rec.shortfall_cleared


def t_min_24():
    rec = _new_abverkauf(100, 90, 10)
    rec.action_confirm()
    try:
        rec.action_create_invoice()
    except UserError as exc:
        assert "24" in str(exc), str(exc)
        return
    raise AssertionError("invoice below 24 cans was allowed")


def t_invoice_deposit():
    rec = _new_abverkauf(100, 76, 24)
    rec.action_confirm()
    rec.action_create_invoice()
    assert rec.invoice_id, "no invoice created"
    deposit_lines = rec.invoice_id.invoice_line_ids.filtered(
        lambda l: l.product_id == pfand)
    assert deposit_lines, "deposit line missing on the sell-through invoice"
    assert deposit_lines.quantity == 24, deposit_lines.quantity
    return rec.invoice_id


def t_kiosk_pfand_block():
    ret = env["magyc.pfand.return"].create({"partner_id": kiosk.id})
    env["magyc.pfand.return.line"].create({
        "return_id": ret.id, "product_id": pfand.id, "qty": 24, "price_unit": 0.25})
    try:
        ret.action_create_credit_note()
    except UserError as exc:
        assert "Kiosk" in str(exc), str(exc)
        return
    raise AssertionError("kiosk deposit return was credited")


def t_delivery_block():
    overdue = env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": kiosk.id,
        "invoice_date": "2026-09-01",
        "invoice_date_due": "2026-09-15",
        "invoice_line_ids": [(0, 0, {
            "product_id": drink.id, "quantity": 24, "price_unit": 0.75,
            "tax_ids": [(6, 0, drink.taxes_id.ids)]})],
    })
    overdue.action_post()
    order = env["sale.order"].create({
        "partner_id": kiosk.id,
        "order_line": [(0, 0, {"product_id": drink.id, "product_uom_qty": 24})],
    })
    try:
        order.action_confirm()
    except UserError as exc:
        assert "Liefersperre" in str(exc), str(exc)
        return
    raise AssertionError("order confirmed despite overdue invoice")


def t_handover_report():
    picking = env["stock.picking"].search([("partner_id", "=", kiosk.id)], limit=1)
    assert picking, "no picking for the kiosk"
    picking.write({"magyc_first_fill_trays": 8, "magyc_signer_name": "Test SSM"})
    html, _ = env["ir.actions.report"]._render_qweb_html(
        "magyc_commission.report_uebergabeprotokoll", picking.ids)
    text = html.decode("utf-8")
    for needle in ("Erstbefüllung", "Fahrzeuglager", "Foto bei Übergabe", "Test SSM"):
        assert needle in text, "missing %s in handover report" % needle


for name, fn in [
    ("fields", t_fields),
    ("phone required", t_phone_required),
    ("kiosk status", t_status),
    ("shortfall review", t_shortfall),
    ("invoice from 24 cans", t_min_24),
    ("deposit on sell-through invoice", t_invoice_deposit),
    ("kiosk deposit return blocked", t_kiosk_pfand_block),
    ("delivery block", t_delivery_block),
    ("handover report", t_handover_report),
]:
    check(name, fn)

for name, status, detail in results:
    print("%-34s %s %s" % (name, status, detail))
print("SUMMARY", sum(1 for r in results if r[1] == "PASS"), "/", len(results))
env.cr.rollback()
