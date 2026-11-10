"""Erzeugt den deutschen Statusbericht (Stand 10.11.2026) mit Funktionsmatrix und offenen Angaben."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Table, TableStyle)

TITLE = "MAGYC DRINKS GmbH \u2013 Statusbericht Odoo 20"
AUTHOR = "PassForm Digital"

NAVY = colors.HexColor("#0f2b46")
BLUE = colors.HexColor("#2a5d84")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")
GREEN = colors.HexColor("#1a7f37")
AMBER = colors.HexColor("#9a6700")
RED = colors.HexColor("#b42318")

H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=26,
                    spaceAfter=4, textColor=NAVY)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                    spaceBefore=10, spaceAfter=5, textColor=NAVY)
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.0, leading=11.9,
                      spaceAfter=3, textColor=INK)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2,
                        bulletFontName="Helvetica", bulletFontSize=9.0, spaceAfter=1)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=8.6, leading=11.6, leftIndent=8,
                      textColor=GREY, spaceBefore=2, spaceAfter=6)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                     textColor=GREY, spaceAfter=10)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.0, leading=10.3, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
CELL_S = ParagraphStyle("cells", parent=CELL, fontSize=7.4, leading=9.6)
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.0, leading=10.3,
                      textColor=colors.white)

# Bereich, Funktion, Stand, Anmerkung
MATRIX = [
    ("Kiosk", "Kontakt, Kiosk-ID, Kommissionslager, Gebiet, Akquisiteur", "umgesetzt", ""),
    ("Kiosk", "Statuskette vom Interessent bis inaktiv, Vertragslaufzeit", "umgesetzt", ""),
    ("Kiosk", "Kiosk-Postfach mit Mailadresse kiosk@, Umwandlung per Klick", "umgesetzt", "neu"),
    ("Kiosk", "Telefonnummer als Pflichtfeld", "umgesetzt", ""),
    ("Vertrag", "Kommissions- und Liefervertrag als Beleg", "umgesetzt", ""),
    ("Lieferung", "Erstbestückung, Nachschub, Übergabeprotokoll", "umgesetzt", ""),
    ("Lieferung", "FEFO-Zuteilung nach MHD, Chargen am Beleg", "umgesetzt", ""),
    ("Lieferung", "Liefersperre bei offenen Beträgen und Differenzen", "umgesetzt", "Regel bestätigen"),
    ("Abverkauf", "Mengenermittlung aus Bestand und Zählung, keine Eingabe der Verkaufsmenge", "umgesetzt", ""),
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
    ("DPG-Clearing und Pfandrückzahlungsverpflichtung", "Konten und Buchungslogik nach Paragraf 17 UStG, Abstimmung mit TU Treuhand"),
    ("Fahrer-App", "Mobile Ansicht für Tour, Übergabe und Rückgabe, 3 bis 5 Tage"),
    ("Vollständige Tourplanung Berlin und Köln", "Feinplanung der Gebiete, Fahrzeuge und Zeitfenster, 4 bis 6 Tage"),
    ("Versand und Marktplätze", "DHL, UPS, DPD, Onlineshop, Marktplätze inklusive Pfand und Steuer"),
    ("KI-Erfassung", "Auslesen der Kiosk-Anfragen und automatische Vorbefüllung, Hosting der Mailadresse"),
    ("Köln als Vollager", "echte Adresse, Regalplan, Umlagerungsprozess, Bestandsführung"),
    ("Mehrsprachigkeit", "Belege und Oberfläche in weiteren Sprachen"),
]

QUESTIONS = [
    ("TU Treuhand", [
        "Konten für Pfand, Pfanderstattung, DPG-Clearing, Rückzahlungsverpflichtung",
        "Anlagekonten und Anlagenverzeichnis",
        "DATEV-Berater- und Mandantennummer, Sachkontenlänge, Wirtschaftsjahr",
    ]),
    ("Geschäftsführung", [
        "B2B-Preislisten und Endkundenpreise im Shop",
        "Zahlungsziel B2B, Bestätigung Startprämie und Akquisiteur-Pauschale",
        "Freigabe für das Ausrollen auf die Produktivinstanz",
    ]),
    ("Abfüllung", [
        "Einkaufspreise, Gewichte je Dose, Tray und Palette",
        "Ansprechpartner und Lieferadresse für den Wareneingang",
    ]),
    ("Vermietung", [
        "Anschrift und Regalplan Köln, Inventarliste Kühlschränke",
    ]),
    ("Zugänge", [
        "DHL, UPS, DPD, Onlineshop, Marktplätze",
        "USt-IdNr., IBAN, Termin für die Ablösung von Qonto",
    ]),
]


def p(text, style=BODY):
    return Paragraph(text, style)


def bullets(items):
    return [Paragraph(t, BULLET, bulletText="\u2022") for t in items]


def _style(table, colour_map=None):
    base = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(table._cellvalues)):
        if i % 2 == 0:
            base.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f6f8fa")))
    for i, colour in (colour_map or {}).items():
        base.append(("TEXTCOLOR", (2, i), (2, i), colour))
    table.setStyle(TableStyle(base))


def matrix_table():
    data = [[Paragraph("Bereich", HEAD), Paragraph("Funktion", HEAD),
             Paragraph("Stand", HEAD), Paragraph("Anmerkung", HEAD)]]
    colours = {}
    for i, (area, func, state, note) in enumerate(MATRIX, start=1):
        data.append([Paragraph(area, CELL_B), Paragraph(func, CELL_S),
                     Paragraph(state, CELL_B), Paragraph(note, CELL_S)])
        colours[i] = {"umgesetzt": GREEN, "teilweise": AMBER}.get(state, RED)
    table = Table(data, colWidths=[24 * mm, 92 * mm, 20 * mm, 34 * mm], repeatRows=1)
    _style(table, colours)
    return table


def simple_table(rows, widths, head):
    data = [[Paragraph(head[0], HEAD), Paragraph(head[1], HEAD)]]
    data += [[Paragraph(a, CELL_B), Paragraph(b, CELL)] for a, b in rows]
    table = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    _style(table)
    return table


def questions_table():
    data = [[Paragraph("Ansprechpartner", HEAD), Paragraph("Benötigte Angabe", HEAD)]]
    for who, items in QUESTIONS:
        data.append([Paragraph(who, CELL_B),
                     Paragraph("<br/>".join("\u2022 " + q for q in items), CELL)])
    table = Table(data, colWidths=[42 * mm, 128 * mm], repeatRows=1)
    _style(table)
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(20 * mm, 11 * mm,
                      "MAGYC DRINKS GmbH \u00b7 Statusbericht Odoo 20 \u00b7 Stand 10.11.2026")
    canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, str(doc.page))
    canvas.restoreState()


def build(out):
    doc = BaseDocTemplate(out, pagesize=A4, title=TITLE, author=AUTHOR,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=22 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    story = [
        p("MAGYC DRINKS GmbH", H1),
        p("Statusbericht Odoo 20, Projekt S00132. Stand: 10. November 2026.", SUB),

        p("1. Kurzfassung", H2),
        *bullets([
            "Das Kommissionsgeschäft mit Kiosken ist vollständig abgebildet: Kiosk, Vertrag, "
            "Erstbestückung, Nachschub, Abverkauf, Pfand, Rechnung, Rückgabe, Mahnwesen.",
            "Der Soll-Ablauf ist umgesetzt: Steuer und Pfand entstehen beim Abverkauf, "
            "die Verkaufsmenge wird nicht eingetippt, Preise kommen aus der Preisliste.",
            "Neu dazugekommen sind Kiosk-Postfach, Tourplanung, Speditionstransfer, "
            "Liefersperre, Verlustkennzeichen und der DATEV-Export.",
            "Alle Erweiterungen sind automatisiert geprüft: 36 Tests, kein Fehler.",
            "Offen sind ausschließlich Punkte, die Angaben oder Zugänge von MAGYC brauchen, "
            "sowie das Ausrollen auf die Produktivinstanz.",
        ]),

        p("2. Umfang S00132", H2),
        p("Die folgende Matrix zeigt je Funktion den Stand. Umgesetzt heißt: im System vorhanden "
          "und durch Tests oder einen Probelauf belegt. Teilweise heißt: die Funktion steht, "
          "aber ein Wert oder eine Angabe fehlt. Offen heißt: nicht enthalten oder nicht möglich, "
          "weil Zugänge oder Entscheidungen fehlen.", BODY),
        matrix_table(),

        p("3. Mehraufwand gegenüber S00132", H2),
        p("Die folgenden Punkte sind nicht Teil des vereinbarten Umfangs. Sie sind technisch "
          "machbar und können als Change Request beauftragt werden.", BODY),
        simple_table([(a, b) for a, b in EXTRA], [62, 108], ("Thema", "Aufwand und Voraussetzung")),

        p("4. DATEV", H2),
        p("DATEV ist nicht Teil von Odoo 20 in der Community-Version. Die Module der Open Source "
          "Erweiterung l10n-germany lagen nur für Odoo 19 vor und wurden auf 20 portiert. "
          "Der Export ist damit ohne Zusatzlizenz möglich.", BODY),
        *bullets([
            "Paket enthält Buchungsstapel, Debitoren und Kreditoren sowie Kontenbeschriftungen.",
            "Format: CP1252, Semikolon als Trennzeichen, Kopfzeile nach DTVF, Steuer aufgeteilt auf 19 %.",
            "Probelauf auf der Entwicklungsdatenbank mit Platzhaltern erfolgreich, Datei wurde erzeugt.",
            "Für den Echtbetrieb fehlen Berater- und Mandantennummer sowie die Kontenzuordnung von TU Treuhand.",
        ]),
        p("Hinweis: Die Module liegen als eigenes Repository vor, damit die Anpassungen "
          "nachvollziehbar und updatefähig bleiben.", NOTE),

        p("5. Prüfung", H2),
        simple_table([
            ("Erweiterungen Kiosk und Provision", "14 Tests, kein Fehler"),
            ("Soll-Ablauf", "13 Tests, kein Fehler"),
            ("DATEV-Export", "9 Tests, kein Fehler"),
            ("Gesamt", "36 Tests, kein Fehler"),
            ("Probelauf mit Beispieldaten", "Lager Köln, vier Kioske, Lieferungen, Rechnung, DATEV-Paket erzeugt"),
        ], [62, 108], ("Prüfbereich", "Ergebnis")),

        p("6. Deployment", H2),
        p("Die Instanz wird von MAGYC betrieben, ein direkter Serverzugang besteht nicht. "
          "Das Ausrollen erfolgt daher über den Upload der Pakete in der Verwaltungsoberfläche "
          "und einen anschließenden Neustart.", BODY),
        *bullets([
            "Pakete liegen bereit: fünf eigene Module sowie die drei DATEV-Module.",
            "Reihenfolge: Abhängigkeiten zuerst, dann die eigenen Module.",
            "Vor dem Ausrollen: Sicherung der Datenbank und Abstimmung eines Wartungsfensters.",
            "Nach dem Ausrollen: Probelauf Abverkauf und DATEV-Export mit echten Buchungen.",
        ]),

        p("7. Offene Angaben", H2),
        p("Ohne die folgenden Angaben bleiben Konten, Preise und Schnittstellen unvollständig. "
          "Sie sind nach Ansprechpartner gruppiert.", BODY),
        questions_table(),

        p("8. Nächste Schritte", H2),
        *bullets([
            "Angaben aus Abschnitt 7 einsammeln, danach Konten und Preise vervollständigen",
            "DATEV-Probelauf mit echten Buchungen und Freigabe durch TU Treuhand",
            "Wartungsfenster festlegen und Erweiterungen ausrollen",
            "Schulung der Kiosk-Betreuung, danach Übergabe in den Betrieb",
        ]),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "MAGYC-Statusbericht-De.pdf"))
