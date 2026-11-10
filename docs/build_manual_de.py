"""Erzeugt das deutsche Handbuch (Stand 10.11.2026) inkl. Screenshots und offener Angaben."""
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                PageTemplate, Paragraph, Table, TableStyle)

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
NOTE = ParagraphStyle("note", parent=BODY, fontSize=8.8, leading=12, leftIndent=8,
                      textColor=GREY, spaceBefore=3, spaceAfter=6)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=26,
                    spaceAfter=4, textColor=NAVY)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                    spaceBefore=10, spaceAfter=5, textColor=NAVY)
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

MODULES = [
    ("Verkauf", "Kommissionsgeschäft Kiosk, Preislisten, Liefersperre, Belegtexte"),
    ("Fakturierung", "SKR04, Abverkaufsrechnung, Pfandzeile, Mahnwesen, DATEV-Export"),
    ("Lager", "Rangsdorf und Köln, Kommissionslager je Kiosk, Qualitätssperre, Touren"),
    ("Kontakte", "Kiosk-Stammdaten, Statuskette, Akquisiteur, Kiosk-Postfach"),
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


def _styled(data, widths):
    layout = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
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
    layout.setStyle(TableStyle(style))
    return layout


def table(rows, widths, head=("Feld", "Bedeutung")):
    data = [[Paragraph(head[0], HEAD), Paragraph(head[1], HEAD)]]
    data += [[Paragraph(a, CELL_B), Paragraph(b, CELL)] for a, b in rows]
    return _styled(data, widths)


def questions_table():
    data = [[Paragraph("Ansprechpartner", HEAD), Paragraph("Benötigte Angabe", HEAD)]]
    for who, items in QUESTIONS:
        data.append([Paragraph(who, CELL_B),
                     Paragraph("<br/>".join("\u2022 " + q for q in items), CELL)])
    return _styled(data, [42, 128])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(20 * mm, 11 * mm,
                      "MAGYC DRINKS GmbH \u00b7 Odoo 20 Handbuch \u00b7 Stand 10.11.2026")
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
        p("Odoo 20 Handbuch: Einrichtung, Abläufe, offene Angaben. Stand: 10. November 2026.", SUB),

        p("1. Zweck und Aufbau", H2),
        p("Dieses Handbuch beschreibt alle eingerichteten Abläufe für das Kommissionsgeschäft mit "
          "Kiosken, die eigenen Erweiterungen und den DATEV-Export. Jede Funktion nennt den Menüweg "
          "und die Schritte in der Reihenfolge, in der sie im Alltag gebraucht werden. Wo ein "
          "Screenshot vorhanden ist, markieren rote Rahmen und Nummern die Felder aus der Anleitung. "
          "Am Ende stehen die Angaben, die für den Produktivstart noch fehlen.", BODY),
        *bullets([
            "Grundlage der Abläufe: Vertriebs- und Lieferkonzept vom 09.11.2026 sowie der abgestimmte Soll-Ablauf.",
            "Die Ware bleibt bis zum Abverkauf Eigentum der MAGYC DRINKS GmbH (Paragraf 3 Absatz 3 UStG).",
            "Steuer und Pfand entstehen erst beim Abverkauf, nicht bei der Übergabe.",
        ]),

        p("2. Systemüberblick", H2),
        p("Die Erweiterungen liegen in fünf Modulen und nutzen die Standardfunktionen von Odoo 20, "
          "statt sie zu ersetzen. Dadurch bleiben Auswertungen, Buchhaltung und Lagerlogik "
          "updatefähig.", BODY),
        table([(a, b) for a, b in MODULES], [45, 125], ("App-Bereich", "Umfang")),
        p("Menüwege: Kommission für Kioske, Abverkauf, Touren und Belegtexte; Verkauf und Fakturierung "
          "für Aufträge, Rechnungen und Mahnwesen; Lager für Lieferungen und Bestände; "
          "Buchhaltung für DATEV.", NOTE),

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
        p("Der Kiosk-Status wird über Aktionen im Reiter MAGYC geführt und nicht frei gesetzt. "
          "So ist jederzeit erkennbar, ob ein Kiosk nur ein Interessent ist oder bereits beliefert wird.", BODY),
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
          "Der Beleg Übergabeprotokoll wird gedruckt und von beiden Seiten unterschrieben. Die Ware "
          "bleibt Eigentum der MAGYC DRINKS GmbH.", BODY),
        *steps([
            "Kommission, Nachschub / Erstbestückung öffnen.",
            "Kiosk wählen, Art der Lieferung (Erstbestückung oder Nachschub) und Menge in Trays erfassen.",
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
          "für Sonderfälle verfügbar und wird dann bewusst ausgelöst.", NOTE),

        p("9. Rückgaben, Qualitätssperre und Verluste", H2),
        p("Rückgaben aus dem Kiosk gehen nicht direkt zurück in den Verkauf, sondern in die "
          "Qualitätssperre und werden dort geprüft.", BODY),
        *bullets([
            "Bestätigter Abverkauf bucht die Rückgabemenge automatisch in die Qualitätssperre.",
            "Verluste werden über eine Lagerbuchung mit Kennzeichen erfasst: RAN/MUSTER oder RAN/SCHADEN.",
            "RAN/SCHADEN benötigt die Freigabe durch die Lagerleitung, RAN/MUSTER nicht.",
            "Nach sechs Monaten ohne Abverkauf wird die Restware über die sechsmonatige Rücknahme zurückgeholt.",
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
          "monatlich je aktivem Kiosk. Beide Beträge sind in der Firma hinterlegt und werden über "
          "Rechnungen abgerechnet.", BODY),
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
            "Debitoren- und Kreditorennummern werden je Kontakt vergeben, entweder fortlaufend oder manuell.",
            "Der Export ist auf einer Entwicklungsdatenbank mit Platzhalterwerten geprüft, "
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

        p("19. Offene Angaben", H2),
        p("Die folgenden Angaben fehlen in den vorliegenden Unterlagen. Ohne sie können Konten, "
          "Preise und Schnittstellen nicht korrekt abgeschlossen werden.", BODY),
        questions_table(),

        p("20. Nächste Schritte", H2),
        *bullets([
            "Angaben aus Abschnitt 19 einsammeln und im System ergänzen",
            "Pfand-Clearing und Rückzahlungsverpflichtung einrichten, sobald die Konten vorliegen",
            "DATEV-Nummern eintragen und einen Probelauf mit echten Buchungen durchführen",
            "Erweiterungen auf die Produktivinstanz ausrollen und Kiosk-Betreuung schulen",
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


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "MAGYC Handbuch - De.pdf"))
