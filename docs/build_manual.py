"""Erzeugt das deutsche Handbuch inkl. Screenshots und offener Angaben."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

TITLE = "MAGYC DRINKS GmbH \u2013 Odoo 20 Handbuch"
AUTHOR = "PassForm Digital"
SHOTS = "C:/Users/ABC/magyc-odoo/docs/screenshots"

NAVY = colors.HexColor("#0f2b46")
BLUE = colors.HexColor("#2a5d84")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=12.6,
                      spaceAfter=3, textColor=INK)
STEP = ParagraphStyle("step", parent=BODY, leftIndent=14, bulletIndent=0,
                      bulletFontName="Helvetica-Bold", bulletFontSize=9.2, spaceAfter=2)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=2,
                        bulletFontName="Helvetica", bulletFontSize=9.2, spaceAfter=1)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=26,
                    spaceAfter=4, textColor=NAVY)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                    spaceBefore=8, spaceAfter=5, textColor=NAVY)
H3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.4, leading=13.5,
                    spaceBefore=6, spaceAfter=3, textColor=BLUE)
SUB = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                     textColor=GREY, spaceAfter=10)
CAP = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
                     textColor=GREY, spaceBefore=2, spaceAfter=8)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.2, leading=10.6, textColor=INK)
CELL_B = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.2, leading=10.6,
                      textColor=colors.white)

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
    canvas.drawString(20 * mm, 11 * mm, "MAGYC DRINKS GmbH  \u00b7  Odoo 20 Handbuch")
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
        p("Odoo 20 Handbuch: Einrichtung, Abläufe, offene Angaben. Stand: 29. Oktober 2026.", SUB),

        p("1. Zweck und Aufbau", H2),
        p("Dieses Handbuch beschreibt die eingerichteten Abläufe für das Kommissionsgeschäft "
          "mit Kiosken und die eigenen Erweiterungen. Jede Funktion zeigt einen Screenshot mit "
          "rot markierten Feldern; die Nummern entsprechen den Schritten in der Anleitung. "
          "Am Ende stehen die Angaben, die für den Abschluss noch fehlen.", BODY),

        p("2. Kiosk anlegen", H2),
        p("Ein Kiosk ist ein Kontakt mit dem Kundentyp Kiosk. Beim Speichern legt das System "
          "automatisch einen eigenen Kommissionslagerort an, benannt nach der Kiosk-ID.", BODY),
        *steps([
            "Kontakte öffnen und einen neuen Kontakt anlegen.",
            "Reiter MAGYC wählen.",
            "Kiosk-ID nach Schema K-BER-0001 eintragen (Feld 1).",
            "Kundentyp Kiosk (Kommission) wählen (Feld 2).",
            "Kommissionslager wird automatisch erzeugt und angezeigt (Feld 3).",
            "Gebiet und bei Bedarf Akquisiteur und Store Success Manager ergänzen (Feld 4).",
        ]),
        figure(f"{SHOTS}/ann-01-kiosk-kontakt.png",
               "Abbildung 1: Kontakt mit Reiter MAGYC. 1 Kiosk-ID, 2 Kundentyp, "
               "3 automatisch erzeugtes Kommissionslager, 4 Gebiet."),

        p("3. Ware an den Kiosk übergeben", H2),
        p("Die Übergabe erfolgt als Lieferschein vom Lager Rangsdorf an den Kommissionslagerort "
          "des Kiosks. Der Beleg Übergabeprotokoll wird aus dem Lieferschein gedruckt und von "
          "beiden Seiten unterschrieben. Die Ware bleibt Eigentum der MAGYC DRINKS GmbH.", BODY),
        *bullets([
            "Lager, Lieferungen: Lieferschein vom Lager Rangsdorf an den Kommissionslagerort des Kiosks",
            "Beleg drucken: Übergabeprotokoll Kommission, enthält Chargen, MHD und Unterschriften",
            "Bestand bleibt im Kommissionslager, keine Rechnung in diesem Schritt",
        ]),

        p("4. Abverkauf melden und abrechnen", H2),
        p("Monatlich wird je Kiosk eine Abverkaufsmeldung erfasst. Bestätigen bucht den "
          "Abverkauf an den Kunden und Rückgaben zurück ins Lager; erst danach entsteht die "
          "Rechnung über die abverkaufte Menge.", BODY),
        *steps([
            "Kommission, Abverkauf Kiosk, Neu.",
            "Kiosk wählen (Feld 1); das Kommissionslager wird vorbelegt.",
            "Zeitraum von und bis setzen (Felder 2 und 3).",
            "Positionen erfassen: Artikel, Abverkauf, Rückgabe, Preis netto (Feld 4).",
            "Bestätigen: Lagerbuchung Abverkauf und Rückgabe werden erzeugt.",
            "Rechnung erstellen: Rechnung über den Abverkauf wird gebucht.",
        ]),
        figure(f"{SHOTS}/ann-02-kommission-neu.png",
               "Abbildung 2: Neue Abverkaufsmeldung. 1 Kiosk, 2 Zeitraum von, 3 Zeitraum bis, "
               "4 Positionen mit Abverkauf, Rückgabe und Preis."),
        figure(f"{SHOTS}/ann-03-abverkauf-formular.png",
               "Abbildung 3: Abgerechnete Meldung. 1 Drucken (Abverkaufsmeldung), 2 Status, "
               "3 Rechnung und Summen: Abverkauf, Rückgabe, Betrag netto."),
        p("Hinweis: Berechnet wird nur der Abverkauf. Rückgaben mindern die Rechnung nicht, "
          "sondern erhöhen den Lagerbestand wieder.", BODY),

        p("5. Pfand", H2),
        p("Pfand wird als eigene Zeile mit 19 % USt geführt. In Aufträgen ergänzt das System "
          "die Pfandzeile automatisch je Getränkezeile. Zurückgegebenes Leergut wird über die "
          "Pfand-Rücknahme als Gutschrift abgerechnet.", BODY),
        *steps([
            "Firma, Reiter Pfand (MAGYC): Pfand automatisch ergänzen aktivieren und "
            "Pfandartikel PFAND-025 wählen.",
            "Kommission, Pfand-Rücknahme, Neu: Kunde und Datum erfassen.",
            "Position mit Pfandartikel und Menge ergänzen.",
            "Gutschrift erstellen: Beleg wird mit 19 % USt gebucht.",
        ]),
        figure(f"{SHOTS}/ann-04-pfand-gutschrift.png",
               "Abbildung 4: Pfand-Rücknahme. 1 Kunde, 2 erzeugte Gutschrift, 3 Status."),

        p("6. Belegtexte pflegen", H2),
        p("Alle Kopf- und Fußtexte liegen als Datensätze in Odoo. Änderungen wirken sofort auf "
          "die Belege, ohne Anpassung am Code. Rechnungstexte richten sich nach dem Kundentyp.", BODY),
        *bullets([
            "Kommission, Belegtexte: Zeile wählen und Texte ändern",
            "Belegarten: Angebot, Auftragsbestätigung, Lieferschein, Rechnung B2B, Rechnung Kiosk, "
            "Rechnung Onlineshop, Gutschrift",
        ]),
        figure(f"{SHOTS}/raw-05-belegtexte.png",
               "Abbildung 5: Belegtexte je Belegart mit Einleitungs- und Schlusstext."),

        p("7. Mahnwesen", H2),
        p("Drei Stufen sind hinterlegt und mit den freigegebenen Texten verknüpft: "
          "Zahlungserinnerung am Fälligkeitstag, 1. Mahnung nach 7 Tagen, 2. Mahnung nach "
          "weiteren 5 Tagen.", BODY),
        *bullets([
            "Einstellungen, Mahnwesen: Stufen, Verzögerung und Vorlage prüfen",
            "Versand erfolgt über die Zahlungserinnerungen je Kunde",
        ]),
        figure(f"{SHOTS}/raw-06-mahnstufen.png",
               "Abbildung 6: Drei Mahnstufen mit Vorlage je Stufe."),

        p("8. Offene Angaben", H2),
        p("Die folgenden Angaben fehlen in den vorliegenden Unterlagen. Ohne sie können Konten, "
          "Preise und Schnittstellen nicht korrekt abgeschlossen werden.", BODY),
        questions_table(),

        p("9. Nächste Schritte", H2),
        *bullets([
            "Angaben aus Abschnitt 8 einsammeln und im System ergänzen",
            "Pfand-Clearing und Rückzahlungsverpflichtung einrichten, sobald die Konten vorliegen",
            "Erweiterungen auf die Produktivinstanz ausrollen und Kiosk-Betreuung schulen",
        ]),
    ]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "MAGYC-Odoo20-Handbuch.pdf"))
