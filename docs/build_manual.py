
"""Bedienhandbuch MAGYC: ein Kapitel je Prozess, Bilder von Staging, Beispiele aus den Testdaten."""
import json, os, re
from PIL import Image as PILImage
from reportlab.platypus import Image, KeepTogether, Spacer, Table, TableStyle, PageBreak, Paragraph
from reportlab.lib.units import mm
from reportlab.lib import colors
from build_docs import (para, steps, bullets, note, table, build, H1, H2, BODY, SMALL, PART, NAVY, LINE, HERE)
from reportlab.platypus import NextPageTemplate
from reportlab.lib.styles import ParagraphStyle

SH = {s["file"]: s for s in json.load(open(os.path.join(HERE, "screenshots", "shots_stg.json"), encoding="utf-8"))}
OUT = os.path.join(HERE, "screenshots", "stg")

def shot(s, name):
    sh = SH[name]
    path = os.path.join(OUT, name)
    w, h = PILImage.open(path).size
    width = 168 * mm; height = min(width * h / w, 84 * mm); width = height * w / h
    block = [Paragraph("<b>Bild: %s</b>" % sh["title"], H2), Image(path, width=width, height=height)]
    if sh["example"]:
        block.append(Paragraph("<i>%s</i>" % sh["example"].replace("&", "&amp;"), SMALL))
    rows = [[Paragraph("<b>%s</b>" % n, BODY), Paragraph(t, BODY)] for n, t in sh["legend"]]
    if rows:
        t = Table(rows, colWidths=[10 * mm, 158 * mm])
        t.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#dc2626")),
                               ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        block.append(t)
    s.append(KeepTogether(block)); s.append(Spacer(1, 8))

def ex(s, text):
    note("<b>Beispiel aus den Testdaten.</b> " + text, "info", s)

