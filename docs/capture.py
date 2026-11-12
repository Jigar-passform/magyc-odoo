"""Erzeugt alle Handbuch-Screenshots mit roten Markierungen (Rahmen + Nummer).

Lauf:  cd docs && uv run --with playwright python capture.py
Voraussetzung: Odoo 20 auf :10031 mit DB magyc_dev, Chrome installiert.
Ergebnis: screenshots/de/*.png und screenshots/shots.json (Titel + Legende je Bild).
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

B = "http://localhost:10031"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "de")
os.makedirs(OUT, exist_ok=True)
PW = os.environ.get("ODOO_PW", "magyc2026")

OVERLAY = """(items) => {
  document.querySelectorAll('.mk-ov').forEach(e => e.remove());
  for (const it of items) {
    const d = document.createElement('div');
    d.className = 'mk-ov';
    d.style.cssText = `position:fixed;z-index:99999;pointer-events:none;border:4px solid #dc2626;border-radius:4px;box-shadow:0 0 0 2px #fff;left:${it.x-9}px;top:${it.y-9}px;width:${it.w+10}px;height:${it.h+10}px`;
    const n = document.createElement('div');
    n.textContent = it.n;
    n.style.cssText = 'position:absolute;left:-16px;top:-20px;width:26px;height:26px;border-radius:13px;background:#dc2626;color:#fff;font:bold 16px/26px Arial;text-align:center;box-shadow:0 0 0 2px #fff';
    d.appendChild(n);
    document.body.appendChild(d);
  }
}"""

SHOTS = []


def mark_and_shoot(pg, name, title, intro, marks, full=False):
    """marks: Liste (locator, nummer, legende). Fehlende Ziele werden gemeldet, nicht verschwiegen."""
    items, legend, missing = [], [], []
    first = True
    for loc, n, text in marks:
        try:
            l = loc.first
            if l.count() == 0:
                raise RuntimeError("nicht gefunden")
            if first:
                l.scroll_into_view_if_needed(timeout=4000)
                pg.wait_for_timeout(400)
                first = False
            bb = l.bounding_box()
            if not bb:
                raise RuntimeError("keine Box")
            items.append({"x": bb["x"], "y": bb["y"], "w": bb["width"], "h": bb["height"], "n": n})
            legend.append([n, text])
        except Exception as e:  # noqa: BLE001
            missing.append((n, text, str(e)[:60]))
    pg.evaluate(OVERLAY, items)
    pg.wait_for_timeout(300)
    path = os.path.join(OUT, name)
    clip = None
    if items and not full:
        vw, vh = 1440, 900
        x0 = min(i["x"] for i in items) - 300; y0 = min(i["y"] for i in items) - 170
        x1 = max(i["x"] + i["w"] for i in items) + 90; y1 = max(i["y"] + i["h"] for i in items) + 100
        cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
        w = max(x1 - x0, 900); h = max(y1 - y0, 560)
        x0 = max(0, min(cx - w / 2, vw - w)); y0 = max(0, min(cy - h / 2, vh - h))
        clip = {"x": x0, "y": y0, "width": min(w, vw), "height": min(h, vh - y0)}
    pg.screenshot(path=path, clip=clip) if clip else pg.screenshot(path=path)
    pg.evaluate("document.querySelectorAll('.mk-ov').forEach(e=>e.remove())")
    SHOTS.append({"file": name, "title": title, "intro": intro, "legend": legend})
    print(("OK  " if not missing else "WARN"), name, os.path.getsize(path), "marks", len(items), missing or "")


def go(pg, url, ready=".o_main_navbar", extra=6500):
    pg.goto(B + url, wait_until="commit")
    pg.wait_for_selector(ready, timeout=60000)
    pg.wait_for_timeout(extra)


def login(pg):
    pg.goto(B + "/web/login?db=magyc_dev")
    pg.fill("input[name=login]", "admin")
    pg.fill("input[name=password]", PW)
    pg.click("button[type=submit]")
    pg.wait_for_timeout(3500)


def rpc(pg, model, method, args, kw=None):
    return pg.evaluate("""async ([m, method, args, kw]) => {
      const r = await fetch('/web/dataset/call_kw/'+m+'/'+method, {method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({jsonrpc:'2.0', method:'call', params:{model:m, method, args, kwargs: kw||{}}})});
      const j = await r.json(); return j.error ? {error: j.error.data.message} : j.result; }""", [model, method, args, kw or {}])


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="de-DE").new_page()
        login(pg)
        go(pg, "/odoo")
        f = lambda sel: pg.locator(sel)
        t = lambda txt: pg.get_by_text(txt, exact=False)
        btn = lambda txt: pg.locator(f"button:has-text('{txt}')")

        # 01 Startseite / Menü
        mark_and_shoot(pg, "de-01-start.png", "Startseite und Hauptmenü",
                       "Nach der Anmeldung erscheint die App-Uebersicht. Die App Kommission enthält alle MAGYC-Funktionen.",
                       [(f(".o_app, .o_home_menu .o_app").filter(has_text="Kommission"), 1, "App Kommission öffnen")])

        # 02 Firma: Konfiguration in drei MAGYC-Reitern
        go(pg, "/odoo/action-base.action_res_company_form/1", ".o_form_view", 7000)
        tab = lambda n: pg.locator(".o_notebook .nav-link", has_text=n)
        mark_and_shoot(pg, "de-02a-firma-datev.png", "Firma: DATEV-Nummern",
                       "Einstellungen > Unternehmen > Firma öffnen. Berater- und Mandantennummer für den DATEV-Export eintragen.",
                       [(f(".o_field_widget[name=l10n_de_datev_consultant_number]"), 1, "Beraternummer"),
                        (f(".o_field_widget[name=l10n_de_datev_client_number]"), 2, "Mandantennummer"),
                        (f(".o_field_widget[name=vat]"), 3, "USt-IdNr. der Firma")])
        tab("Pfand (MAGYC)").click(); pg.wait_for_timeout(800)
        mark_and_shoot(pg, "de-02b-firma-pfand.png", "Firma: Reiter Pfand (MAGYC)",
                       "Legt fest, welcher Artikel als Pfand dient und ob er automatisch an Rechnungen kommt.",
                       [(tab("Pfand (MAGYC)"), 1, "Reiter öffnen"),
                        (f(".o_field_widget[name=pfand_auto_add]"), 2, "Pfand automatisch ergänzen"),
                        (f(".o_field_widget[name=pfand_product_id]"), 3, "Pfandartikel wählen")])
        tab("Kommission (MAGYC)").click(); pg.wait_for_timeout(800)
        mark_and_shoot(pg, "de-02c-firma-kommission.png", "Firma: Reiter Kommission (MAGYC)",
                       "Lager für zurückgenommene, qualitätsgesperrte Ware.",
                       [(tab("Kommission (MAGYC)"), 1, "Reiter öffnen"),
                        (f(".o_field_widget[name=magyc_quality_location_id]"), 2, "Lagerort Qualitätssperre")])
        tab("Kiosk-Prozess (MAGYC)").click(); pg.wait_for_timeout(800)
        mark_and_shoot(pg, "de-02d-firma-kioskprozess.png", "Firma: Reiter Kiosk-Prozess (MAGYC)",
                       "Mengen und Beträge für Erstbestückung, Nachschub, Rücknahme, Provision und Startprämie.",
                       [(f(".o_field_widget[name=magyc_first_fill_trays]"), 1, "Erstbestückung Trays"),
                        (f(".o_field_widget[name=magyc_refill_min_trays]"), 2, "Mindestmenge Nachschub"),
                        (f(".o_field_widget[name=magyc_return_months]"), 3, "Rücknahme in Monaten"),
                        (f(".o_field_widget[name=magyc_akquisiteur_fee]"), 4, "Akquisiteur-Provision"),
                        (f(".o_field_widget[name=magyc_bonus_amount]"), 5, "Startprämie"),
                        (f(".o_field_widget[name=magyc_trays_per_pallet]"), 6, "Trays je Palette")])

        # 03 Kontakt / Kiosk (Reiter MAGYC)
        go(pg, "/odoo/action-base.action_partner_form/26", ".o_form_view", 6000)
        pg.locator(".o_notebook .nav-link", has_text="MAGYC").click(); pg.wait_for_timeout(1000)
        mark_and_shoot(pg, "de-03-kontakt-kiosk.png", "Kontakt: Reiter MAGYC (Kiosk-Stammdaten)",
                       "Jeder Kiosk ist ein Kontakt. Die Kiosk-Felder stehen im Reiter MAGYC.",
                       [(pg.locator(".o_notebook .nav-link", has_text="MAGYC"), 1, "Reiter MAGYC"),
                        (f(".o_field_widget[name=kiosk_id]"), 2, "Kiosk-ID"),
                        (f(".o_field_widget[name=kiosk_area]"), 3, "Gebiet (Kürzel)"),
                        (f(".o_field_widget[name=commission_location_id]"), 4, "Kommissionslager des Kiosks"),
                        (f(".o_field_widget[name=kiosk_status]"), 5, "Kiosk-Status")])

        # 04 Pfandartikel
        go(pg, "/odoo/action-sale.product_template_action/25", ".o_form_view", 6000)
        mark_and_shoot(pg, "de-04-artikel-pfand.png", "Artikel: Pfandartikel",
                       "Am Artikel wird Pfand gekennzeichnet. Nur so kommt der Pfandbetrag auf Rechnung und Gutschrift.",
                       [(f(".o_field_widget[name=is_pfand]"), 1, "Haken Pfandartikel"),
                        (f(".o_field_widget[name=list_price]"), 2, "Preis des Pfandartikels")])

        # 05 Kiosk-Postfach Liste + Formular
        go(pg, "/odoo/action-623", ".o_list_renderer", 4000)
        mark_and_shoot(pg, "de-05-postfach-liste.png", "Kiosk-Postfach: Eingänge",
                       "Neue Kiosk-Anfragen aus dem Webformular landen hier. Offene Anfragen zuerst bearbeiten.",
                       [(f(".o_main_navbar .o_menu_sections"), 1, "Menü Kommission"),
                        (f(".o_data_row").first, 2, "Anfrage öffnen"),
                        (btn("Neu"), 3, "Eingang manuell erfassen")])
        f(".o_data_row").first.click()
        pg.wait_for_timeout(3000)
        mark_and_shoot(pg, "de-06-postfach-formular.png", "Kiosk-Postfach: Anfrage bearbeiten",
                       "Aus der Anfrage entsteht per Knopfdruck der Kiosk samt Kontakt, oder die Anfrage wird abgelehnt.",
                       [(btn("Kiosk anlegen"), 1, "Kiosk aus Anfrage anlegen"),
                        (btn("Ablehnen"), 2, "Anfrage ablehnen"),
                        (f(".o_statusbar_status"), 3, "Status: Neu, Kiosk angelegt, Abgelehnt")])

        # 07/08 Abverkauf
        go(pg, "/odoo/action-586", ".o_list_renderer", 4000)
        mark_and_shoot(pg, "de-07-abverkauf-liste.png", "Abverkauf Kiosk: Liste",
                       "Eine Abverkaufsmeldung je Kiosk und Zeitraum. Die Menge kommt aus dem Bestand, nie aus Handeingabe.",
                       [(btn("Neu"), 1, "Neue Meldung"),
                        (f(".o_data_row").first, 2, "Meldung öffnen")])
        f(".o_data_row").first.click()
        pg.wait_for_timeout(3500)
        mark_and_shoot(pg, "de-08-abverkauf-formular.png", "Abverkauf Kiosk: Meldung prüfen und abrechnen",
                       "Zeitraum wählen, Zeilen prüfen, bestätigen. Beim Abrechnen entsteht die Rechnung mit Pfand und Steuer.",
                       [(f(".o_field_widget[name=partner_id], .o_field_widget[name=kiosk_id]"), 1, "Kiosk"),
                        (f(".o_statusbar_status"), 2, "Status der Meldung"),
                        (btn("Drucken"), 3, "Abverkaufsliste drucken"),
                        (btn("Zeile hinzufügen"), 4, "Zeile ergänzen")])

        # 09/10 Pfand
        go(pg, "/odoo/action-605", ".o_list_renderer", 4000)
        f(".o_data_row").first.click()
        pg.wait_for_timeout(3500)
        mark_and_shoot(pg, "de-09-pfand-ruecknahme.png", "Pfand-Rücknahme",
                       "Zurückgenommenes Leergut wird gezählt, daraus entsteht eine Pfand-Gutschrift an den Kiosk.",
                       [(f(".o_field_widget[name=partner_id]"), 1, "Kunde oder Kiosk"),
                        (f(".o_statusbar_status"), 2, "Status Entwurf, Abgerechnet"),
                        (btn("Zeile hinzufügen"), 3, "Leergut-Position erfassen")])

        # 11 Touren
        go(pg, "/odoo/action-609", ".o_list_renderer", 4000)
        f(".o_data_row").first.click()
        pg.wait_for_timeout(3500)
        mark_and_shoot(pg, "de-10-tour.png", "Tour planen und abschließen",
                       "Eine Tour bündelt offene Lieferungen eines Gebiets für einen Fahrer.",
                       [(btn("Offene Lieferungen übernehmen"), 1, "Offene Lieferungen automatisch übernehmen"),
                        (btn("Tour abschließen"), 2, "Tour abschließen"),
                        (f(".o_field_widget[name=driver_id], .o_field_widget[name=fahrer_id]"), 3, "Fahrer"),
                        (f(".o_notebook .nav-link").first, 4, "Reiter Stopps")])

        # 12 Belegtexte
        go(pg, "/odoo/action-587", ".o_list_renderer", 4000)
        mark_and_shoot(pg, "de-11-belegtexte.png", "Belegtexte",
                       "Einleitungs- und Schlusstext je Belegtyp. Änderung gilt für alle neuen Belege.",
                       [(f(".o_data_row").first, 1, "Belegtyp öffnen und Text anpassen"),
                        (btn("Neu"), 2, "Weiteren Belegtyp anlegen")])

        # 13 Nachschub (Wizard)
        go(pg, "/odoo/action-612", ".modal", 3000)
        kf = pg.locator(".modal .o_field_widget input").first
        kf.click(); pg.wait_for_timeout(1200)
        pg.locator(".modal ~ .o-autocomplete--dropdown-menu li, .o-autocomplete--dropdown-item, ul.o-autocomplete--dropdown-menu li").first.click(); pg.wait_for_timeout(1200)
        mark_and_shoot(pg, "de-12-nachschub-wizard.png", "Nachschub / Erstbestückung",
                       "Der Assistent erzeugt die Lieferung an den Kiosk nach den Mengen aus den Einstellungen.",
                       [(f(".modal .o_field_widget").first, 1, "Kiosk wählen"),
                        (f(".modal-footer button").first, 2, "Lieferung erzeugen")])

        # 14 Speditionstransfer (Wizard)
        go(pg, "/odoo/action-615", ".modal", 3000)
        mark_and_shoot(pg, "de-13-speditionstransfer.png", "Speditionstransfer",
                       "Palettenweise Lieferung an die Spedition mit Gebiet und Mengen.",
                       [(f(".modal .o_field_widget").first, 1, "Erstes Pflichtfeld"),
                        (f(".modal-footer button").first, 2, "Transfer anlegen")])

        # 15 Verkaufsauftrag und 16 Rechnung
        go(pg, "/odoo/action-sale.action_orders/24", ".o_form_view", 6000)
        mark_and_shoot(pg, "de-14-verkaufsauftrag.png", "Verkaufsauftrag mit Pfandzeile",
                       "Preis immer aus der Preisliste. Pfand wird als eigene Zeile angefügt.",
                       [(f(".o_statusbar_status"), 1, "Status"),
                        (f(".o_field_widget[name=pricelist_id]"), 2, "Preisliste"),
                        (f(".o_list_renderer tbody tr.o_data_row").first, 3, "Position")])
        go(pg, "/odoo/action-account.action_move_out_invoice_type/41", ".o_form_view", 6000)
        mark_and_shoot(pg, "de-15-rechnung.png", "Rechnung nach Abverkauf",
                       "Steuer und Pfand entstehen erst beim Abverkauf. Hier prüfen und buchen.",
                       [(f(".o_statusbar_status"), 1, "Status der Rechnung"),
                        (f(".o_field_widget[name=partner_id]"), 2, "Kunde"),
                        (btn("Print"), 3, "PDF mit Belegtexten drucken")])

        # 17 DATEV
        go(pg, "/odoo/action-622", ".o_list_renderer, .o_form_view", 5000)
        btn("Neu").first.click(); pg.wait_for_timeout(3000)
        mark_and_shoot(pg, "de-16-datev-export.png", "DATEV-Export (DTVF)",
                       "Geschäftsjahr und Perioden wählen, Journale festlegen, dann Generate.",
                       [(f(".o_field_widget[name=fiscalyear_id]"), 1, "Geschäftsjahr"),
                        (f(".o_field_widget[name=period_ids]"), 2, "Perioden"),
                        (f(".o_field_widget[name=journal_ids]"), 3, "Journale"),
                        (btn("Generate"), 4, "Export erzeugen")])
        b.close()
    json.dump(SHOTS, open(os.path.join(HERE, "screenshots", "shots.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("fertig", len(SHOTS))


if __name__ == "__main__":
    sys.exit(main())
