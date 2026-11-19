
"""Handbuch-Screenshots direkt von Staging mit roten Markierungen. Beispieldaten = Szenario DEMO."""
import json, os, sys
from playwright.sync_api import sync_playwright

B = "https://staging-magyc.cloudpepper.site"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "stg"); os.makedirs(OUT, exist_ok=True)
PW = open(os.environ["DOCSHOT_PWFILE"]).read().strip()
IDS = json.load(open(os.environ["DOCSHOT_IDS"], encoding="utf-8"))
SHOTS = []

OVERLAY = """(items) => {
  document.querySelectorAll('.mk-ov').forEach(e => e.remove());
  for (const it of items) {
    const d = document.createElement('div'); d.className = 'mk-ov';
    d.style.cssText = `position:fixed;z-index:99999;pointer-events:none;border:4px solid #dc2626;border-radius:4px;box-shadow:0 0 0 2px #fff;left:${it.x-9}px;top:${it.y-9}px;width:${it.w+10}px;height:${it.h+10}px`;
    const n = document.createElement('div'); n.textContent = it.n;
    n.style.cssText = 'position:absolute;left:-16px;top:-20px;width:26px;height:26px;border-radius:13px;background:#dc2626;color:#fff;font:bold 16px/26px Arial;text-align:center;box-shadow:0 0 0 2px #fff';
    d.appendChild(n); document.body.appendChild(d);
  }
}"""

def shoot(pg, name, title, intro, marks, example="", full=False):
    items, legend, missing = [], [], []
    first = True
    for loc, n, text in marks:
        try:
            l = loc.first
            if l.count() == 0: raise RuntimeError("nicht gefunden")
            if first:
                l.scroll_into_view_if_needed(timeout=4000); pg.wait_for_timeout(400); first = False
            bb = l.bounding_box()
            if not bb: raise RuntimeError("keine Box")
            items.append({"x": bb["x"], "y": bb["y"], "w": bb["width"], "h": bb["height"], "n": n}); legend.append([n, text])
        except Exception as e:
            missing.append((n, text, str(e)[:50]))
    pg.evaluate(OVERLAY, items); pg.wait_for_timeout(300)
    path = os.path.join(OUT, name); clip = None
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
    SHOTS.append({"file": name, "title": title, "intro": intro, "example": example, "legend": legend})
    print(("OK  " if not missing else "WARN"), name, os.path.getsize(path), "marks", len(items), missing or "", flush=True)

