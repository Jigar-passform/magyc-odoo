"""Erzeugt die deutsche Dokumentation (Einrichtung + offene Angaben) als PDF."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

TITLE = "MAGYC DRINKS GmbH – Odoo 20 Einrichtung und offene Angaben"
AUTHOR = "PassForm Digital"

NAVY = colors.HexColor("#0f2b46")
BLUE = colors.HexColor("#2a5d84")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=12.6,
                      spaceAfter=3, textColor=INK)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2,
                        bulletFontName="Helvetica", bulletFontSize=9.2, spaceAfter=1)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=26,
                    spaceAfter=4, textColor=NAVY)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                    spaceBefore=10, spaceAfter=6, textColor=NAVY)
H3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.2, leading=13.5,
                    spaceBefore=8, spaceAfter=3, textColor=BLUE)
CAP = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
                     textColor=GREY, spaceBefore=2, spaceAfter=10)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                     textColor=GREY, spaceAfter=10)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.2, leading=10.6, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.2, leading=10.6,
                      textColor=colors.white)

SETUP = [
    ("Firma und Belege", [
        "Firmendaten, Logo, Beleg-Kopf- und Fußzeile nach Freigabevorlage",
        "Belegtexte je Belegart: Angebot, Auftragsbestätigung, Lieferschein, Übergabeprotokoll, "
        "Rechnung Kiosk, Rechnung B2B, Rechnung Onlineshop, Gutschrift",
        "Mahnwesen mit drei Stufen: Zahlungserinnerung, 1. Mahnung, 2. Mahnung",
    ]),
    ("Rechnungswesen", [
        "Kontenrahmen SKR04 mit 1.312 Konten, 19 % Umsatzsteuer und Vorsteuer",
        "Zahlungsziel 14 Tage netto",
        "Pfand als eigene Zeile, 19 % USt, getrennt vom Getränkeerlös",
    ]),
    ("Artikel und Gebinde", [
        "MAGYC Lemon Zero und MAGYC Berry Zero, 0,25 l, mit GTIN, Chargenführung und MHD",
        "Pfand Einweg (DPG) 0,25 EUR als eigener Artikel",
        "Gebinde: Tray 24 Dosen und Europalette 120 Trays, Tray-GTINs je Sorte",
        "Preisliste Kiosk mit 0,75 EUR netto je Dose, FEFO-Lagerentnahme",
    ]),
    ("Lager", [
        "Hauptlager Rangsdorf mit Wareneingang, Qualitätssperre, Lager- und Regalplätze, "
        "Packstation, Warenausgang, Muster, Schaden",
        "Nebenlager Köln, Fahrzeuglager Berlin/Brandenburg und Köln",
        "Kommissionsware je Kiosk als eigener Lagerort, Ware bleibt bis zum Abverkauf Eigentum MAGYC",
    ]),
    ("Kontakte", [
        "Elf Lieferanten mit Rolle (Abfüller, Dosen, Pfandsystem, Steuerkanzlei, Vermietung)",
        "Kiosk-Stammdaten: Kiosk-ID, Kundentyp, Gebiet, Akquisiteur, Store Success Manager, "
        "Kommissionslager",
    ]),
]

MODULES = [
    ("Kiosk-Stammdaten", [
        "Zusatzfelder am Kontakt, Kommissionslager wird beim Anlegen eines Kiosks automatisch erzeugt",
    ]),
    ("Kommissionsabrechnung", [
        "Abverkaufsmeldung je Kiosk und Zeitraum: Abverkauf, Rückgabe, Preis",
        "Bestätigen bucht den Abverkauf an den Kunden und Rückgaben zurück ins Lager",
        "Monatsrechnung wird aus der Meldung erzeugt und gebucht",
        "Übergabeprotokoll und Abverkaufsmeldung als PDF mit Unterschriftszeilen",
    ]),
    ("Pfand", [
        "Pfandzeile wird je Getränkezeile automatisch ergänzt, 19 % USt",
        "Pfand-Rücknahme erzeugt die Gutschrift an den Kiosk",
    ]),
    ("Belegtexte und Mahnwesen", [
        "Texte sind als Datensätze pflegbar, keine Anpassung am Code nötig",
        "Rechnungstext richtet sich nach dem Kundentyp (Kiosk, B2B, Onlineshop)",
    ]),
]

QUESTIONS = [
    ("TU Treuhand", [
        "Kontonummer für Erlöse Pfand 19 % USt?",
        "Kontonummer für Pfanderstattungen und DPG-Clearing nach Paragraf 17 UStG?",
        "Kontonummer und Ansatz für die Pfandrückzahlungsverpflichtung in der Bilanz?",
        "Anlagekonten und Anlagenverzeichnis für Stapler, Packtisch, Kühlschränke, Regale?",
        "DATEV-Berater- und Mandantennummer, Sachkontenlänge, Wirtschaftsjahr?",
        "Bestätigung: Pfand 0,25 EUR netto im Kiosk- und B2B-Geschäft, 0,25 EUR brutto im Shop?",
    ]),
    ("Geschäftsführung und Vertrieb", [
        "B2B-Preislisten: welche Staffeln und Konditionen gelten?",
        "Endkundenpreise im Onlineshop (brutto) je Sorte?",
        "Zahlungsziel B2B: bleiben 14 Tage netto oder abweichend?",
        "Signing Bonus 50 EUR je Kiosk: als Dienstleistung mit 19 % USt korrekt?",
        "Kunden- und Kiosknummern: Schema wie K-BER-0001 bestätigen?",
        "Telefonnummer als Pflichtfeld im Kundenstamm beibehalten?",
    ]),
    ("Eko-Vit / Abfüllung", [
        "Einkaufspreis je Dose für Lemon und Berry?",
        "Rolle der Rechnung von Queen of Beverage (0,27 EUR je Dose Berry)?",
        "Gewichte je Dose, Tray und Palette sowie Palettenmaße?",
        "Ansprechpartner und Lieferadresse für Wareneingang und Buchung?",
    ]),
    ("Vermietung und Ausstattung", [
        "Anschrift des Nebenlagers Köln und Ansprechpartner?",
        "Regalplan Rangsdorf: Reihen, Gänge und Plätze inklusive endgültiger Anzahl?",
        "Kühlschränke von Gastro-Michel: Inventarliste für das Anlagenverzeichnis?",
    ]),
    ("Zugänge und Schnittstellen", [
        "DHL, UPS und DPD: Vertragsnummern und API-Zugänge?",
        "Onlineshop: System, Zugang und Abbildung von Pfand und Steuer?",
        "Marktplätze: welche Kanäle und welche Zugänge?",
        "USt-IdNr. der MAGYC DRINKS GmbH?",
        "Bank: IBAN der Berliner Sparkasse und Termin für die Ablösung von Qonto?",
    ]),
    ("Deployment", [
        "Freigabe, die Erweiterungen auf die Produktivinstanz auszurollen?",
        "Wunschtermin für die Produktivnahme und Schulung der Kiosk-Betreuung?",
    ]),
]


def figure(path, caption, width_mm=165):
    width = width_mm * mm
    return KeepTogether([
        Image(path, width=width, height=width * 900.0 / 1440.0),
        Paragraph(caption, CAP),
    ])

def bullets(items):
    return [Paragraph(t, BULLET, bulletText="\u2022") for t in items]


def blocks(items):
    return [KeepTogether([Paragraph(name, H3)] + bullets(lines)) for name, lines in items]


def questions_table():
    data = [[Paragraph("Ansprechpartner", HEAD), Paragraph("Benötigte Angabe", HEAD)]]
    for who, items in QUESTIONS:
        data.append([Paragraph(who, CELL_B),
                     Paragraph("<br/>".join("\u2022 " + q for q in items), CELL)])
    table = Table(data, colWidths=[42 * mm, 128 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f6f8fa")))
    table.setStyle(TableStyle(style))
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(20 * mm, 11 * mm, "MAGYC DRINKS GmbH  ·  Odoo 20 Dokumentation")
    canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, str(doc.page))
    canvas.restoreState()


def build(out):
    doc = BaseDocTemplate(out, pagesize=A4, title=TITLE, author=AUTHOR,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=22 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    story = [
        Paragraph("MAGYC DRINKS GmbH", H1),
        Paragraph("Odoo 20 – Einrichtung, Abläufe und offene Angaben. Stand: 29. Oktober 2026.", SUB),

        Paragraph("1. Zweck des Dokuments", H2),
        Paragraph("Dieses Dokument beschreibt den eingerichteten Stand des Odoo-Systems und listet die "
                  "Angaben, die für den Abschluss noch fehlen. Die offenen Punkte stehen am Ende, "
                  "geordnet nach Ansprechpartner, damit sie direkt weitergegeben werden können.", BODY),

        Paragraph("2. Einrichtung", H2),
        *blocks(SETUP),

        Paragraph("3. Eigene Erweiterungen", H2),
        *blocks(MODULES),

        Paragraph("4. Abläufe", H2),
        Paragraph("Kommission: Ware wird per Lieferschein und Übergabeprotokoll an den Kiosk "
                  "übergeben und bleibt im Kommissionslager. Monatlich meldet der Kiosk Abverkauf "
                  "und Rückgabe; daraus entstehen Lagerbuchung und Rechnung.", BODY),
        Paragraph("Pfand: Pfand wird auf Angebot, Auftrag und Rechnung als eigene Zeile geführt. "
                  "Zurückgegebene Leergutmengen werden über die Pfand-Rücknahme als Gutschrift "
                  "abgerechnet.", BODY),
        Paragraph("Mahnwesen: Nach Fälligkeit werden Zahlungserinnerung, 1. Mahnung und 2. Mahnung "
                  "mit den freigegebenen Texten erzeugt.", BODY),

        Paragraph("5. Offene Angaben", H2),
        Paragraph("Die folgenden Angaben fehlen in den vorliegenden Unterlagen. Ohne sie können die "
                  "betroffenen Konten, Preise und Schnittstellen nicht korrekt abgeschlossen werden.", BODY),
        Spacer(1, 4),
        questions_table(),

        Paragraph("6. Screenshots", H2),
        Paragraph("Aufnahmen aus der eingerichteten Instanz. Die Dateien liegen im Projektordner "
                  "unter docs/screenshots.", BODY),
        figure("C:/Users/ABC/magyc-odoo/docs/screenshots/01-abverkauf-liste.png",
               "Abbildung 1: Abverkaufsmeldungen je Kiosk mit Status und Rechnung"),
        figure("C:/Users/ABC/magyc-odoo/docs/screenshots/02-abverkauf-formular.png",
               "Abbildung 2: Abverkaufsmeldung mit Zeitraum, Summen, Positionen und Rechnung"),
        figure("C:/Users/ABC/magyc-odoo/docs/screenshots/03-pfand-ruecknahme-liste.png",
               "Abbildung 3: Pfand-Rücknahme mit Gutschrift"),
        figure("C:/Users/ABC/magyc-odoo/docs/screenshots/05-belegtexte.png",
               "Abbildung 4: Belegtexte je Belegart, pflegbar ohne Codeänderung"),
        Paragraph("7. Nächste Schritte", H2),
        *bullets([
            "Angaben aus Abschnitt 5 einsammeln und im System ergänzen",
            "Pfand-Clearing und Rückzahlungsverpflichtung einrichten, sobald die Konten vorliegen",
            "Erweiterungen auf die Produktivinstanz ausrollen und Kiosk-Betreuung schulen",
        ]),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "MAGYC-Odoo20-Dokumentation.pdf"))
