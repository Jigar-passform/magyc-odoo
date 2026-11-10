"""Soll-Ablauf 01.11.2026 als ausführbarer Test (ersetzt smoke_change_request.py)."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSollAblauf(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        drinks = cls.company._magyc_drink_products()
        cls.drink = drinks[:1] or cls.env["product.product"].create({
            "name": "Lemon Zero (Test)", "type": "consu", "sale_ok": True,
        })
        cls.pfand = cls.company.pfand_product_id or cls.env["product.product"].search(
            [("is_pfand", "=", True)], limit=1)
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1)
        cls.stock = cls.warehouse.lot_stock_id
        cls.lot = cls.env["stock.lot"].create({
            "name": "SOLL-TEST-LOT",
            "product_id": cls.drink.id,
            "company_id": cls.company.id,
            "removal_date": fields.Datetime.now() + timedelta(days=120),
        })
        cls.env["stock.quant"]._update_available_quantity(
            cls.drink, cls.stock, 1000.0, lot_id=cls.lot)

    def _kiosk(self, **values):
        values.setdefault("name", "Kiosk Soll-Ablauf")
        values.setdefault("kundentyp", "kiosk")
        values.setdefault("phone", "+49 30 1234567")
        values.setdefault("kiosk_area", "BER")
        values.setdefault("kiosk_iban", "DE02120300000000202051")
        return self.env["res.partner"].create(values)

    def _abverkauf(self, kiosk, expected, counted, sold, returned=0.0):
        location = kiosk.commission_location_id
        self.assertTrue(location, "Kiosk hat kein Kommissionslager")
        rec = self.env["magyc.abverkauf"].create({
            "partner_id": kiosk.id,
            "location_id": location.id,
            "date_from": fields.Date.today().replace(day=1),
            "date_to": fields.Date.today(),
        })
        self.env["magyc.abverkauf.line"].create({
            "abverkauf_id": rec.id,
            "product_id": self.drink.id,
            "qty_expected": expected,
            "qty_counted": counted,
            "qty_sold": sold,
            "qty_returned": returned,
            "price_unit": 0.75,
        })
        rec.invalidate_recordset()
        return rec

    def test_01_fields(self):
        kiosk = self._kiosk()
        for fname in ("kiosk_gln", "kiosk_iban", "contract_start", "contract_term_months",
                      "contract_signed", "kiosk_status", "contract_end"):
            self.assertIn(fname, kiosk._fields)

    def test_02_phone_required(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Kiosk ohne Telefon", "kundentyp": "kiosk"})

    def test_03_status(self):
        kiosk = self._kiosk()
        kiosk.write({"contract_signed": False})
        self.assertEqual(kiosk.kiosk_status, "interessent")
        kiosk.write({"contract_signed": True, "contract_start": "2026-11-01"})
        self.assertEqual(kiosk.kiosk_status, "aktiv")
        self.assertTrue(kiosk.contract_end)

    def test_04_shortfall_review(self):
        rec = self._abverkauf(self._kiosk(), 100, 90, 5)
        self.assertEqual(rec.qty_shortfall_total, 5)
        with self.assertRaises(UserError):
            rec.action_confirm()
        rec.action_flag_shortfall()
        self.assertEqual(rec.state, "review")
        rec.action_clear_shortfall()
        self.assertTrue(rec.shortfall_cleared)

    def test_05_min_24_cans(self):
        rec = self._abverkauf(self._kiosk(), 100, 90, 10)
        rec.action_confirm()
        with self.assertRaises(UserError) as error:
            rec.action_create_invoice()
        self.assertIn("24", str(error.exception))

    def test_06_invoice_with_deposit(self):
        rec = self._abverkauf(self._kiosk(), 100, 76, 24)
        rec.action_confirm()
        rec.action_create_invoice()
        self.assertTrue(rec.invoice_id)
        deposits = rec.invoice_id.invoice_line_ids.filtered(
            lambda line: line.product_id == self.pfand)
        self.assertTrue(deposits, "Pfandzeile fehlt auf der Abverkaufsrechnung")
        self.assertEqual(deposits.quantity, 24)

    def test_07_kiosk_deposit_return_blocked(self):
        kiosk = self._kiosk()
        returns = self.env["magyc.pfand.return"].create({"partner_id": kiosk.id})
        self.env["magyc.pfand.return.line"].create({
            "return_id": returns.id, "product_id": self.pfand.id,
            "qty": 24, "price_unit": 0.25})
        with self.assertRaises(UserError) as error:
            returns.action_create_credit_note()
        self.assertIn("Kiosk", str(error.exception))

    def test_08_delivery_block(self):
        kiosk = self._kiosk()
        overdue = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": kiosk.id,
            "invoice_date": fields.Date.today() - timedelta(days=60),
            "invoice_date_due": fields.Date.today() - timedelta(days=45),
            "invoice_line_ids": [(0, 0, {
                "product_id": self.drink.id, "quantity": 24, "price_unit": 0.75,
                "tax_ids": [(6, 0, self.drink.taxes_id.ids)]})],
        })
        overdue.action_post()
        order = self.env["sale.order"].create({
            "partner_id": kiosk.id,
            "order_line": [(0, 0, {
                "product_id": self.drink.id, "product_uom_qty": 24})],
        })
        with self.assertRaises(UserError) as error:
            order.action_confirm()
        self.assertIn("Liefersperre", str(error.exception))

    def test_09_handover_report(self):
        kiosk = self._kiosk()
        picking = kiosk._magyc_deliver([(self.drink, 24)], "Übergabe-Test")
        picking.write({"magyc_first_fill_trays": 8, "magyc_signer_name": "Test SSM"})
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "magyc_commission.report_uebergabeprotokoll", picking.ids)
        text = html.decode("utf-8")
        for needle in ("Erstbefüllung", "Fahrzeuglager", "Foto bei Übergabe", "Test SSM"):
            self.assertIn(needle, text)

    def test_10_return_to_quality_hold(self):
        rec = self._abverkauf(self._kiosk(), 100, 76, 20, returned=4)
        rec.action_confirm()
        returns = self.env["stock.picking"].search(
            [("origin", "like", rec.name)]).filtered(
            lambda picking: "Rückgabe" in (picking.origin or ""))
        self.assertTrue(returns, "keine Rückgabe-Lieferung")
        quality = self.company._magyc_default_quality_location()
        self.assertTrue(quality, "kein Qualitätssperrlager")
        self.assertEqual(returns.location_dest_id, quality)

    def test_11_pick_list_report(self):
        kiosk = self._kiosk()
        picking = kiosk._magyc_deliver([(self.drink, 24)], "Lieferschein-Test")
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "magyc_commission.report_lieferschein", picking.ids)
        text = html.decode("utf-8")
        for needle in ("Lieferschein Kommission", "GTIN", "MHD", "Unterschrift"):
            self.assertIn(needle, text)

    def test_12_contract_report(self):
        kiosk = self._kiosk()
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "magyc_commission.report_kiosk_contract", kiosk.ids)
        text = html.decode("utf-8")
        for needle in ("Kommissions- und Liefervertrag", "Laufzeit", "IBAN"):
            self.assertIn(needle, text)

    def test_13_missing_count_cron(self):
        self.env["magyc.abverkauf"]._cron_missing_counts()