def manual():
    s = []
    para("<b>Bedienhandbuch</b>", s, ParagraphStyle("ct", parent=BODY, fontName="Helvetica-Bold", fontSize=12, textColor=NAVY, spaceAfter=10))
    para("Dieses Handbuch beschreibt jeden angefragten Prozess in der Reihenfolge, in der er im Betrieb vorkommt. "
         "Jedes Kapitel nennt Ziel, Menuepfad, Schritte, Regeln und eine Kontrolle. Alle Bilder stammen vom "
         "Staging-System. Rote Quadrate mit Nummer zeigen, wo geklickt oder eingetragen wird. Die Beispiele sind "
         "echte Datensaetze, die ein Pruefablauf mit 51 Schritten auf Staging angelegt hat und die dort einsehbar sind.", s)
    note("<b>Staging ist nicht Produktion.</b> Alle Namen mit DEMO am Anfang sind Testdaten. Die Kioske K-BER-0024, "
         "K-BER-0025 und K-KOE-0004 sind erfunden.", "warn", s)
    table(["Teil", "Kapitel", "Prozess"],
          [["A", "1 bis 3", "Wareneingang, Stellplaetze, Umlagerung und Etiketten"],
           ["B", "4 bis 6", "Kiosk-Postfach, Erstbestueckung, Uebergabeprotokoll, Startpraemie"],
           ["C", "7 bis 9", "Zaehlung und Abverkauf, Rechnung mit Pfand, Nachschub und Liefersperre"],
           ["D", "10 bis 12", "Pfand: Ruecknahme und Rueckstellung, Tour, Speditionstransfer"],
           ["E", "13", "Abrechnung Primewave und Ruecknahme nach sechs Monaten"],
           ["F", "14", "Pruefprotokoll: alle 51 Schritte mit Ergebnis"]],
          [14 * mm, 24 * mm, 130 * mm], s)
    s.append(NextPageTemplate("Body")); s.append(PageBreak())

    # ------------------------------------------------------------------ A
    s.append(Paragraph("Teil A. Lager", PART))
    para("1. Wareneingang buchen", s, H1)
    para("<b>Ziel.</b> Ware vom Lieferanten mit Charge, MHD und Stellplatz einbuchen.", s)
    para("<b>Wer.</b> Lagerleitung (Gruppe MAGYC Lager).", s)
    steps(["<b>Einkauf &gt; Bestellung</b>: Bestellung anlegen und <b>Bestaetigen</b>. Es entsteht ein Wareneingang.",
           "<b>Lager &gt; Wareneingang</b> oeffnen, <b>Wareneingang buchen</b> klicken.",
           "Je Position <b>Charge neu</b>, <b>MHD</b>, <b>Menge</b> und <b>Stellplatz</b> eintragen. Eine Sorte darf auf mehrere Zeilen mit verschiedenen Chargen und Faechern verteilt werden.",
           "Optional <b>Etiketten drucken</b> mit Anzahl. <b>Buchen</b>.",
           "Kontrolle: Status <b>Erledigt</b>, Menge je Stellplatz stimmt, Charge hat ein MHD."], s)
    shot(s, "s01-bestellung.png")
    shot(s, "s02-wareneingang.png")
    ex(s, "Bestellung P00001 bei Eko-Vit: 2.880 Dosen Lemon und 1.440 Dosen Berry. Gebucht als Lemon DEMO-LEM-A (MHD 16.08.2027) 1.440 in R01-01-00, "
          "Lemon DEMO-LEM-B (MHD 17.02.2027) 1.440 in R01-02-00 und Berry DEMO-BER-A (MHD 17.07.2027) 1.440 in R02-01-00.")
    note("<b>Regel.</b> Hat eine Charge kein MHD, vergibt das System 270 Tage ab Eingang. Ohne diese Voreinstellung galt jede neue Charge sofort als abgelaufen.", "info", s)

    para("2. Bestand nach Stellplatz und FEFO", s, H1)
    para("<b>Ziel.</b> Sehen, was wo liegt, nach Artikel, Charge und MHD.", s)
    steps(["<b>Lager &gt; Bestand nach Stellplatz</b>.",
           "Suche und Filter nutzen, zum Beispiel Zone Pickzone oder Artikel Lemon. Nach Charge oder MHD gruppieren.",
           "Kontrolle: Die Charge mit dem fruehesten MHD steht in der Auswahl zuerst."], s)
    shot(s, "s03-bestand-stellplatz.png")
    ex(s, "DEMO-LEM-B (MHD 17.02.2027) wird vor DEMO-LEM-A (MHD 16.08.2027) genommen. Beim Umlagern von 480 Dosen in die Pickzone war genau diese Charge im Pickplatz.")
    bullets(["<b>FEFO</b>: die Charge mit dem naechsten MHD geht zuerst raus (Kategorie Getraenke).",
             "<b>Pickzone</b>: Kundenauftraege werden nur aus der Pickzone kommissioniert. Das Lager Rangsdorf hat dafuer die Lieferregel auf die Pickzone gestellt.",
             "<b>Abgelaufene Ware</b> darf nicht an Kunden und nicht in ein Kiosklager. Ein taeglicher Lauf verschiebt sie in die Quarantaene.",
             "Beispiel: Charge DEMO-ABGELAUFEN (MHD 09.11.2026) mit 48 Dosen wurde vom Lauf in die Quarantaene gebucht."], s)

    para("3. Umlagerung, Etiketten und Verbrauch", s, H1)
    para("<b>3.1 Umlagerung von Fach zu Fach.</b>", s)
    steps(["<b>Lager &gt; Umlagerung</b>.",
           "<b>Von Stellplatz</b> und <b>Auf Stellplatz</b> als Code tippen oder scannen, <b>Artikel</b> und <b>Menge</b> waehlen.",
           "<b>Umlagern</b>. Der Vorgang bucht einen internen Transfer und erledigt ihn sofort.",
           "Kontrolle: Bestand beider Plaetze in <b>Bestand nach Stellplatz</b>."], s)
    shot(s, "s04-umlagerung.png")
    ex(s, "480 Dosen Lemon von R01-02-00 nach PICK-MAG-LEM-250 und 480 Dosen Berry von R02-01-00 nach PICK-MAG-BER-250. Gleiches Fach als Quelle und Ziel wird abgelehnt (Meldung: Quelle und Ziel sind identisch).")
    para("<b>3.2 Etiketten drucken.</b>", s)
    steps(["<b>Lager &gt; Etiketten drucken</b>.", "Zone waehlen, Anzahl eintragen (0 = alle) oder einzelne Plaetze waehlen.",
           "<b>Drucken</b>. Jedes Etikett zeigt den Code und einen Strichcode (Code128), der in der Lager-Barcode-App gescannt wird."], s)
    shot(s, "s05-etiketten.png")
    para("<b>3.3 Verbrauch abschreiben.</b> Material ohne Wert verlaesst das Lager ueber das Verbrauchslager. "
         "Das Verbrauchslager ist ein eigener Lagerort. Ein Abschreibungsvorgang bucht die Menge dorthin und waehlt die Charge nach FEFO.", s)
    ex(s, "6 Dosen Lemon wurden mit der Begruendung DEMO Klebeband/Bruch nach RAN/Verbrauchslager gebucht.")

    # ------------------------------------------------------------------ B
    s.append(Paragraph("Teil B. Kiosk gewinnen und beliefern", PART))
    para("4. Kiosk-Postfach: aus der Mail wird ein Kiosk", s, H1)
    para("<b>Ziel.</b> Flixcheck schickt nach jeder Unterschrift eine Mail an die Adresse kiosk@. Odoo legt daraus Kiosk, Kommissionslager und den Lieferauftrag fuer die Erstbestueckung an.", s)
    steps(["Die Mail trifft ein. Pflichtfelder: Telefon, Strasse, PLZ, Ort.",
           "<b>Kommission &gt; Kioskbetrieb &gt; Kiosk-Postfach</b> zeigt den Eingang.",
           "Sind alle Felder da und der Kiosk neu: Status <b>Kiosk angelegt</b>, Kiosk-Status <b>Erstbestueckung geplant</b>, ein Lieferauftrag mit 8 Trays (4 Lemon, 4 Berry).",
           "Fehlt etwas oder ist es eine Dublette: Status <b>Pruefen</b> und eine Aufgabe. Es wird kein zweiter Kiosk angelegt."], s)
    shot(s, "s06-postfach-liste.png")
    shot(s, "s07-postfach-kiosk.png")
    shot(s, "s08-postfach-dublette.png")
    ex(s, "Mail von Spaeti Kreuzberg: Kiosk K-BER-0024 mit IBAN, Kommissionslager Kommissionsware Kunden/K-BER-0024 (leer) und Lieferauftrag RAN/OUT/00036. "
          "Eine zweite Mail mit gleicher E-Mail-Adresse wurde als Dublette zu K-BER-0024 auf Pruefen gesetzt. Eine Mail ohne Pflichtfelder legte keinen Kiosk an. "
          "Zwei weitere Mails ergaben K-BER-0025 (Berlin) und K-KOE-0004 (Koeln), das Gebiet folgt dem Ort.")
    note("<b>Hinweis.</b> Die Kiosk-ID folgt dem Gebiet: K-BER-nnnn fuer Berlin, K-KOE-nnnn fuer Koeln. Das Feldformat der echten Flixcheck-Mail ist noch offen, bis eine echte Mail vorliegt.", "warn", s)

    para("5. Erstbestueckung und Uebergabeprotokoll", s, H1)
    para("<b>Ziel.</b> Die Ware wird erst mit Unterschrift und Kuehlschrank-Foto gebucht. Vorher gehoert dem Kiosk nichts.", s)
    para("<b>Wer.</b> Fahrer (Gruppe MAGYC Fahrer), am Handy.", s)
    steps(["Der Fahrer laedt die Ware aus der Pickzone ins Fahrzeuglager (Umlagerung auf FZ/BER-01 oder FZ/KOE-01).",
           "Beim Kiosk: <b>Lager &gt; Lieferungen</b>, Lieferauftrag oeffnen, Reiter <b>Uebergabe</b>.",
           "Der Kiosk unterschreibt auf dem Bildschirm, der Fahrer fotografiert den bestueckten Kuehlschrank.",
           "<b>Uebergabe bestaetigen</b>. Erst jetzt wird gebucht, der Kiosk wird <b>aktiv</b>.",
           "Kontrolle: Lieferung Erledigt, Kommissionslager gefuellt, Kiosk-Status aktiv."], s)
    shot(s, "s11-erstbestueckung-offen.png")
    shot(s, "s10-uebergabe.png")
    shot(s, "s09-kontakt-kiosk.png")
    ex(s, "RAN/OUT/00036 fuer K-BER-0024: ohne Unterschrift Meldung 'Ohne Unterschrift im Uebergabeprotokoll wird nicht gebucht', "
          "mit Unterschrift aber ohne Foto 'Foto des bestueckten Kuehlschranks fehlt'. Mit beidem: 192 Dosen im Kommissionslager, Kiosk aktiv. "
          "RAN/OUT/00037 (K-BER-0025) und RAN/OUT/00038 (K-KOE-0004) warten noch auf den Fahrer.")
    note("<b>Technischer Hinweis.</b> Die Buchung laeuft ohne SMS-Dialog. Ohne diese Einstellung blieb die Lieferung stehen, weil das Modul stock_sms eine Bestaetigung verlangt.", "info", s)

    para("6. Startpraemie und Akquisiteur-Provision", s, H1)
    steps(["Mit dem bestaetigten Uebergabeprotokoll entstehen zwei Aufgaben fuer die Finanzen: <b>Startpraemie zahlen</b> (50 EUR an den Kiosk, mit IBAN) und die Provision fuer Primewave (50 EUR).",
           "Nach der Zahlung am Kontakt, Reiter <b>MAGYC</b>: <b>Praemie als ausgezahlt markieren</b>.",
           "Kontrolle: Startpraemie steht auf <b>Ausgezahlt</b>, Datum gesetzt."], s)
    ex(s, "K-BER-0024: Startpraemie wechselte von Keine auf Offen und nach Markierung auf Ausgezahlt am 19.11.2026. Die Aufgabe Startpraemie zahlen (K-BER-0024) lag bei der Finanz-Person.")

    # ------------------------------------------------------------------ C
    s.append(Paragraph("Teil C. Abverkauf und Rechnung", PART))
    para("7. Zaehlung und Abverkauf", s, H1)
    para("<b>Ziel.</b> Der Store Success Manager (SSM) zaehlt im Kiosk. Daraus entsteht die Menge, die in Rechnung geht. Mengen werden nicht getippt, sondern aus dem Bestand abgeleitet, der Preis kommt aus der Preisliste.", s)
    steps(["Am Kiosk-Kontakt <b>Bestand zaehlen</b>. Es entsteht eine Abverkaufsmeldung mit je einer Zeile je Sorte.",
           "In <b>Gezaehlt</b> den Bestand im Kuehlschrank eintragen. <b>Abverkauf</b> ist Sollbestand minus gezaehlt.",
           "<b>Bestaetigen</b>. Die verkaufte Menge geht aus dem Kommissionslager.",
           "Kontrolle: Status <b>Bestaetigt</b>, Rest im Kommissionslager stimmt."], s)
    shot(s, "s12-abverkauf.png")
    ex(s, "K-BER-0024, Soll 96 Lemon und 96 Berry. Gezaehlt 60 Lemon und 70 Berry. Abverkauf 36 Lemon und 26 Berry, je 0,75 EUR netto, zusammen 46,50 EUR netto. Rest im Kommissionslager danach 130 Dosen.")
    para("<b>Differenz klaeren.</b> Ist weniger gezaehlt, als System, Abverkauf und Rueckgabe erklaeren, entsteht eine Differenz. Das System sperrt die Bestaetigung.", s)
    steps(["<b>Differenz markieren</b> legt eine Pruefaufgabe an. Status <b>Pruefung Differenz</b>.",
           "Nach der Klaerung <b>Differenz geklaert</b>. Danach laesst sich bestaetigen."], s)
    shot(s, "s13-abverkauf-differenz.png")
    ex(s, "Eine zweite Zaehlung mit 40 Dosen Differenz wurde zuerst mit 'Bestandsdifferenz offen' abgelehnt, nach der Klaerung bestaetigt. Mit nur 10 verkauften Dosen entstand keine Rechnung: 'Rechnung erst ab 24 Dosen'.")

    para("8. Rechnung mit Pfand", s, H1)
    steps(["In der bestaetigten Meldung <b>Rechnung erstellen</b>. Voraussetzung: mindestens 24 Dosen, keine offene Differenz.",
           "Die Rechnung enthaelt je Sorte eine Zeile und das Pfand als eigene Zeile, jeweils 19 % USt.",
           "Kontrolle: Rechnung gebucht, Pfandmenge ist gleich der verkauften Menge."], s)
    shot(s, "s14-rechnung.png")
    ex(s, "INV/2026/00001 an DEMO Spaeti Kreuzberg: 36 Lemon x 0,75 = 27,00, 26 Berry x 0,75 = 19,50, Pfand 62 x 0,25 = 15,50. Netto 62,00, USt 11,78, brutto 73,78.")
    note("<b>Regel.</b> Verkaufte Ware verlaesst das Kundenlager mit der Rechnung. Der Restbestand bleibt MAGYC-Eigentum. Bei Kioskrechnungen ist der Bestand schon mit der Abverkaufsmeldung ausgebucht.", "info", s)

    para("9. Nachschub und Liefersperre", s, H1)
    steps(["Am Kiosk-Kontakt <b>Nachschub anfordern</b>.",
           "Trays Lemon und Berry eintragen. Mindestens 4 Trays gesamt.",
           "Gibt es eine ueberfaellige Rechnung oder eine offene Differenz, bricht das System mit einer Meldung ab.",
           "Sonst entsteht ein Lieferauftrag. Gebucht wird wie bei der Erstbestueckung mit Unterschrift."], s)
    shot(s, "s19-nachschub.png")
    ex(s, "K-BER-0024 mit 2 + 2 Trays = 96 Dosen: Lieferauftrag RAN/OUT/00041. Mit 1 + 1 Tray: 'Nachschub erst ab 4 Trays. Aktuell 2'. "
          "K-BER-0025 hatte eine 30 Tage ueberfaellige Rechnung: 'Liefersperre: offene ueberfaellige Rechnung'.")

    # ------------------------------------------------------------------ D
    s.append(Paragraph("Teil D. Pfand und Logistik", PART))
    para("10. Pfand: Ruecknahme und Rueckstellung", s, H1)
    para("<b>10.1 Ruecknahme.</b> Zurueckgenommenes Pfand erzeugt eine Gutschrift. Kioske sind ausgenommen, ihr Pfand laeuft ueber die Abverkaufsrechnung und die DPG.", s)
    steps(["<b>Pfand &gt; Pfand-Ruecknahme</b>, <b>Neu</b>, Kunde waehlen.", "Menge und Preis je Dose eintragen.", "<b>Gutschrift erstellen</b>."], s)
    shot(s, "s15-pfand-ruecknahme.png")
    ex(s, "DEMO Bistro B2B gab 20 Dosen zurueck: Gutschrift RINV/2026/00001 ueber 5,00 EUR netto. Fuer K-BER-0024 wurde dieselbe Aktion abgelehnt ('Keine Pfandrueckgabe an Kioske').")
    para("<b>10.2 Pfandzeile im Auftrag.</b> B2B-Auftraege bekommen je Dose eine Pfandzeile zu 0,25 EUR netto. Im Onlineshop ist 0,25 EUR der Bruttopreis.", s)
    ex(s, "S00005 DEMO Bistro B2B, 48 Dosen: Pfandzeile 48 x 0,25 netto. S00006 Webshop, 24 Dosen: 0,2101 netto je Dose, das sind 0,25 brutto.")
    para("<b>10.3 Rueckstellung.</b> Die Kanzlei verlangt: Pfand in Verkehr brutto auf 4401, Rueckstellung fuer nicht zurueckgenommene Dosen netto, Soll 4000 gegen Haben 3071.", s)
    steps(["<b>Pfand &gt; Pfand-Rueckstellung</b>.", "Periode, ausgegebene und zurueckgenommene Dosen eintragen, die Konten 3071 und 4000 und das Journal waehlen.",
           "<b>Buchen</b>. Kontrolle: Die Salden von 4000 und 4401 stimmen im Zahlenwert ueberein."], s)
    shot(s, "s16-pfand-rueckstellung.png")
    ex(s, "1.000 Dosen ausgegeben, 500 zurueck: 125,00 EUR brutto offen, Rueckstellung 105,04 EUR netto. Buchung MISC/2026/11/0002, Soll Bestandsveraenderung Pfandverbindlichkeiten 105,04, Haben Offene Pfandruecknahmen 105,04. Das ist das Beispiel aus dem Schreiben der Kanzlei.")
    note("<b>Offen.</b> Staging laeuft im Kontenrahmen SKR03. Die Kanzlei nennt SKR04-Nummern. In SKR04 ist 4000 ein Erloeskonto, 4401 und 3071 gibt es nicht. Die Konten stehen bis zur Antwort der Kanzlei unter den genannten Nummern.", "warn", s)

    para("11. Tour planen", s, H1)
    steps(["<b>Kommission &gt; Logistik &gt; Touren</b>, <b>Neu</b>. Gebiet (Berlin oder Koeln), Fahrer und Fahrzeuglager eintragen.",
           "<b>Offene Lieferungen uebernehmen</b>. Die Stopps werden nach Postleitzahl sortiert.",
           "Kontrolle: Nur Kioske des Gebiets, Reihenfolge aufsteigend nach PLZ."], s)
    shot(s, "s17-tour.png")
    ex(s, "Tour Berlin: 2 Stopps, 10999 (Kreuzberg) vor 12045 (Neukoelln). Tour Koeln: ein Stopp, Ehrenfeld.")

    para("12. Speditionstransfer zwischen Lagern", s, H1)
    steps(["<b>Kommission &gt; Logistik &gt; Speditionstransfer</b>.", "Quelle, Ziel und Anzahl Paletten eintragen. Eine Palette sind 12 Trays je Sorte.",
           "<b>Transfer erstellen</b>. Es entsteht ein interner Transfer, die Chargen werden nach FEFO gewaehlt."], s)
    shot(s, "s18-spedition.png")
    ex(s, "1 Palette von Rangsdorf nach Koeln: 576 Dosen (12 Trays Lemon plus 12 Trays Berry), Beleg RAN/QC/00012.")

    # ------------------------------------------------------------------ E
    s.append(Paragraph("Teil E. Abrechnung und Rueckholung", PART))
    para("13. Primewave-Abrechnung und Ruecknahme nach sechs Monaten", s, H1)
    para("<b>13.1 Monatsrechnung Primewave.</b> Ein Lauf schreibt am Monatsanfang eine Eingangsrechnung je Akquisiteur ueber alle im Vormonat uebergebenen Kioske, eine Zeile je Kiosk zu 50 EUR. Ein zweiter Lauf legt nichts doppelt an.", s)
    ex(s, "Zeile K-BER-0024 10/2026 zu 50,00 EUR, Rechnung als Entwurf an Primewave Media UG, Summe 50,00 EUR.")
    para("<b>13.2 Ruecknahme nach sechs Monaten.</b> Unverkaufte Ware, die laenger als 6 Monate im Kiosk liegt, wird in die Qualitaetssperre zurueckgebucht.", s)
    ex(s, "Zum Test wurde der Bestand von K-BER-0024 auf 200 Tage alt gesetzt. Der Lauf legte RAN/QC/00013 an. Danach hat der Kiosk keinen Bestand mehr.")
    note("<b>Hinweis.</b> Der Bestand von K-BER-0024 auf Staging ist deshalb 0. Das ist das Ergebnis dieses Pruefschritts.", "warn", s)

    # ------------------------------------------------------------------ F
    s.append(Paragraph("Teil F. Pruefprotokoll", PART))
    para("14. Pruefprotokoll: 51 Schritte", s, H1)
    para("Der Ablauf wurde zuerst auf einer Kopie und danach auf Staging ausgefuehrt. Alle 51 Schritte waren erfolgreich. Der Ablauf legt auch die Beispieldaten an.", s)
    rows = []
    f = os.path.join(HERE, "e2e_results.txt")
    if os.path.exists(f):
        for line in open(f, encoding="utf-8"):
            p = line.rstrip("\n").split("|")
            if p[0] == "RES" and len(p) >= 5:
                rows.append([p[1], p[3][:78], p[2]])
    table(["Nr.", "Pruefung", "Ergebnis"], rows or [["", "keine Daten", ""]], [14 * mm, 128 * mm, 26 * mm], s)
    para("Nicht geprueft sind Dinge, die von Dritten abhaengen: DSV/UPS-Etikett (Zugangsdaten fehlen), echte Flixcheck-Mail, Hardware-Scanner, "
         "Eingang einer Mail am Staging-Postfach (Mail-Versand ist dort abgeschaltet). Diese Punkte stehen in der Liste der offenen Angaben.", s)
    para("Ende des Bedienhandbuchs. Aenderungswuensche an PassForm Digital, Projekt S00132.", s, SMALL)
    return s

if __name__ == "__main__":
    build(os.path.join(HERE, "MAGYC-Bedienhandbuch-De.pdf"), "Bedienhandbuch", "Jeder Prozess mit Bildern und Beispielen", manual())
