"""Build the MAGYC Odoo 20 status report PDF (EN + DE, summary + requirements table)."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

AUTHOR = "PassForm Digital"
TITLE = "MAGYC DRINKS GmbH - Odoo 20 Implementation Status"

NAVY = colors.HexColor("#0f2b46")
BLUE = colors.HexColor("#2a5d84")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")
GREEN = colors.HexColor("#1a7f37")
AMBER = colors.HexColor("#9a6700")
RED = colors.HexColor("#b42318")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.0, leading=11.8,
                      spaceAfter=2, textColor=INK)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2,
                        bulletFontName="Helvetica", bulletFontSize=9.0, spaceAfter=1)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=15, leading=19,
                    spaceBefore=6, spaceAfter=8, textColor=NAVY)
H3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.2, leading=13.5,
                    spaceBefore=5, spaceAfter=2, textColor=BLUE)
TITLE_S = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, leading=28,
                         spaceAfter=4, textColor=NAVY)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                     textColor=GREY, spaceAfter=12)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.0, leading=10.2, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.0, leading=10.2,
                      textColor=colors.white)

EN = [
    ("Sales", [
        "Commission process per kiosk: sell-through report, automatic stock issue, monthly invoice",
        "Deposit carried as its own order and invoice line at 19 % VAT",
        "Document texts per document type: offer, order confirmation, delivery slip, invoice B2B, "
        "invoice kiosk, invoice shop, credit note",
        "Three pricelists (Kiosk, B2B, Online shop) and a 14-day payment term",
    ]),
    ("Invoicing", [
        "SKR04 chart of accounts with 1,312 accounts, 19 % output and input VAT",
        "Monthly kiosk invoices generated from the sell-through report and posted automatically",
        "Deposit shown separately at the tax rate of the drink",
    ]),
    ("Inventory", [
        "Warehouse Rangsdorf with 28 locations: goods-in, quality hold, storage and rack slots, "
        "packing, goods-out, samples, damage, Cologne, vehicles, consignment",
        "Lot tracking with expiry dates (FEFO-ready) and GS1 lot barcodes on delivery slips",
        "Package types tray (24 cans) and pallet (120 trays)",
        "Two drinks and one deposit article with confirmed GTINs",
    ]),
    ("Contacts", [
        "Kiosk master data: kiosk ID, customer type, area, canvasser, store success manager, "
        "consignment location",
        "Eleven vendors with their role recorded",
    ]),
]

DE = [
    ("Verkauf", [
        "Kommissionsprozess je Kiosk: Abverkaufsmeldung, automatische Warenausbuchung, Monatsrechnung",
        "Pfand als eigene Auftrags- und Rechnungszeile mit 19 % USt",
        "Belegtexte je Belegtyp: Angebot, Auftragsbestätigung, Lieferschein, Rechnung B2B, "
        "Rechnung Kiosk, Rechnung Onlineshop, Gutschrift",
        "Drei Preislisten (Kiosk, B2B, Onlineshop) und Zahlungsziel 14 Tage",
    ]),
    ("Rechnungswesen", [
        "Kontenrahmen SKR04 mit 1.312 Konten, 19 % Umsatzsteuer und Vorsteuer",
        "Monatliche Kiosk-Rechnungen aus der Abverkaufsmeldung, automatisch gebucht",
        "Pfand getrennt ausgewiesen, mit dem Steuersatz des Getränks",
    ]),
    ("Lager", [
        "Lager Rangsdorf mit 28 Lagerorten: Wareneingang, Qualitätssperre, Lager und Regalplätze, "
        "Packstation, Warenausgang, Muster, Schaden, Köln, Fahrzeuge, Kommission",
        "Chargenführung mit Mindesthaltbarkeitsdatum (FEFO-fähig) und GS1-Chargen-Barcodes auf dem "
        "Lieferschein",
        "Gebindearten Tray (24 Dosen) und Palette (120 Trays)",
        "Zwei Getränke und ein Pfandartikel mit bestätigten GTINs",
    ]),
    ("Kontakte", [
        "Kiosk-Stammdaten: Kiosk-ID, Kundentyp, Gebiet, Akquisiteur, Store Success Manager, "
        "Kommissionslager",
        "Elf Lieferanten mit hinterlegter Rolle",
    ]),
]

REQ_EN = [
    ("1. Company logo on documents", "Logo, report header and footer configured", "done"),
    ("2. Document texts",
     "Per-document intro and closing texts: offer, order confirmation, delivery slip, invoices, "
     "credit note", "done"),
    ("3. Chart of accounts SKR04 / DATEV",
     "SKR04 loaded with 1,312 accounts and 19 % VAT; deposit and asset accounts plus DATEV "
     "numbers still with the tax office", "partly"),
    ("4. Articles",
     "Two drinks and one deposit article with GTINs, lots and expiry dates; purchase price and "
     "weights still open", "partly"),
    ("5. Customer data",
     "Kiosk fields prepared; customer import starts after the first goods receipt", "open"),
    ("6. Supplier data",
     "11 suppliers created with roles; addresses and bank details still open", "partly"),
    ("7. Warehouse structure",
     "Rangsdorf warehouse with 28 locations; rack plan and Cologne address open", "partly"),
    ("8. Commission billing (kiosk)",
     "Sell-through report, automatic stock issue and monthly invoice, tested end to end", "done"),
    ("9. Deposit handling",
     "Own line at 19 % VAT, added per drink line and carried onto invoices; returns and clearing "
     "still open", "partly"),
    ("10. Handover protocol",
     "Printable PDF report with lots, expiry dates and signature lines", "done"),
    ("11. Kiosk master data",
     "Kiosk ID, customer type, area, canvasser, store success manager, consignment location", "done"),
    ("12. Deployment to the live instance",
     "Custom extensions not yet rolled out to the cloud instance", "open"),
]

REQ_DE = [
    ("1. Firmenlogo auf Belegen", "Logo, Beleg-Kopf- und Fußzeile eingerichtet", "done"),
    ("2. Belegtexte",
     "Einleitungs- und Schlusstexte je Belegtyp: Angebot, Auftragsbestätigung, Lieferschein, "
     "Rechnungen, Gutschrift", "done"),
    ("3. Kontenrahmen SKR04 / DATEV",
     "SKR04 mit 1.312 Konten und 19 % USt geladen; Pfand- und Anlagekonten sowie DATEV-Nummern "
     "noch bei der Steuerkanzlei", "partly"),
    ("4. Artikel",
     "Zwei Getränke und ein Pfandartikel mit GTINs, Chargen und MHD; Einkaufspreis und Gewichte "
     "noch offen", "partly"),
    ("5. Kundendaten",
     "Kiosk-Felder vorbereitet; Kundenimport startet nach dem ersten Wareneingang", "open"),
    ("6. Lieferantendaten",
     "11 Lieferanten mit Rolle angelegt; Adressen und Bankdaten noch offen", "partly"),
    ("7. Lagerstruktur",
     "Lager Rangsdorf mit 28 Lagerorten; Regalplan und Adresse Köln offen", "partly"),
    ("8. Kommissionsabrechnung (Kiosk)",
     "Abverkaufsmeldung, automatische Warenausbuchung und Monatsrechnung, Ende-zu-Ende getestet",
     "done"),
    ("9. Pfandbehandlung",
     "Eigene Zeile mit 19 % USt, je Getränkezeile und auf Rechnungen; Rücknahme und Clearing "
     "noch offen", "partly"),
    ("10. Übergabeprotokoll",
     "Druckbarer PDF-Report mit Chargen, MHD und Unterschriftszeilen", "done"),
    ("11. Kiosk-Stammdaten",
     "Kiosk-ID, Kundentyp, Gebiet, Akquisiteur, Store Success Manager, Kommissionslager", "done"),
    ("12. Deployment auf die Live-Instanz",
     "Erweiterungen noch nicht auf die Cloud-Instanz ausgerollt", "open"),
]

STATUS_LABEL = {
    "en": {"done": "Done", "partly": "Partly", "open": "Open"},
    "de": {"done": "Erledigt", "partly": "Teilweise", "open": "Offen"},
}
STATUS_COLOR = {"done": GREEN, "partly": AMBER, "open": RED}


def bullets(items):
    return [Paragraph(t, BULLET, bulletText="\u2022") for t in items]


def section(blocks):
    return [KeepTogether([Paragraph(name, H3)] + bullets(items)) for name, items in blocks]


def requirements_table(rows, lang):
    head = ["Requirement" if lang == "en" else "Anforderung",
            "Progress" if lang == "en" else "Stand", "Status"]
    data = [[Paragraph(h, HEAD) for h in head]]
    for req, progress, status in rows:
        data.append([
            Paragraph(req, CELL_B),
            Paragraph(progress, CELL),
            Paragraph(STATUS_LABEL[lang][status],
                      ParagraphStyle("st", parent=CELL, fontName="Helvetica-Bold",
                                     textColor=STATUS_COLOR[status])),
        ])
    table = Table(data, colWidths=[62 * mm, 87 * mm, 21 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
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
    canvas.drawString(20 * mm, 11 * mm, "MAGYC DRINKS GmbH  \u00b7  Odoo 20")
    canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, str(doc.page))
    canvas.restoreState()


def build(out):
    doc = BaseDocTemplate(out, pagesize=A4, title=TITLE, author=AUTHOR,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=22 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    story = [
        Paragraph("MAGYC DRINKS GmbH", TITLE_S),
        Paragraph("Odoo 20 implementation - completed work and requirement status. "
                  "Status: 28 October 2026.", SUB),
        Paragraph("English", H2),
        *section(EN),
        Spacer(1, 4),
        Paragraph("Requirements and status", H2),
        requirements_table(REQ_EN, "en"),
        PageBreak(),
        Paragraph("Deutsch", H2),
        *section(DE),
        Spacer(1, 4),
        Paragraph("Anforderungen und Status", H2),
        requirements_table(REQ_DE, "de"),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "MAGYC-Odoo20-Status.pdf"))
