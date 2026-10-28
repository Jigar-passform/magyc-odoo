"""Build the MAGYC Odoo 20 implementation summary PDF (EN + DE)."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                               PageTemplate, Paragraph, Spacer)

AUTHOR = "PassForm Digital"
TITLE = "MAGYC DRINKS GmbH - Odoo 20 Implementation Summary"

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=12.4,
                      spaceAfter=2, textColor=colors.HexColor("#1a1a1a"))
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2,
                        bulletFontName="Helvetica", bulletFontSize=9.2, spaceAfter=1)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=15, leading=19,
                    spaceBefore=6, spaceAfter=8, textColor=colors.HexColor("#0f2b46"))
H3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.2, leading=13.5,
                    spaceBefore=6, spaceAfter=3, textColor=colors.HexColor("#2a5d84"))
TITLE_S = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, leading=28,
                         spaceAfter=4, textColor=colors.HexColor("#0f2b46"))
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                     textColor=colors.HexColor("#555555"), spaceAfter=14)

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
    ("Company and Settings", [
        "Company master data, logo, document header and footer",
        "German language activated; stock features (lots, locations, units, pricelists, signature) "
        "switched on",
    ]),
    ("Integration", [
        "Odoo MCP endpoint connected and verified",
        "RPC API key stored outside the code base; access scopes documented",
    ]),
    ("Development and Verification", [
        "Four custom add-ons: kiosk master data, commission billing, deposit handling, document texts",
        "Handover protocol as a printable PDF report with lots, expiry dates and signature lines",
        "Installed and tested on a local Odoo 20 instance; end-to-end test passed "
        "(stock issue, invoice, deposit line, report)",
        "Source code committed and pushed to the project repository",
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
    ("Firma und Einstellungen", [
        "Firmendaten, Logo, Beleg-Kopf- und Fußzeile",
        "Deutsche Sprache aktiviert; Lagerfunktionen (Chargen, Lagerorte, Maßeinheiten, "
        "Preislisten, Signatur) eingeschaltet",
    ]),
    ("Schnittstellen", [
        "Odoo-MCP-Endpoint verbunden und geprüft",
        "RPC-API-Key außerhalb des Codes hinterlegt; Zugriffs-Scopes dokumentiert",
    ]),
    ("Entwicklung und Verifikation", [
        "Vier eigene Erweiterungen: Kiosk-Stammdaten, Kommissionsabrechnung, Pfandbehandlung, "
        "Belegtexte",
        "Übergabeprotokoll als druckbarer PDF-Report mit Chargen, MHD und Unterschriftszeilen",
        "Auf einer lokalen Odoo-20-Instanz installiert und getestet; Ende-zu-Ende-Test bestanden "
        "(Ausbuchung, Rechnung, Pfandzeile, Report)",
        "Quellcode committet und in das Projekt-Repository gepusht",
    ]),
]

OPEN_DE = [
    "Pfand-Rücknahme und DPG-Clearing (§ 17 UStG) – Kontonummern der Steuerkanzlei offen",
    "Mahnstufen-Texte (Zahlungserinnerung, 1. und 2. Mahnung)",
    "Deployment der Erweiterungen auf die Cloud-Instanz",
    "Offene Stammdaten: USt-IdNr., IBAN, DATEV-Nummern, Einkaufspreise, Gewichte, Adresse Köln, "
    "Regalplan",
]

OPEN_EN = [
    "Deposit returns and clearing (section 17 UStG) – waiting for account numbers from the tax office",
    "Dunning texts (payment reminder, first and second notice)",
    "Deployment of the custom add-ons to the cloud instance",
    "Master data still open: VAT ID, IBAN, DATEV numbers, purchase prices, weights, Cologne address, "
    "rack plan",
]


def bullets(items):
    return [Paragraph(t, BULLET, bulletText="•") for t in items]


def section(blocks):
    flow = []
    for name, items in blocks:
        flow.append(KeepTogether([Paragraph(name, H3)] + bullets(items)))
    return flow


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d0d7de"))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(20 * mm, 11 * mm, "MAGYC DRINKS GmbH  ·  Odoo 20")
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
        Paragraph("Odoo 20 implementation - completed work by application area. "
                  "Status: 28 October 2026.", SUB),
        Paragraph("English", H2),
        *section(EN),
        PageBreak(),
        Paragraph("Deutsch", H2),
        *section(DE),
        Spacer(1, 6),
        KeepTogether([Paragraph("Offene Punkte / Open Items", H2),
                       Paragraph("Deutsch", H3)] + bullets(OPEN_DE)),
        KeepTogether([Paragraph("English", H3)] + bullets(OPEN_EN)),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "MAGYC-Odoo20-Summary.pdf"))