def go(pg, url, ready=".o_main_navbar", extra=5000):
    pg.goto(B + url, wait_until="commit"); pg.wait_for_selector(ready, timeout=90000); pg.wait_for_timeout(extra)

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="de-DE")
        pg = ctx.new_page()
        pg.goto(B + "/web/login?db=staging-magyc.cloudpepper.site", wait_until="commit")
        pg.wait_for_selector("input[name=login]", timeout=90000)
        pg.fill("input[name=login]", "docshot"); pg.fill("input[name=password]", PW)
        pg.click("button[type=submit]"); pg.wait_for_timeout(5000)
        f = lambda s: pg.locator(s)
        btn = lambda t: pg.locator(f"button:has-text('{t}')")
        fld = lambda n: pg.locator(f".o_field_widget[name={n}]")
        A = IDS["actions"]; K = {k[1]: k[0] for k in IDS["kiosks"]}

        # 01 Wareneingang: Bestellung
        go(pg, "/odoo/action-purchase.purchase_rfq/%d" % IDS["po"][0][0], ".o_form_view")
        shoot(pg, "s01-bestellung.png", "Einkauf: Bestellung bei Eko-Vit", "Die Bestellung wird im Einkauf angelegt und bestätigt. Daraus entsteht der erwartete Wareneingang.",
              [(fld("partner_id"), 1, "Lieferant"), (f(".o_statusbar_status"), 2, "Status Bestellung"), (f(".o_list_renderer tbody tr.o_data_row"), 3, "Positionen")],
              "Beispiel: P00001, Eko-Vit, 2.880 Dosen Lemon und 1.440 Dosen Berry zu 0,27 EUR.")
        # 02 Wareneingang gebucht
        go(pg, "/odoo/action-stock.action_picking_tree_all/%d" % 42, ".o_form_view")
        shoot(pg, "s02-wareneingang.png", "Lager: Wareneingang gebucht", "Der Wareneingang zeigt Charge, MHD und Stellplatz je Position. Gebucht wird mit dem Assistenten.",
              [(f(".o_statusbar_status"), 1, "Status Erledigt"), (fld("origin"), 2, "Bestellung"), (btn("Wareneingang buchen"), 3, "Assistent Wareneingang")],
              "Beispiel: RAN/IN/00001, Lemon in R01-01-00 und R01-02-00, Berry in R02-01-00.")
        # 03 Bestand nach Stellplatz
        go(pg, "/odoo/action-%d" % A["Bestand nach Stellplatz"], ".o_list_renderer")
        shoot(pg, "s03-bestand-stellplatz.png", "Lager: Bestand nach Stellplatz", "Die Bestandsanzeige listet Artikel, Charge, MHD und Stellplatz. Filter und Gruppierung nach Zone sind möglich.",
              [(f(".o_searchview"), 1, "Suche und Filter"), (f(".o_list_renderer thead"), 2, "Spalten Charge, MHD, Stellplatz"), (f(".o_list_renderer tbody tr.o_data_row"), 3, "Bestand je Charge")],
              "Beispiel: DEMO-LEM-B (MHD 17.02.2027) liegt vor DEMO-LEM-A (MHD 16.08.2027) und wird zuerst genommen.")
        # 04 Umlagerung
        go(pg, "/odoo/action-%d" % A["Umlagerung"], ".o_form_view, .modal")
        shoot(pg, "s04-umlagerung.png", "Lager: Umlagerung von Fach zu Fach", "Von Stellplatz, auf Stellplatz, Artikel und Menge eintragen oder scannen.",
              [(fld("source_bin"), 1, "Von Stellplatz"), (fld("dest_bin"), 2, "Auf Stellplatz"), (fld("product_id"), 3, "Artikel"), (fld("qty"), 4, "Menge")],
              "Beispiel: 480 Dosen Lemon von R01-02-00 nach PICK-MAG-LEM-250.")
        # 05 Etiketten
        go(pg, "/odoo/action-%d" % A["Etiketten drucken"], ".o_form_view, .modal")
        shoot(pg, "s05-etiketten.png", "Lager: Stellplatz-Etiketten drucken", "Zone und Anzahl wählen oder einzelne Plätze auswählen. Jedes Etikett trägt Code und Strichcode.",
              [(fld("filter_zone"), 1, "Zone"), (fld("label_count"), 2, "Anzahl, 0 = alle"), (btn("Drucken"), 3, "Etiketten erzeugen")],
              "Beispiel: Zone Pickzone, Etiketten PICK-MAG-LEM-250 und PICK-MAG-BER-250.")
        # 06 Kiosk-Postfach Liste und Formular
        go(pg, "/odoo/action-%d" % A["Kiosk-Postfach"], ".o_list_renderer")
        shoot(pg, "s06-postfach-liste.png", "Kiosk-Postfach: Eingänge", "Jede Flixcheck-Mail erscheint als Eintrag. Status Kiosk angelegt oder Prüfen.",
              [(f(".o_list_renderer thead"), 1, "Spalten"), (f(".o_list_renderer tbody tr.o_data_row").first, 2, "Eintrag"), (f(".o_main_navbar .o_menu_sections"), 3, "Menü Kommission")],
              "Beispiel: drei Kioske angelegt, zwei Einträge stehen auf Prüfen (Dublette und fehlende Pflichtfelder).")
        go(pg, "/odoo/action-%d/%d" % (A["Kiosk-Postfach"], 18), ".o_form_view")
        shoot(pg, "s07-postfach-kiosk.png", "Kiosk-Postfach: automatisch angelegter Kiosk", "Aus der Mail entsteht Kiosk, Kommissionslager und Lieferauftrag.",
              [(f(".o_statusbar_status"), 1, "Status Kiosk angelegt"), (fld("partner_id"), 2, "Angelegter Kiosk"), (fld("iban"), 3, "IBAN aus der Mail")],
              "Beispiel: DEMO Späti Kreuzberg, Oranienstraße 12, K-BER-0024.")
        go(pg, "/odoo/action-%d/%d" % (A["Kiosk-Postfach"], 19), ".o_form_view")
        shoot(pg, "s08-postfach-dublette.png", "Kiosk-Postfach: Dublette erkannt", "Gleiche E-Mail wie ein bestehender Kiosk. Es entsteht kein zweiter Kiosk, sondern eine Prüfaufgabe.",
              [(f(".o_statusbar_status"), 1, "Status Prüfen"), (fld("duplicate_partner_id"), 2, "Dublette von")],
              "Beispiel: zweite Mail von kreuzberg@example.com.")
        # 09 Kontakt Kiosk
        go(pg, "/odoo/action-base.action_partner_form/%d" % K["K-BER-0024"], ".o_form_view")
        pg.locator(".o_notebook .nav-link", has_text="MAGYC").first.click(); pg.wait_for_timeout(900)
        shoot(pg, "s09-kontakt-kiosk.png", "Kontakt: Kiosk mit Status aktiv", "Der Kontakt zeigt Kiosk-ID, Status und Akquisiteur.",
              [(pg.locator(".o_notebook .nav-link", has_text="MAGYC").first, 1, "Reiter MAGYC"), (fld("kiosk_status"), 2, "Kiosk-Status"), (fld("kiosk_id"), 3, "Kiosk-ID"), (fld("akquisiteur_id"), 4, "Akquisiteur Primewave")],
              "Beispiel: K-BER-0024, Status aktiv, Startprämie ausgezahlt.")
        # 10 Erstbestückung Übergabeprotokoll
        go(pg, "/odoo/action-stock.action_picking_tree_all/%d" % 46, ".o_form_view")
        for t_ in ("Übergabe", "MAGYC"):
            tb = pg.locator(".o_notebook .nav-link", has_text=t_)
            if tb.count():
                tb.first.click(); pg.wait_for_timeout(900); break
        shoot(pg, "s10-uebergabe.png", "Lieferung: Übergabeprotokoll mit Unterschrift und Foto", "Erst Unterschrift und Kühlschrank-Foto buchen die Ware. Ohne beides bleibt die Lieferung offen.",
              [(f(".o_statusbar_status"), 1, "Status Erledigt"), (fld("magyc_signature"), 2, "Unterschrift Kiosk"), (fld("magyc_photo"), 3, "Foto Kühlschrank")],
              "Beispiel: RAN/OUT/00036, 192 Dosen in das Kommissionslager K-BER-0024.")
        go(pg, "/odoo/action-stock.action_picking_tree_all/%d" % 47, ".o_form_view")
        shoot(pg, "s11-erstbestueckung-offen.png", "Lieferung: Erstbestückung geplant, noch nicht gebucht", "Stufe 1 legt nur den Lieferauftrag an. Der Kiosk hat noch keine Ware.",
              [(f(".o_statusbar_status"), 1, "Status Bereit"), (fld("partner_id"), 2, "Kiosk"), (fld("origin"), 3, "Herkunft")],
              "Beispiel: RAN/OUT/00037 für K-BER-0025, wartet auf den Fahrer.")
        # 12 Abverkauf
        go(pg, "/odoo/action-%d/%d" % (A["Abverkaufsmeldungen"], 4), ".o_form_view")
        shoot(pg, "s12-abverkauf.png", "Abverkauf: Zählung und Rechnung", "Der SSM zählt. Abverkauf ist Soll minus gezählt. Der Preis kommt aus der Preisliste und ist nicht änderbar.",
              [(f(".o_statusbar_status"), 1, "Status Abgerechnet"), (f(".o_list_renderer tbody tr.o_data_row").first, 2, "Zeile mit Soll, gezählt, Abverkauf"), (fld("invoice_id"), 3, "Rechnung")],
              "Beispiel: 96 Soll, 60 gezählt = 36 Lemon, 26 Berry, je 0,75 EUR netto.")
        go(pg, "/odoo/action-%d/%d" % (A["Abverkaufsmeldungen"], 5), ".o_form_view")
        shoot(pg, "s13-abverkauf-differenz.png", "Abverkauf: Bestandsdifferenz geklärt", "Bei einer Differenz sperrt das System die Bestätigung, bis sie geklärt ist.",
              [(f(".o_statusbar_status"), 1, "Status"), (fld("shortfall_cleared"), 2, "Differenz geklärt"), (fld("qty_shortfall_total"), 3, "Differenz gesamt")],
              "Beispiel: Zählung mit 40 Dosen Differenz, erst nach Klärung bestätigt, unter 24 Dosen keine Rechnung.")
        # 14 Rechnung
        go(pg, "/odoo/action-account.action_move_out_invoice_type/5", ".o_form_view")
        shoot(pg, "s14-rechnung.png", "Rechnung nach Abverkauf mit Pfandzeile", "Getränk und Pfand stehen als getrennte Zeilen, beide mit 19 % USt.",
              [(f(".o_statusbar_status"), 1, "Status Gebucht"), (fld("partner_id"), 2, "Kiosk"), (f(".o_list_renderer tbody tr.o_data_row").last, 3, "Pfandzeile")],
              "Beispiel: INV/2026/00001, 36 Lemon + 26 Berry zu 0,75, Pfand 62 x 0,25, netto 62,00, brutto 73,78.")
        # 15 Pfand Rücknahme + Rückstellung
        go(pg, "/odoo/action-%d" % A["Pfand-Rücknahme"], ".o_list_renderer")
        shoot(pg, "s15-pfand-ruecknahme.png", "Pfand: Rücknahme B2B", "Zurückgenommenes Pfand erzeugt eine Gutschrift. Kioske sind ausgenommen.",
              [(f(".o_list_renderer thead"), 1, "Spalten"), (f(".o_list_renderer tbody tr.o_data_row").first, 2, "Rücknahme")],
              "Beispiel: DEMO Bistro B2B, 20 x 0,25, Gutschrift RINV/2026/00001 über 5,00 netto.")
        go(pg, "/odoo/action-account.action_account_moves_all", ".o_list_renderer, .o_view_nocontent", 6000)
        for fc in pg.locator(".o_searchview .o_facet_remove").all():
            try: fc.click(); pg.wait_for_timeout(400)
            except Exception: pass
        sb = pg.locator(".o_searchview_input").first
        sb.click(); sb.fill("Pfandrückstellung"); pg.wait_for_timeout(900)
        opt = pg.locator(".o_searchview_autocomplete li").first
        if opt.count(): opt.click()
        else: sb.press("Enter")
        pg.wait_for_timeout(3500)
        shoot(pg, "s16-pfand-rueckstellung.png", "Pfand: Rückstellung netto gebucht", "1.000 Dosen in Verkehr, 500 zurück: 125,00 brutto offen, Rückstellung 105,04 netto. Die Buchung entsteht im Assistenten Pfand-Rückstellung.",
              [(f(".o_searchview"), 1, "Suche nach Buchung Pfandrückstellung"), (f(".o_list_renderer tbody tr.o_data_row").nth(0), 2, "Soll Konto 4000"), (f(".o_list_renderer tbody tr.o_data_row").nth(1), 3, "Haben Konto 3071")],
              "Beispiel: Soll 4000 105,04 gegen Haben 3071 105,04, wie im Schreiben der Kanzlei.")
        # 17 Tour
        go(pg, "/odoo/action-%d/%d" % (A["Touren"], 4), ".o_form_view")
        shoot(pg, "s17-tour.png", "Tour: Stopps nach Postleitzahl", "Offene Kiosk-Lieferungen des Gebiets werden übernommen und nach PLZ sortiert.",
              [(fld("area"), 1, "Gebiet"), (fld("driver_id"), 2, "Fahrer"), (f(".o_list_renderer tbody tr.o_data_row").first, 3, "Stopp")],
              "Beispiel: Tour Berlin, 2 Stopps: 10999 Kreuzberg, 12045 Neukölln. Tour Köln: nur Ehrenfeld.")
        # 18 Speditionstransfer
        go(pg, "/odoo/action-%d" % A["Speditionstransfer"], ".o_form_view, .modal")
        shoot(pg, "s18-spedition.png", "Speditionstransfer Rangsdorf nach Köln", "Eine Palette sind 12 Trays je Sorte.",
              [(fld("source_warehouse_id"), 1, "Quelle"), (fld("dest_warehouse_id"), 2, "Ziel"), (fld("pallets"), 3, "Paletten")],
              "Beispiel: 1 Palette = 576 Dosen (12 Trays Lemon und 12 Trays Berry).")
        # 19 Nachschub
        go(pg, "/odoo/action-%d" % A["Lieferung an Kiosk"], ".o_form_view, .modal")
        shoot(pg, "s19-nachschub.png", "Nachschub anfordern", "Mindestens 4 Trays. Bei überfälliger Rechnung ist die Lieferung gesperrt.",
              [(fld("partner_id"), 1, "Kiosk"), (fld("mode"), 2, "Nachschub oder Erstbestückung"), (fld("lemon_trays"), 3, "Trays Lemon"), (fld("berry_trays"), 4, "Trays Berry")],
              "Beispiel: K-BER-0024, 2 + 2 Trays = 96 Dosen. 1 + 1 Tray wird abgelehnt, K-BER-0025 ist wegen offener Rechnung gesperrt.")
        b.close()
    json.dump(SHOTS, open(os.path.join(HERE, "screenshots", "shots_stg.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("fertig", len(SHOTS))

if __name__ == "__main__":
    sys.exit(main())
