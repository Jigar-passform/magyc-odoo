"""Erzeugt zwei deutsche PDFs: Handbuch mit Statusbericht und die Liste der offenen Angaben."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                PageTemplate, Paragraph, Table, TableStyle)

SHOTS = "C:/Users/ABC/magyc-odoo/docs/screenshots"
NAVY = colors.HexColor("#0f2b46")
BLUE = colors.HexColor("#2a5d84")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")
GREEN = colors.HexColor("#1a7f37")
AMBER = colors.HexColor("#9a6700")
RED = colors.HexColor("#b42318")
ZEBRA = colors.HexColor("#f6f8fa")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.0, leading=12.2,
                      spaceAfter=3, textColor=INK)
STEP = ParagraphStyle("step", parent=BODY, leftIndent=14, bulletIndent=0,
                      bulletFontName="Helvetica-Bold", bulletFontSize=9.0, spaceAfter=2)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2,
                        bulletFontName="Helvetica", bulletFontSize=9.0, spaceAfter=1)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=8.5, leading=11.4, leftIndent=8,
                      textColor=GREY, spaceBefore=3, spaceAfter=6)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=26,
                    spaceAfter=4, textColor=NAVY)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17.5,
                    spaceBefore=10, spaceAfter=5, textColor=NAVY)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                     textColor=GREY, spaceAfter=10)
CAP = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
                     textColor=GREY, spaceBefore=2, spaceAfter=8)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.0, leading=10.3, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
CELL_S = ParagraphStyle("cells", parent=CELL, fontSize=7.4, leading=9.6)
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.0, leading=10.3,
                      textColor=colors.white)

MATRIX = [
    ("Kiosk", "Kontakt, Kiosk-ID, Kommissionslager, Gebiet, Akquisiteur", "umgesetzt", ""),
    ("Kiosk", "Statuskette vom Interessent bis inaktiv, Vertragslaufzeit", "umgesetzt", ""),
    ("Kiosk", "Kiosk-Postfach mit Mailadresse kiosk@, Umwandlung per Klick", "umgesetzt", "neu"),
    ("Kiosk", "Telefonnummer als Pflichtfeld", "umgesetzt", ""),
    ("Vertrag", "Kommissions- und Liefervertrag als Beleg", "umgesetzt", ""),
    ("Lieferung", "Erstbestückung, Nachschub, Übergabeprotokoll", "umgesetzt", ""),
    ("Lieferung", "FEFO-Zuteilung nach MHD, Chargen am Beleg", "umgesetzt", ""),
    ("Lieferung", "Liefersperre bei offenen Beträgen und Differenzen", "umgesetzt", "Regel bestätigen"),
    ("Abverkauf", "Mengen aus Bestand und Zählung, keine Eingabe der Verkaufsmenge", "umgesetzt", ""),
    ("Abverkauf", "Buchung Abverkauf und Rückgabe in die Qualitätssperre", "umgesetzt", ""),
    ("Abverkauf", "Rechnung je Zeitraum, Mindestmenge 24 Dosen", "umgesetzt", "Wert bestätigen"),
    ("Abverkauf", "Prüfstatus bei Differenz", "umgesetzt", ""),
    ("Pfand", "Pfandzeile mit 19 % USt, brutto und netto getrennt", "umgesetzt", ""),
    ("Pfand", "Pfand-Rücknahme als Gutschrift", "umgesetzt", "für Kioske Ausnahme"),
    ("Pfand", "DPG-Clearing Paragraf 17 UStG, Rückzahlungsverpflichtung", "offen", "Konten fehlen"),
    ("Lager", "Rangsdorf mit 28 Lagerplätzen, Qualitätssperre", "umgesetzt", ""),
    ("Lager", "Köln als Nebenlager mit Platzhalteradresse", "teilweise", "Adresse fehlt"),
    ("Lager", "Speditionstransfer Berlin nach Köln", "umgesetzt", "Palettenlogik prüfen"),
    ("Lager", "Verluste mit Kennzeichen RAN/MUSTER und RAN/SCHADEN", "umgesetzt", ""),
    ("Lager", "Sechsmonatige Rücknahme ohne Abverkauf", "umgesetzt", ""),
    ("Touren", "Tourplanung je Gebiet, Sortierung nach Postleitzahl", "umgesetzt", ""),
    ("Touren", "Fahrer-App für unterwegs", "offen", "eigener Aufwand"),
    ("Provision", "Startprämie 50 EUR, Akquisiteur-Pauschale monatlich", "umgesetzt", ""),
    ("Belege", "Belegtexte je Belegart pflegbar", "umgesetzt", ""),
    ("Belege", "Mahnwesen mit drei Stufen", "umgesetzt", "Vorlagen freigegeben"),
    ("Buchhaltung", "SKR04 mit 1.312 Konten, 19 % USt", "umgesetzt", ""),
    ("Buchhaltung", "DATEV-Export als DTVF-Paket", "umgesetzt", "Nummern fehlen"),
    ("Schnittstellen", "DHL, UPS, DPD", "offen", "Zugänge fehlen"),
    ("Schnittstellen", "Onlineshop und Marktplätze", "offen", "Zugänge fehlen"),
    ("Schnittstellen", "KI-gestützte Erfassung von Kiosk-Anfragen", "offen", "Postfach vorhanden"),
]

EXTRA = [
    ("DPG-Clearing und Pfandrückzahlungsverpflichtung",
     "Konten und Buchungslogik nach Paragraf 17 UStG, Abstimmung mit TU Treuhand"),
    ("Fahrer-App", "Mobile Ansicht für Tour, Übergabe und Rückgabe, 3 bis 5 Tage"),
    ("Vollständige Tourplanung Berlin und Köln",
     "Feinplanung der Gebiete, Fahrzeuge und Zeitfenster, 4 bis 6 Tage"),
    ("Versand und Marktplätze", "DHL, UPS, DPD, Onlineshop, Marktplätze inklusive Pfand und Steuer"),
    ("KI-Erfassung", "Auslesen der Kiosk-Anfragen und Vorbefüllung, Hosting der Mailadresse"),
    ("Köln als Vollager", "echte Adresse, Regalplan, Umlagerungsprozess, Bestandsführung"),
    ("Mehrsprachigkeit", "Belege und Oberfläche in weiteren Sprachen"),
]

# Wer, Angabe, warum nötig, was blockiert
OPEN = [
    ("TU Treuhand", "Konten für Pfand, Pfanderstattung, DPG-Clearing, Rückzahlungsverpflichtung",
     "Buchungslogik nach Paragraf 17 UStG", "Pfandabrechnung und Bilanzansatz"),
    ("TU Treuhand", "Anlagekonten und Anlagenverzeichnis",
     "Bewertung von Stapler, Packtisch, Kühlschränken, Regalen", "Anlagenbuchhaltung"),
    ("TU Treuhand", "DATEV-Berater- und Mandantennummer, Sachkontenlänge, Wirtschaftsjahr",
     "Kopfzeile und Kontenlänge im Export", "DATEV-Export im Echtbetrieb"),
    ("Geschäftsführung", "B2B-Preislisten mit Staffeln und Konditionen",
     "Preis kommt aus der Preisliste, nicht aus dem Auftrag", "B2B-Angebote"),
    ("Geschäftsführung", "Endkundenpreise im Onlineshop je Sorte",
     "Bruttopreise und Pfand im Shop", "Shop-Anbindung"),
    ("Geschäftsführung", "Zahlungsziel B2B, Bestätigung Startprämie und Akquisiteur-Pauschale",
     "Fälligkeiten und Provisionsrechnung", "Mahnwesen, Provisionslauf"),
    ("Geschäftsführung", "Freigabe für das Ausrollen auf die Produktivinstanz",
     "Instanz wird von MAGYC betrieben", "Produktivnahme"),
    ("Abfüllung", "Einkaufspreise je Dose, Gewichte je Dose, Tray und Palette",
     "Kalkulation, Verpackungseinheiten, Fracht", "Margen, Liefermengen"),
    ("Abfüllung", "Ansprechpartner und Lieferadresse für den Wareneingang",
     "Wareneingang und Buchung", "Bestandsführung"),
    ("Vermietung", "Anschrift und Regalplan Köln, Inventarliste Kühlschränke",
     "echtes Lager statt Platzhalter", "Umlagerung Köln, Anlagen"),
    ("Zugänge", "DHL, UPS, DPD, Onlineshop, Marktplätze",
     "Versand und Kanäle", "Versandabwicklung, Shop"),
    ("Zugänge", "USt-IdNr., IBAN, Termin für die Ablösung von Qonto",
     "Belege und Zahlungsverkehr", "Rechnungen, Lastschrift"),
]

CHECK = [
    ("Erweiterungen Kiosk und Provision", "14 Tests, kein Fehler"),
    ("Soll-Ablauf", "13 Tests, kein Fehler"),
    ("DATEV-Export", "9 Tests, kein Fehler"),
    ("Gesamt", "36 Tests, kein Fehler"),
    ("Probelauf mit Beispieldaten",
     "Lager Köln, vier Kioske, Lieferungen, Rechnung, DATEV-Paket erzeugt"),
]


def p(text, style=BODY):
    return Paragraph(text, style)


def steps(items):
    return [Paragraph(t, STEP, bulletText=f"{i}.") for i, t in enumerate(items, start=1)]


def bullets(items):
    return [Paragraph(t, BULLET, bulletText="\u2022") for t in items]


def figure(path, caption):
    width = 168 * mm
    return KeepTogether([
        Image(path, width=width, height=width * 900.0 / 1440.0),
        Paragraph(caption, CAP),
    ])


def styled(data, widths, colour_col=None, colours_map=None):
    table = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    if colour_col is not None:
        for i, colour in (colours_map or {}).items():
            style.append(("TEXTCOLOR", (colour_col, i), (colour_col, i), colour))
    table.setStyle(TableStyle(style))
    return table


def table(rows, widths, head):
    data = [[Paragraph(h, HEAD) for h in head]]
    data += [[Paragraph(str(a), CELL_B)] + [Paragraph(str(b), CELL) for b in rest]
             for a, *rest in rows] if len(head) > 2 else \
            [[Paragraph(str(a), CELL_B), Paragraph(str(b), CELL)] for a, b in rows]
    return styled(data, widths)


def matrix_table():
    data = [[Paragraph("Bereich", HEAD), Paragraph("Funktion", HEAD),
             Paragraph("Stand", HEAD), Paragraph("Anmerkung", HEAD)]]
    colours = {}
    for i, (area, func, state, note) in enumerate(MATRIX, start=1):
        data.append([Paragraph(area, CELL_B), Paragraph(func, CELL_S),
                     Paragraph(state, CELL_B), Paragraph(note, CELL_S)])
        colours[i] = {"umgesetzt": GREEN, "teilweise": AMBER}.get(state, RED)
    return styled(data, [24, 92, 20, 34], colour_col=2, colours_map=colours)


def footer(label):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(20 * mm, 11 * mm,
                          f"MAGYC DRINKS GmbH \u00b7 {label} \u00b7 Stand 10.11.2026")
        canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, str(doc.page))
        canvas.restoreState()
    return draw


def document(out, title, label):
    doc = BaseDocTemplate(out, pagesize=A4, title=title, author="PassForm Digital",
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=22 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer(label))])
    return doc


def build_manual(out):
    doc = document(out, "MAGYC DRINKS GmbH \u2013 Odoo 20 Handbuch", "Odoo 20 Handbuch")
    story = [
        p("MAGYC DRINKS GmbH", H1),
        p("Odoo 20 Handbuch: Einrichtung, Abläufe, Prüfung und Umfang. Stand: 10. November 2026.", SUB),

        p("1. Zweck und Aufbau", H2),
        p("Dieses Handbuch beschreibt alle eingerichteten Abläufe für das Kommissionsgeschäft mit "
          "Kiosken, die eigenen Erweiterungen und den DATEV-Export. Jede Funktion nennt den Menüweg "
          "und die Schritte in der Reihenfolge, in der sie im Alltag gebraucht werden. Wo ein "
          "Screenshot vorhanden ist, markieren rote Rahmen und Nummern die Felder aus der Anleitung. "
          "Kapitel 19 und 20 zeigen den Prüfstand und den Umfang. Die Angaben, die von MAGYC noch "
          "fehlen, stehen im getrennten Dokument Offene Angaben.", BODY),
        *bullets([
            "Grundlage: Vertriebs- und Lieferkonzept vom 09.11.2026 und der abgestimmte Soll-Ablauf.",
            "Die Ware bleibt bis zum Abverkauf Eigentum der MAGYC DRINKS GmbH (Paragraf 3 Absatz 3 UStG).",
            "Steuer und Pfand entstehen erst beim Abverkauf, nicht bei der Übergabe.",
        ]),

        p("2. Systemüberblick", H2),
        p("Die Erweiterungen liegen in fünf Modulen und nutzen die Standardfunktionen von Odoo 20, "
          "statt sie zu ersetzen. Dadurch bleiben Auswertungen, Buchhaltung und Lagerlogik "
          "updatefähig.", BODY),
        table([
            ("Verkauf", "Kommissionsgeschäft Kiosk, Preislisten, Liefersperre, Belegtexte"),
            ("Fakturierung", "SKR04, Abverkaufsrechnung, Pfandzeile, Mahnwesen, DATEV-Export"),
            ("Lager", "Rangsdorf und Köln, Kommissionslager je Kiosk, Qualitätssperre, Touren"),
            ("Kontakte", "Kiosk-Stammdaten, Statuskette, Akquisiteur, Kiosk-Postfach"),
        ], [45, 125], ("App-Bereich", "Umfang")),

        p("3. Kiosk anlegen", H2),
        p("Ein Kiosk ist ein Kontakt mit dem Kundentyp Kiosk. Beim Speichern legt das System "
          "automatisch einen eigenen Kommissionslagerort an, benannt nach der Kiosk-ID. Die "
          "Telefonnummer ist Pflicht, weil jede Nachbestellung und jede Rückfrage darüber läuft.", BODY),
        *steps([
            "Kontakte öffnen und einen neuen Kontakt anlegen.",
            "Reiter MAGYC wählen.",
            "Kiosk-ID nach Schema K-BER-0001 eintragen (Feld 1).",
            "Kundentyp Kiosk (Kommission) wählen (Feld 2).",
            "Kommissionslager wird automatisch erzeugt und angezeigt (Feld 3).",
            "Gebiet, Akquisiteur und Store Success Manager ergänzen (Feld 4).",
        ]),
        figure(f"{SHOTS}/ann-01-kiosk-kontakt.png",
               "Abbildung 1: Kontakt mit Reiter MAGYC. 1 Kiosk-ID, 2 Kundentyp, "
               "3 automatisch erzeugtes Kommissionslager, 4 Gebiet."),

        p("4. Statuskette und Vertrag", H2),
        p("Der Kiosk-Status wird über Aktionen geführt und nicht frei gesetzt. So ist jederzeit "
          "erkennbar, ob ein Kiosk nur ein Interessent ist oder bereits beliefert wird.", BODY),
        table([
            ("Interessent", "Kontakt erfasst, noch kein Vertrag"),
            ("Vertrag eingegangen", "Unterschriebener Vertrag liegt vor"),
            ("Erstbestückung geplant", "Lieferung ist angelegt, Ware noch nicht übergeben"),
            ("Aktiv", "Ware übergeben, Abverkauf und Abrechnung laufen"),
            ("Inaktiv", "Kein Vertrag mehr, keine Belieferung"),
        ], [45, 125], ("Status", "Bedeutung")),
        *bullets([
            "Vertragsbeginn und Laufzeit (Standard 12 Monate) erfassen, das Vertragsende wird berechnet.",
            "IBAN des Kiosks hinterlegen, bevor die Startprämie ausgezahlt wird.",
            "Beleg Kommissions- und Liefervertrag aus dem Kontakt drucken.",
        ]),

        p("5. Kiosk-Postfach", H2),
        p("Bewerbungen und Anfragen kommen über die Adresse kiosk@ in Odoo an. Jede Nachricht wird "
          "als Bewerbung gespeichert und kann mit einem Klick in einen Kiosk umgewandelt werden.", BODY),
        *steps([
            "Kommission, Kiosk-Postfach öffnen.",
            "Eintrag prüfen: Betreff, E-Mail, Telefon, Ort und Nachricht.",
            "Fehlende Telefonnummer ergänzen, sie ist für die Kiosk-Anlage Pflicht.",
            "Kiosk anlegen: das Kontaktformular öffnet sich vorbefüllt, Status wird Interessent.",
            "Nicht passende Anfragen mit Ablehnen schließen.",
            "Alternativ Aktionen ausführen, wenn die Anfrage telefonisch oder auf der Messe eingeht.",
        ]),
        p("Hinweis: Es wird bewusst kein Kiosk automatisch erzeugt. Ohne Telefonnummer wäre der "
          "Datensatz unvollständig und würde bei der ersten Lieferung scheitern.", NOTE),

        p("6. Ware an den Kiosk übergeben", H2),
        p("Die Übergabe erfolgt als Lieferschein vom Lager an den Kommissionslagerort des Kiosks. "
          "Das Übergabeprotokoll wird gedruckt und von beiden Seiten unterschrieben. Die Ware bleibt "
          "Eigentum der MAGYC DRINKS GmbH.", BODY),
        *steps([
            "Kommission, Nachschub / Erstbestückung öffnen.",
            "Kiosk wählen, Art der Lieferung und Menge in Trays erfassen.",
            "Lieferung anlegen; die Chargen werden nach MHD zugeteilt (FEFO).",
            "Lieferung ausführen: Menge prüfen und validieren.",
            "Übergabeprotokoll drucken, Foto und Unterschrift am Lieferschein hinterlegen.",
        ]),
        *bullets([
            "Erstbestückung: 8 Trays, je 4 Lemon Zero und 4 Berry Zero.",
            "Nachschub: mindestens 4 Trays, ausgelöst durch den Abverkauf oder durch die Tour.",
            "Das Kommissionslager zeigt jederzeit, welche Menge beim Kiosk steht.",
        ]),

        p("7. Abverkauf melden und abrechnen", H2),
        p("Die abverkaufte Menge ergibt sich aus dem Bestand beim Kiosk abzüglich der gezählten "
          "Restmenge. Eine eingetippte Verkaufsmenge wird nicht akzeptiert, weil sie nicht "
          "nachvollziehbar ist.", BODY),
        *steps([
            "Kommission, Abverkauf Kiosk, Neu.",
            "Kiosk wählen (Feld 1); das Kommissionslager wird vorbelegt.",
            "Zeitraum von und bis setzen (Felder 2 und 3).",
            "Positionen erfassen: Artikel, erwartete Menge, gezählte Menge, Rückgabe, Preis netto (Feld 4).",
            "Bestätigen: Abverkauf und Rückgabe werden gebucht.",
            "Rechnung erstellen: Rechnung über den Abverkauf wird erstellt und gebucht.",
        ]),
        figure(f"{SHOTS}/ann-02-kommission-neu.png",
               "Abbildung 2: Neue Abverkaufsmeldung. 1 Kiosk, 2 Zeitraum von, 3 Zeitraum bis, "
               "4 Positionen mit erwarteter und gezählter Menge."),
        figure(f"{SHOTS}/ann-03-abverkauf-formular.png",
               "Abbildung 3: Abgerechnete Meldung. 1 Drucken, 2 Status, 3 Rechnung und Summen."),
        *bullets([
            "Differenz zwischen erwarteter und gezählter Menge: Meldung geht in Prüfung, es wird nicht fakturiert.",
            "Prüfung abschließen oder Differenz freigeben, danach ist die Rechnung möglich.",
            "Rechnung erst ab 24 Dosen je Zeitraum, kleinere Mengen werden in den nächsten Zeitraum übertragen.",
        ]),

        p("8. Pfand", H2),
        p("Pfand ist eine eigene Position mit 19 % USt. Beim Kiosk entsteht es erst mit der "
          "Abverkaufsrechnung, nicht bei der Übergabe.", BODY),
        *steps([
            "Firma, Reiter Pfand (MAGYC): Pfand automatisch ergänzen aktivieren und Pfandartikel wählen.",
            "Kommission, Pfand-Rücknahme, Neu: Kunde und Datum erfassen.",
            "Position mit Pfandartikel und Menge ergänzen.",
            "Gutschrift erstellen: Beleg wird mit 19 % USt gebucht.",
        ]),
        figure(f"{SHOTS}/ann-04-pfand-gutschrift.png",
               "Abbildung 4: Pfand-Rücknahme. 1 Kunde, 2 erzeugte Gutschrift, 3 Status."),
        p("Abweichung zum Soll-Ablauf: Für Kioske ist keine Pfandgutschrift vorgesehen, weil das "
          "Leergut über die DPG abgerechnet wird. Die Gutschrift bleibt als Ausnahme für B2B und "
          "für Sonderfälle verfügbar.", NOTE),

        p("9. Rückgaben, Qualitätssperre und Verluste", H2),
        p("Rückgaben aus dem Kiosk gehen nicht direkt zurück in den Verkauf, sondern in die "
          "Qualitätssperre und werden dort geprüft.", BODY),
        *bullets([
            "Bestätigter Abverkauf bucht die Rückgabemenge automatisch in die Qualitätssperre.",
            "Verluste werden über eine Lagerbuchung mit Kennzeichen erfasst: RAN/MUSTER oder RAN/SCHADEN.",
            "RAN/SCHADEN benötigt die Freigabe durch die Lagerleitung, RAN/MUSTER nicht.",
            "Nach sechs Monaten ohne Abverkauf holt die sechsmonatige Rücknahme die Restware zurück.",
        ]),

        p("10. Touren planen", H2),
        p("Eine Tour fasst die offenen Lieferungen eines Gebiets zusammen und sortiert die Stopps "
          "nach Postleitzahl. Die Reihenfolge in Zehnerschritten lässt Platz für Zwischenstopps.", BODY),
        *steps([
            "Kommission, Touren, Neu.",
            "Name, Datum, Gebiet und Fahrer erfassen.",
            "Offene Lieferungen übernehmen: alle passenden Lieferscheine werden zugeordnet.",
            "Stopps prüfen und bei Bedarf die Reihenfolge ändern.",
            "Tour abschließen, wenn alle Stopps erledigt sind.",
        ]),

        p("11. Speditionstransfer Berlin nach Köln", H2),
        p("Der Transfer zwischen den Lagern wird über einen Assistenten gebucht, damit die Ware "
          "nicht doppelt erfasst wird und der Bestand in beiden Lagern stimmt.", BODY),
        *steps([
            "Kommission, Speditionstransfer öffnen.",
            "Quelllager und Ziellager wählen.",
            "Paletten und Trays je Palette erfassen, Notiz für die Spedition ergänzen.",
            "Transfer buchen: die Lieferung wird erzeugt und direkt validiert.",
            "Bestand in beiden Lagern prüfen.",
        ]),

        p("12. Startprämie und Akquisiteur", H2),
        p("Die Startprämie von 50 EUR wird mit der ersten Übergabe fällig, die Akquisiteur-Pauschale "
          "monatlich je aktivem Kiosk. Beide Beträge sind in der Firma hinterlegt.", BODY),
        *bullets([
            "Startprämie: Status am Kiosk zeigt offen, ausgezahlt oder storniert.",
            "Akquisiteur-Rechnung: monatlicher Lauf erzeugt die Sammelrechnung.",
            "Pflege der Pauschale in den Einstellungen der Firma, Reiter MAGYC.",
        ]),

        p("13. Liefersperre", H2),
        p("Ein Kiosk mit überfälliger Rechnung oder offener Differenz kann nicht beliefert werden. "
          "Die Sperre greift beim Bestätigen des Auftrags und zeigt den Grund an.", BODY),
        *bullets([
            "Sperre aufheben nur mit Begründung und Berechtigung, die Aufhebung wird protokolliert.",
            "Tage bis zur Sperre sind in den Einstellungen der Firma hinterlegt.",
        ]),

        p("14. Belegtexte pflegen", H2),
        p("Alle Kopf- und Fußtexte liegen als Datensätze in Odoo. Änderungen wirken sofort auf die "
          "Belege, ohne Anpassung am Code. Rechnungstexte richten sich nach dem Kundentyp.", BODY),
        *bullets([
            "Kommission, Belegtexte: Zeile wählen und Texte ändern",
            "Belegarten: Angebot, Auftragsbestätigung, Lieferschein, Rechnung B2B, Rechnung Kiosk, "
            "Rechnung Onlineshop, Gutschrift",
        ]),
        figure(f"{SHOTS}/raw-05-belegtexte.png",
               "Abbildung 5: Belegtexte je Belegart mit Einleitungs- und Schlusstext."),

        p("15. Mahnwesen", H2),
        p("Drei Stufen sind hinterlegt und mit den freigegebenen Texten verknüpft: "
          "Zahlungserinnerung am Fälligkeitstag, 1. Mahnung nach 7 Tagen, 2. Mahnung nach "
          "weiteren 5 Tagen.", BODY),
        *bullets([
            "Einstellungen, Mahnwesen: Stufen, Verzögerung und Vorlage prüfen",
            "Versand erfolgt über die Zahlungserinnerungen je Kunde",
        ]),
        figure(f"{SHOTS}/raw-06-mahnstufen.png",
               "Abbildung 6: Drei Mahnstufen mit Vorlage je Stufe."),

        p("16. DATEV-Export", H2),
        p("Der Export erzeugt die Dateien, die DATEV für die Buchführung erwartet: Buchungsstapel, "
          "Debitoren und Kreditoren sowie Kontenbeschriftungen. Die Dateien werden als Paket "
          "heruntergeladen und in DATEV importiert.", BODY),
        *steps([
            "Buchhaltung, Berichterstattung, DATEV DTVF Export öffnen.",
            "Geschäftsjahr und Zeitraum wählen.",
            "Export erzeugen; das Paket enthält drei CSV-Dateien.",
            "Paket herunterladen und in DATEV importieren.",
            "Bei Fehlermeldungen: Kontenzuordnung und Debitorennummern prüfen.",
        ]),
        *bullets([
            "Kontenlänge, Berater- und Mandantennummer stehen in den Einstellungen der Firma.",
            "Debitoren- und Kreditorennummern werden je Kontakt vergeben, fortlaufend oder manuell.",
            "Der Export ist auf der Entwicklungsdatenbank mit Platzhaltern geprüft, "
            "die echten Nummern kommen von TU Treuhand.",
        ]),

        p("17. Stammdaten und Preislisten", H2),
        p("Preise werden nie im Auftrag eingetippt, sondern kommen aus der Preisliste des Kunden. "
          "Damit sind Aktionen und Staffeln an einer Stelle pflegbar.", BODY),
        table([
            ("Kiosk", "0,75 EUR je Dose, Pfand 0,25 EUR netto"),
            ("B2B", "Staffelpreise, noch offen"),
            ("Onlineshop", "Bruttopreise, Pfand 0,25 EUR brutto"),
        ], [45, 125], ("Preisliste", "Stand")),
        *bullets([
            "Produkte: Lemon Zero und Berry Zero, GTIN am Produkt, GLN am Kiosk.",
            "Tray und Palette sind als Verpackung gepflegt, damit Mengen eindeutig sind.",
        ]),

        p("18. Rollen und Rechte", H2),
        p("Die Rechte folgen den Aufgaben. Die Freigabe von Schäden und die Aufhebung einer "
          "Liefersperre sind bewusst eingeschränkt.", BODY),
        table([
            ("Geschäftsführung", "Alle Rechte, Freigaben, Auswertungen"),
            ("Lagerleitung", "Lagerbuchungen, Schadensfreigabe, Touren"),
            ("Store Success Manager", "Kioske, Abverkauf, Übergaben"),
            ("Fahrer", "Touren, Übergaben, Rückgaben"),
            ("Buchhaltung", "Rechnungen, Mahnwesen, DATEV"),
        ], [50, 120], ("Rolle", "Aufgabe")),

        p("19. Prüfstand", H2),
        p("Alle Erweiterungen sind automatisiert geprüft. Zusätzlich wurde ein Probelauf mit "
          "Beispieldaten gefahren, der einen vollständigen DATEV-Export erzeugt.", BODY),
        table(CHECK, [62, 108], ("Prüfbereich", "Ergebnis")),

        p("20. Umfang S00132 und Mehraufwand", H2),
        p("Die Matrix zeigt je Funktion den Stand. Umgesetzt heißt: im System vorhanden und durch "
          "Tests oder Probelauf belegt. Teilweise heißt: Funktion steht, ein Wert fehlt. Offen "
          "heißt: nicht enthalten oder nicht möglich, weil Angaben oder Zugänge fehlen.", BODY),
        matrix_table(),
        p("Nicht Teil von S00132, technisch machbar und als Change Request beauftragbar:", BODY),
        table(EXTRA, [62, 108], ("Thema", "Aufwand und Voraussetzung")),

        p("21. Nächste Schritte", H2),
        *bullets([
            "Offene Angaben einsammeln, danach Konten und Preise vervollständigen",
            "DATEV-Probelauf mit echten Buchungen und Freigabe durch TU Treuhand",
            "Wartungsfenster festlegen und Erweiterungen ausrollen",
            "Schulung der Kiosk-Betreuung, danach Übergabe in den Betrieb",
        ]),

        p("Anhang: Begriffe", H2),
        table([
            ("Abverkauf", "Verkauf der Kommissionsware durch den Kiosk"),
            ("Erstbestückung", "Erste Lieferung an einen neuen Kiosk, 8 Trays"),
            ("Kommissionslager", "Lagerort beim Kiosk, Ware bleibt Eigentum von MAGYC"),
            ("Qualitätssperre", "Lagerort für Rückgaben, die geprüft werden"),
            ("FEFO", "Zuteilung nach MHD, kürzestes Datum zuerst"),
            ("Tray", "Verpackungseinheit, Grundlage für Liefermengen"),
        ], [45, 125], ("Begriff", "Erklärung")),
    ]
    doc.build(story)
    return out


def build_open(out):
    doc = document(out, "MAGYC DRINKS GmbH \u2013 Offene Angaben", "Offene Angaben")
    story = [
        p("MAGYC DRINKS GmbH", H1),
        p("Offene Angaben für den Produktivstart. Stand: 10. November 2026.", SUB),
        p("Die folgenden Angaben liegen nicht vor. Jede Zeile nennt, wofür die Angabe gebraucht "
          "wird und was bis dahin nicht abgeschlossen werden kann. Sobald eine Angabe vorliegt, "
          "wird sie im System ergänzt und die betroffene Funktion geprüft.", BODY),

        p("1. Übersicht nach Ansprechpartner", H2),
    ]
    rows = [[Paragraph("Wer", HEAD), Paragraph("Angabe", HEAD),
             Paragraph("Wofür", HEAD), Paragraph("Blockiert", HEAD)]]
    for who, what, why, blocks in OPEN:
        rows.append([Paragraph(who, CELL_B), Paragraph(what, CELL), Paragraph(why, CELL_S),
                     Paragraph(blocks, CELL_S)])
    story.append(styled(rows, [26, 76, 40, 28]))

    story += [
        p("2. Was ohne die Angaben trotzdem läuft", H2),
        *bullets([
            "Kiosk anlegen, Lieferung, Abverkauf und Rechnung funktionieren mit den hinterlegten Werten.",
            "Touren, Kiosk-Postfach, Verluste und Rücknahme sind vollständig nutzbar.",
            "Der DATEV-Export erzeugt Dateien, der Import in DATEV ist ohne echte Nummern nicht freigegeben.",
            "Liefersperre und Mahnwesen arbeiten, die Texte sind gesetzt.",
        ]),

        p("3. Rückmeldung", H2),
        p("Angaben können gesammelt oder einzeln geliefert werden. Sinnvoll ist die Reihenfolge: "
          "zuerst TU Treuhand, weil Konten und DATEV-Nummern mehrere Bereiche gleichzeitig "
          "freigeben; danach Preise und Zugänge. Für Rückfragen zu einzelnen Punkten steht "
          "PassForm Digital zur Verfügung.", BODY),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build_manual("MAGYC-Handbuch-De.pdf"))
    print(build_open("MAGYC-Offene-Angaben-De.pdf"))
