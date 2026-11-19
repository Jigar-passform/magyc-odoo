from datetime import timedelta
import base64

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.binary import BinaryBytes

# 1x1 PNG: die Image-Felder des Uebergabeprotokolls brauchen eine gueltige Datei.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==")

@tagged("post_install", "-at_install")
class TestMagycOps(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.lemon, cls.berry = cls.company._magyc_drink_products()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1)
        cls.stock = cls.warehouse.lot_stock_id
        cls.akquisiteur = cls.env["res.partner"].create({
            "name": "Primewave Media UG (Test)",
            "is_akquisiteur": True,
            "supplier_rank": 1,
        })
        cls.fee_product = cls.env["product.product"].create({
            "name": "Akquisiteur-Provision (Test)",
            "type": "service",
            "purchase_ok": True,
            "standard_price": 50.0,
        })
        cls.company.write({
            "magyc_akquisiteur_product_id": cls.fee_product.id,
            "magyc_finance_user_id": cls.env.user.id,
        })
        cls.lot_early = cls.env["stock.lot"].create({
            "name": "MAG-TEST-EARLY",
            "product_id": cls.lemon.id,
            "company_id": cls.company.id,
            "removal_date": fields.Datetime.now() + timedelta(days=30),
        })
        cls.lot_late = cls.env["stock.lot"].create({
            "name": "MAG-TEST-LATE",
            "product_id": cls.lemon.id,
            "company_id": cls.company.id,
            "removal_date": fields.Datetime.now() + timedelta(days=300),
        })
        cls.env["stock.quant"]._update_available_quantity(
            cls.lemon, cls.stock, 400.0, lot_id=cls.lot_early)
        cls.env["stock.quant"]._update_available_quantity(
            cls.lemon, cls.stock, 400.0, lot_id=cls.lot_late)
        cls.berry_lot = cls.env["stock.lot"].create({
            "name": "MAG-TEST-BERRY",
            "product_id": cls.berry.id,
            "company_id": cls.company.id,
            "removal_date": fields.Datetime.now() + timedelta(days=120),
        })
        cls.env["stock.quant"]._update_available_quantity(
            cls.berry, cls.stock, 400.0, lot_id=cls.berry_lot)
        cls.kiosk = cls.env["res.partner"].create({
            "name": "Kiosk Test Berlin",
            "kundentyp": "kiosk",
            "phone": "+49 30 1234567",
            "kiosk_area": "BER",
            "kiosk_iban": "DE02120300000000202051",
            "akquisiteur_id": cls.akquisiteur.id,
        })

    def _sign(self, picking):
        """Uebergabeprotokoll: Unterschrift und Kuehlschrankfoto sind Pflicht."""
        picking.write({
            "magyc_signer_name": "Kiosk Test",
            "magyc_signature": BinaryBytes(PNG),
            "magyc_photo": BinaryBytes(PNG),
        })

    # ------------------------------------------------------------------ tests
    def test_01_kiosk_id_from_sequence(self):
        self.assertRegex(self.kiosk.kiosk_id, r"^K-BER-\d{4}$")
        koeln = self.env["res.partner"].create({
            "name": "Kiosk Test Köln",
            "kundentyp": "kiosk",
            "phone": "+49 221 7654321",
            "kiosk_area": "KOE",
        })
        self.assertRegex(koeln.kiosk_id, r"^K-KOE-\d{4}$")

    def test_02_kiosk_id_unique(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({
                "name": "Doppelte ID",
                "kundentyp": "kiosk",
                "phone": "+49 30 999999",
                "kiosk_id": self.kiosk.kiosk_id,
            })

    def test_03_status_chain(self):
        self.assertEqual(self.kiosk.kiosk_status, "interessent")
        self.kiosk.action_mark_contract_received()
        self.assertEqual(self.kiosk.kiosk_status, "vertrag_eingegangen")
        self.kiosk.action_plan_first_fill()
        self.assertEqual(self.kiosk.kiosk_status, "erstbestueckung_geplant")
        picking = self.env["stock.picking"].search([
            ("partner_id", "=", self.kiosk.id), ("magyc_is_first_fill", "=", True)])
        self.assertTrue(picking, "Erstbestückung muss eine Lieferung anlegen")
        self.assertEqual(len(picking.move_ids), 2)
        self.assertEqual(sum(picking.move_ids.mapped("product_uom_qty")), 8 * 24)
        self.kiosk.action_activate()
        self.assertEqual(self.kiosk.kiosk_status, "aktiv")

    def test_04_contract_signed_sets_active(self):
        partner = self.env["res.partner"].create({
            "name": "Kiosk Vertrag", "kundentyp": "kiosk",
            "phone": "+49 30 5555555",
        })
        partner.contract_signed = True
        self.assertEqual(partner.kiosk_status, "aktiv")
        partner.contract_signed = False
        self.assertEqual(partner.kiosk_status, "interessent")

    def test_05_refill_minimum(self):
        wizard = self.env["magyc.delivery.wizard"].create({
            "partner_id": self.kiosk.id, "mode": "refill",
            "lemon_trays": 1, "berry_trays": 1,
        })
        with self.assertRaises(UserError):
            wizard.action_create()
        wizard.write({"lemon_trays": 2, "berry_trays": 2})
        action = wizard.action_create()
        picking = self.env["stock.picking"].browse(action["res_id"])
        # Stufe 2: die Lieferung steht bestaetigt, gebucht wird erst bei Unterschrift.
        self.assertNotEqual(picking.state, "done")
        self._sign(picking)
        picking.action_confirm_handover()
        self.assertEqual(picking.state, "done")
        self.assertEqual(sum(picking.move_ids.mapped("product_uom_qty")), 4 * 24)

    def test_06_fefo_uses_earliest_lot(self):
        abverkauf = self.env["magyc.abverkauf"].create({
            "partner_id": self.kiosk.id,
            "location_id": self.kiosk.commission_location_id.id,
            "date_from": fields.Date.context_today(self),
            "date_to": fields.Date.context_today(self),
        })
        self.env["stock.quant"]._update_available_quantity(
            self.lemon, self.kiosk.commission_location_id, 20.0, lot_id=self.lot_late)
        self.env["stock.quant"]._update_available_quantity(
            self.lemon, self.kiosk.commission_location_id, 20.0, lot_id=self.lot_early)
        allocation = abverkauf._magyc_allocate_lots(self.lemon, 10)
        self.assertEqual(allocation[0][0], self.lot_early)

    def test_07_handover_triggers_bonus(self):
        self.kiosk.action_plan_first_fill()
        picking = self.env["stock.picking"].search([
            ("partner_id", "=", self.kiosk.id), ("magyc_is_first_fill", "=", True)])
        self.assertTrue(picking.magyc_is_handover)
        with self.assertRaises(UserError):
            picking.action_confirm_handover()
        self._sign(picking)
        picking.action_confirm_handover()
        self.assertTrue(picking.magyc_handover_confirmed)
        self.assertEqual(self.kiosk.magyc_bonus_state, "open")
        activity = self.env["mail.activity"].search([
            ("res_model", "=", "res.partner"), ("res_id", "=", self.kiosk.id)])
        self.assertIn("Startprämie", activity.summary)

    def test_08_akquisiteur_monthly_bill(self):
        self.kiosk.action_plan_first_fill()
        picking = self.env["stock.picking"].search([
            ("partner_id", "=", self.kiosk.id), ("magyc_is_first_fill", "=", True)])
        self._sign(picking)
        picking.action_confirm_handover()
        last_month = fields.Date.subtract(fields.Date.context_today(self), months=1)
        picking.magyc_handover_date = last_month
        moves = self.env["magyc.ops"]._cron_akquisiteur_bills()
        self.assertTrue(moves, "Monatsrechnung muss entstehen")
        self.assertEqual(moves.move_type, "in_invoice")
        self.assertEqual(moves.invoice_line_ids.quantity, 1)
        self.assertEqual(moves.invoice_line_ids.price_unit, 50.0)
        self.assertEqual(moves.state, "draft")
        # zweiter Lauf legt keine Dublette an
        self.assertFalse(self.env["magyc.ops"]._cron_akquisiteur_bills())

    def test_09_six_month_return(self):
        self.kiosk.action_plan_first_fill()
        location = self.kiosk.commission_location_id
        self.env["stock.quant"]._update_available_quantity(
            self.berry, location, 30.0, lot_id=self.env["stock.lot"].create({
                "name": "MAG-TEST-OLD", "product_id": self.berry.id,
                "company_id": self.company.id,
                "removal_date": fields.Datetime.now() + timedelta(days=60),
            }))
        quant = self.env["stock.quant"].search([
            ("location_id", "=", location.id), ("product_id", "=", self.berry.id)], limit=1)
        self.env.cr.execute(
            "UPDATE stock_quant SET in_date = %s WHERE id = %s",
            (fields.Datetime.now() - timedelta(days=400), quant.id))
        quant.invalidate_recordset(["in_date"])
        pickings = self.env["magyc.ops"]._cron_six_month_returns()
        self.assertTrue(pickings)
        self.assertEqual(pickings.location_dest_id,
                         self.company._magyc_default_quality_location())
        self.assertEqual(pickings.state, "done")
        # idempotent
        self.assertFalse(self.env["magyc.ops"]._cron_six_month_returns())

    def test_10_transfer_between_warehouses(self):
        koeln = self.env["stock.warehouse"].create({
            "name": "MAGYC Köln (Test)", "code": "KOET",
            "company_id": self.company.id,
        })
        wizard = self.env["magyc.transfer.wizard"].create({
            "source_warehouse_id": self.warehouse.id,
            "dest_warehouse_id": koeln.id,
            "pallets": 1,
            "trays_per_pallet": 1,
        })
        action = wizard.action_create_transfer()
        picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.location_dest_id, koeln.lot_stock_id)
        self.assertEqual(sum(picking.move_ids.mapped("product_uom_qty")), 2 * 24)
        with self.assertRaises(UserError):
            self.env["magyc.transfer.wizard"].create({
                "source_warehouse_id": self.warehouse.id,
                "dest_warehouse_id": self.warehouse.id,
                "pallets": 1,
            }).action_create_transfer()

    def test_11_pfand_shop_price_gross(self):
        pfand = self.company.pfand_product_id
        self.assertTrue(pfand, "Pfand-Artikel muss konfiguriert sein")
        shop = self.env["res.partner"].create({
            "name": "Shop Kunde (Test)", "kundentyp": "online"})
        kiosk_order_partner = self.env["res.partner"].create({
            "name": "B2B Kunde (Test)", "kundentyp": "b2b"})
        self.company.write({"pfand_auto_add": True, "magyc_pfand_shop_price": 0.25})
        order = self.env["sale.order"].create({
            "partner_id": shop.id,
            "order_line": [(0, 0, {"product_id": self.lemon.id, "product_uom_qty": 24})],
        })
        order._magyc_sync_pfand_line()
        line = order.order_line.filtered(lambda l: l.product_id == pfand)
        self.assertTrue(line)
        rate = sum(pfand.taxes_id.mapped("amount")) / 100.0
        expected = 0.25 / (1.0 + rate) if rate else 0.25
        self.assertAlmostEqual(line.price_unit, expected, places=4)
        b2b = self.env["sale.order"].create({
            "partner_id": kiosk_order_partner.id,
            "order_line": [(0, 0, {"product_id": self.lemon.id, "product_uom_qty": 24})],
        })
        b2b._magyc_sync_pfand_line()
        self.assertAlmostEqual(
            b2b.order_line.filtered(lambda l: l.product_id == pfand).price_unit,
            pfand.lst_price, places=4)

    def test_12_tour_orders_stops_by_zip(self):
        near = self.env["res.partner"].create({
            "name": "Kiosk A", "kundentyp": "kiosk", "phone": "+49 30 1",
            "zip": "10115", "gebiet": "Berlin"})
        far = self.env["res.partner"].create({
            "name": "Kiosk B", "kundentyp": "kiosk", "phone": "+49 30 2",
            "zip": "14199", "gebiet": "Berlin"})
        picking_type = self.env["stock.picking.type"].with_context(
            active_test=False).search(
            [("code", "=", "outgoing"), ("warehouse_id", "=", self.warehouse.id)], limit=1)
        for number, partner in enumerate((far, near), start=1):
            self.env["stock.picking"].create({
                "picking_type_id": picking_type.id,
                "partner_id": partner.id,
                "location_id": self.stock.id,
                "location_dest_id": partner.commission_location_id.id,
                "origin": "Tour-Test %s" % number,
                "move_ids": [(0, 0, {
                    "product_id": self.lemon.id,
                    "product_uom_qty": 24,
                    "uom_id": self.lemon.uom_id.id,
                    "location_id": self.stock.id,
                    "location_dest_id": partner.commission_location_id.id,
                })],
            }).action_confirm()
        tour = self.env["magyc.tour"].create({
            "name": "Tour Test", "area": "BER", "date": fields.Date.context_today(self)})
        tour.action_fill_open_pickings()
        # Auf einer Datenbank mit echten Lieferungen stehen weitere Stopps in der Tour:
        # geprueft wird die Reihenfolge der beiden Teststopps, nicht ihre absolute Nummer.
        stops = tour.picking_ids.filtered(
            lambda p: p.partner_id in (near | far)).sorted("magyc_stop_sequence")
        self.assertEqual(len(stops), 2)
        self.assertEqual(stops[0].partner_id, near)
        self.assertEqual(stops[1].partner_id, far)
        self.assertLess(stops[0].magyc_stop_sequence, stops[1].magyc_stop_sequence)
        zips = [p.partner_id.zip or "99999" for p in tour.picking_ids.sorted("magyc_stop_sequence")]
        self.assertEqual(zips, sorted(zips))

    def test_14_kiosk_postfach(self):
        application = self.env["magyc.kiosk.application"].create({
            "name": "Neuer Kiosk Hauptstraße",
            "email_from": "kiosk@example.com",
            "phone": "+49 30 5554443",
            "street": "Hauptstraße 1",
            "zip": "10115",
            "city": "Berlin",
            "message": "Wir möchten MAGYC führen.",
        })
        self.assertEqual(application.state, "new")
        self.assertFalse(application.partner_id)
        action = application.action_create_kiosk()
        kiosk = self.env["res.partner"].browse(action["res_id"])
        self.assertEqual(kiosk.kundentyp, "kiosk")
        # Stufe 1 legt direkt den Lieferauftrag fuer die Erstbestueckung an.
        self.assertEqual(kiosk.kiosk_status, "erstbestueckung_geplant")
        self.assertEqual(kiosk.phone, "+49 30 5554443")
        self.assertEqual(application.partner_id, kiosk)
        self.assertEqual(application.state, "converted")
        # ohne Telefon kein Kiosk, sondern eine Aufgabe zum Pruefen
        ohne_nummer = self.env["magyc.kiosk.application"].create({
            "name": "Kiosk ohne Nummer"})
        ohne_nummer.action_create_kiosk()
        self.assertEqual(ohne_nummer.state, "check")
        self.assertFalse(ohne_nummer.partner_id)
        self.assertTrue(self.env.ref("magyc_ops.alias_magyc_kiosk"))

    def test_17_postfach_auto_intake(self):
        app = self.env["magyc.kiosk.application"].create({
            "name": "Kiosk Flixcheck Test",
            "email_from": "flixcheck-test@example.com",
            "phone": "+49 30 999888",
            "street": "Teststr. 1",
            "zip": "10115",
            "city": "Berlin",
            "iban": "DE02120300000000202051",
        })
        app._magyc_auto_process()
        self.assertEqual(app.state, "converted")
        kiosk = app.partner_id
        self.assertEqual(kiosk.kundentyp, "kiosk")
        self.assertEqual(kiosk.kiosk_iban, "DE02120300000000202051")
        self.assertEqual(kiosk.kiosk_status, "erstbestueckung_geplant")
        picking = self.env["stock.picking"].search([
            ("partner_id", "=", kiosk.id), ("magyc_is_first_fill", "=", True)])
        self.assertTrue(picking, "Erstbestueckung muss als Lieferauftrag entstehen")
        self.assertNotEqual(picking.state, "done", "Stufe 1 darf noch nicht buchen")

    def test_18_postfach_dublette(self):
        vals = {
            "name": "Kiosk Dublette",
            "email_from": "dublette@example.com",
            "phone": "+49 30 111222",
            "street": "Doppelweg 2",
            "zip": "10117",
            "city": "Berlin",
        }
        first = self.env["magyc.kiosk.application"].create(vals)
        first._magyc_auto_process()
        second = self.env["magyc.kiosk.application"].create(vals)
        second._magyc_auto_process()
        self.assertEqual(second.state, "check")
        self.assertEqual(second.duplicate_partner_id, first.partner_id)

    def test_13_scrap_tags_and_damage_approval(self):
        muster = self.env.ref("magyc_ops.scrap_tag_muster")
        schaden = self.env.ref("magyc_ops.scrap_tag_schaden")
        self.assertEqual(muster.name, "RAN/MUSTER")
        self.assertEqual(schaden.name, "RAN/SCHADEN")
        picking = self.kiosk._magyc_deliver([(self.lemon, 24)], "Scrap-Test")
        move = picking.move_ids[0]
        move.scrap_reason_tag_ids = [(6, 0, [schaden.id])]
        self.assertTrue(move._magyc_is_damage_loss())
        move.scrap_reason_tag_ids = [(6, 0, [muster.id])]
        self.assertFalse(move._magyc_is_damage_loss())
