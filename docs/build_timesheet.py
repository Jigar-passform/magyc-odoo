"""Arbeitszeitnachweis MAGYC - 29.10.2026 (7,0 h)."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

NAVY = colors.HexColor("#0f2b46")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")

H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=24,
                    textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=9.5, leading=13,
                     textColor=GREY, spaceAfter=10)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.4, leading=10.8, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.4, leading=10.8,
                      textColor=colors.white)

ROWS = [
    ("Mahnwesen aufgebaut", "Drei Mahnstufen (Fälligkeit, +7 Tage, +12 Tage) mit deutschen "
     "Vorlagen aus der Belegtexte-Vorlage, Einspielung per Migration, Ablösung der Standardstufen", 1.0),
    ("Kommission: Rückgaben", "Rückgaben werden ins Lager Rangsdorf zurückgebucht, Summen "
     "(Abverkauf, Rückgabe, Betrag netto) am Beleg, neue druckbare Abverkaufsmeldung", 1.2),
    ("Pfand-Rücknahme", "Neues Belegobjekt für Leergut, Erzeugung und Buchung der Gutschrift "
     "mit 19 % USt, Menüeintrag", 1.0),
    ("Stammdaten und Voreinstellungen", "Kiosk-Kontakt legt Kommissionslager automatisch an, "
     "Preislistenregeln Kiosk, Tray-GTINs, Signing-Bonus-Artikel, FEFO-Lagerentnahme aktiviert", 0.8),
    ("Fehlerbehebung Chargen", "Bestätigung schlug bei chargengeführten Artikeln fehl; "
     "FEFO-Allokation über vorhandene Chargen mit Ersatzanlage, Statusbezeichnung korrigiert", 0.8),
    ("Handbuch und Screenshots", "Deutsches Handbuch über alle Abläufe, sechs Aufnahmen, "
     "rot markierte Felder mit Nummerierung, Abgleich der offenen Angaben", 1.7),
    ("Test und Auslieferung", "Ende-zu-Ende-Tests (Abverkauf, Rechnung, Pfand, Mahnstufen), "
     "Bereinigung, Commit und Push, Abstimmung der offenen Punkte", 0.5),
]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(20 * mm, 11 * mm, "MAGYC DRINKS GmbH  \u00b7  Arbeitszeitnachweis 29.10.2026")
    canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, str(doc.page))
    canvas.restoreState()


def build(out):
    doc = BaseDocTemplate(out, pagesize=A4, title="Arbeitszeitnachweis 29.10.2026",
                          author="PassForm Digital", leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=22 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])

    data = [[Paragraph("Leistung", HEAD), Paragraph("Beschreibung", HEAD),
             Paragraph("Stunden", HEAD)]]
    for title, desc, hours in ROWS:
        data.append([Paragraph(title, CELL_B), Paragraph(desc, CELL),
                     Paragraph(("%.1f" % hours).replace(".", ","), CELL)])
    data.append([Paragraph("Summe", CELL_B), Paragraph("", CELL),
                 Paragraph("%.1f" % sum(r[2] for r in ROWS), CELL_B)])

    table = Table(data, colWidths=[45 * mm, 108 * mm, 17 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1), colors.HexColor("#eef2f6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
    ]))

    story = [
        Paragraph("Arbeitszeitnachweis", H1),
        Paragraph("Projekt: MAGYC DRINKS GmbH, Odoo 20 (Auftrag S00132)<br/>"
                  "Tag: 29. Oktober 2026<br/>Erbracht von: PassForm Digital", SUB),
        table,
        Spacer(1, 8),
        Paragraph("Gesamt: 7,0 Stunden. Alle Leistungen sind im Repository "
                  "github.com/Jigar-passform/magyc-odoo dokumentiert (Commits 04deb48 bis 027362b) "
                  "und auf der Testinstanz geprüft.", SUB),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "Arbeitszeitnachweis-2026-10-29.pdf"))
