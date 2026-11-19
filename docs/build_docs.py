# -*- coding: utf-8 -*-
"""Erzeugt die zwei Kunden-PDFs fuer MAGYC DRINKS GmbH (S00132).

  MAGYC-Handbuch-De.pdf          Schritt-fuer-Schritt-Handbuch + Status
  MAGYC-Offene-Angaben-De.pdf    offene Punkte, die Angaben des Kunden brauchen

Aufruf:
  cd docs && uv run --with reportlab python build_docs.py
"""
import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                CondPageBreak, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")

NAVY = colors.HexColor("#0f2b46")
BLUE = colors.HexColor("#2a5d84")
INK = colors.HexColor("#1a1a1a")
GREY = colors.HexColor("#555555")
LINE = colors.HexColor("#d0d7de")
GREEN = colors.HexColor("#1a7f37")
AMBER = colors.HexColor("#9a6700")
RED = colors.HexColor("#b42318")
ZEBRA = colors.HexColor("#f6f8fa")

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["BodyText"], fontName="Helvetica",
                      fontSize=9.6, leading=13.6, textColor=INK,
                      alignment=TA_JUSTIFY, spaceAfter=5)
BODY_L = ParagraphStyle("bodyl", parent=BODY, alignment=TA_LEFT)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                    fontSize=16, leading=20, textColor=NAVY,
                    spaceBefore=10, spaceAfter=8, keepWithNext=1)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    fontSize=11.5, leading=15, textColor=BLUE,
                    spaceBefore=12, spaceAfter=5, keepWithNext=1)
STEP = ParagraphStyle("step", parent=BODY, leftIndent=15, firstLineIndent=-15,
                      spaceAfter=3.2, alignment=TA_LEFT)
BULLET = ParagraphStyle("bullet", parent=STEP, leftIndent=12, firstLineIndent=-8)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.6, leading=9.8,
                       textColor=GREY, alignment=TA_LEFT)
CAP = ParagraphStyle("cap", parent=SMALL, fontSize=7.4, leading=9.2,
                     spaceBefore=2, spaceAfter=8)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.6, leading=11.4,
                      alignment=TA_LEFT, spaceAfter=0)
CELLH = ParagraphStyle("cellh", parent=CELL, fontName="Helvetica-Bold",
                       textColor=colors.white)
PART = ParagraphStyle("part", parent=H1, fontSize=9.5, textColor=GREY,
                      spaceBefore=0, spaceAfter=2)


# Deutsche Rechtschreibung: Wortliste statt genereller Ersetzung, weil
# "Steuern", "neue" oder "Adresse" korrekt sind und nicht angetastet werden duerfen.
DE = {
    "Abverkaeufe": "Abverkäufe", "aelter": "älter", "aelteren": "älteren",
    "aelteste": "älteste", "aenderbar": "änderbar", "aendern": "ändern",
    "aendert": "ändert", "Aenderung": "Änderung", "Aenderungen": "Änderungen",
    "Aenderungswuensche": "Änderungswünsche", "Anhaenge": "Anhänge",
    "Auftragsbestaetigung": "Auftragsbestätigung", "ausfuehren": "ausführen",
    "ausgewaehlt": "ausgewählt", "auswaehlen": "auswählen",
    "beschaedigt": "beschädigt", "beschaedigte": "beschädigte",
    "bestaetigen": "bestätigen", "Bestaetigen": "Bestätigen",
    "Bestaetigt": "Bestätigt", "bestaetigten": "bestätigten",
    "Bestaetigung": "Bestätigung", "Bestueckung": "Bestückung",
    "einschraenken": "einschränken", "Empfaenger": "Empfänger",
    "enthaelt": "enthält", "ergaenzen": "ergänzen", "erklaert": "erklärt",
    "Erklaerung": "Erklärung", "Erstbestueckung": "Erstbestückung",
    "faellig": "fällig", "Faellige": "Fällige", "Farbflaechen": "Farbflächen",
    "fuehren": "führen", "fuellen": "füllen", "fuellt": "füllt", "Fuer": "Für",
    "fuer": "für", "funktionsfaehig": "funktionsfähig", "gefuehrt": "geführt",
    "gefuellt": "gefüllt", "gehoert": "gehört", "geklaert": "geklärt",
    "geklaerte": "geklärte", "geprueft": "geprüft",
    "Geschaeftsfuehrung": "Geschäftsführung", "geschaetzt": "geschätzt",
    "gestuetzte": "gestützte", "Getraenk": "Getränk", "Getraenke": "Getränke",
    "Getraenkeartikel": "Getränkeartikel", "Getraenkepreis": "Getränkepreis",
    "gewaehlten": "gewählten", "gezaehlt": "gezählt", "gezaehlten": "gezählten",
    "gezaehlter": "gezählter", "haeufigste": "häufigste", "heisst": "heißt",
    "hinzufuegen": "hinzufügen", "Hoehe": "Höhe", "kaufmaennische": "kaufmännische",
    "klaeren": "klären", "Koeln": "Köln", "Kuehlschrank": "Kühlschrank",
    "Kuehlschrankreihen": "Kühlschrankreihen", "laesst": "lässt",
    "laeuft": "läuft", "Loeschen": "Löschen", "Marktplaetze": "Marktplätze",
    "Massnahme": "Maßnahme", "Menue": "Menü", "Menueindex": "Menüindex",
    "Menueleiste": "Menüleiste", "Menuepfad": "Menüpfad", "Menuepfade": "Menüpfade",
    "Menues": "Menüs", "moeglich": "möglich", "muessen": "müssen",
    "Nachschuebe": "Nachschübe", "naechste": "nächste", "Naechste": "Nächste",
    "naechsten": "nächsten", "Naechster": "Nächster", "noetig": "nötig",
    "oeffnen": "öffnen", "oeffnet": "öffnet", "Palettenmasse": "Palettenmaße",
    "Pfandruecknahme": "Pfand-Rücknahme", "Pfandruecknahmen": "Pfand-Rücknahmen",
    "Pfandrueckzahlung": "Pfandrückzahlung", "Praemie": "Prämie",
    "Praemien": "Prämien", "pruefen": "prüfen", "Pruefstand": "Prüfstand",
    "prueft": "prüft", "Pruefung": "Prüfung", "Qualitaetssperre": "Qualitätssperre",
    "Rueckgabe": "Rückgabe", "Ruecknahme": "Rücknahme",
    "Sachkontenlaenge": "Sachkontenlänge", "schaetzen": "schätzen",
    "Schaetzwerten": "Schätzwerten", "Schluessel": "Schlüssel",
    "Spaltenueberschrift": "Spaltenüberschrift", "Startpraemie": "Startprämie",
    "Startpraemien": "Startprämien", "Steuersaetze": "Steuersätze",
    "taeglichen": "täglichen", "Tagesgeschaeft": "Tagesgeschäft",
    "tatsaechlichen": "tatsächlichen", "traegt": "trägt", "ueber": "über",
    "Ueberfaellig": "Überfällig", "Uebergabeprotokoll": "Übergabeprotokoll",
    "uebergehen": "übergehen", "uebernehmen": "übernehmen",
    "uebernimmt": "übernimmt", "ueberschreiben": "überschreiben",
    "Uebertrag": "Übertrag", "Untermenue": "Untermenü",
    "unvollstaendig": "unvollständig", "vollstaendige": "vollständige",
    "vorausgefuellter": "vorausgefüllter", "Vorgaenge": "Vorgänge",
    "waehlen": "wählen", "waehrend": "während", "Waehrung": "Währung",
    "wofuer": "wofür", "zaehlen": "zählen", "Zaehlen": "Zählen",
    "Zaehlergebnis": "Zählergebnis", "Zaehlfehler": "Zählfehler",
    "zaehlt": "zählt", "Zaehlung": "Zählung", "Zaehlwert": "Zählwert",
    "Zugaenge": "Zugänge", "zugehoerigen": "zugehörigen", "zurueck": "zurück",
    "Zurueck": "Zurück", "zurueckbuchen": "zurückbuchen",
    "zurueckkommt": "zurückkommt", "Zuruecknehmen": "Zurücknehmen",
    "Einbahnstrassen": "Einbahnstraßen", "Schwarzweiss": "Schwarzweiß",
}
WORD = __import__("re").compile(r"\b(" + "|".join(DE) + r")\b")


class DeParagraph(Paragraph):
    """Paragraph, der die Wortliste anwendet, damit Umlaute korrekt stehen."""

    def __init__(self, text, *a, **kw):
        super().__init__(WORD.sub(lambda m: DE[m.group(1)], text), *a, **kw)


Paragraph = DeParagraph  # alle Aufrufe unten nutzen die Wortliste


def de(t):
    return WORD.sub(lambda m: DE[m.group(1)], t)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text, story, style=BODY):
    story.append(Paragraph(text, style))


def steps(items, story):
    for i, t in enumerate(items, 1):
        story.append(Paragraph("<b>%d.</b> %s" % (i, t), STEP))
    story.append(Spacer(1, 3))


def bullets(items, story):
    for t in items:
        story.append(Paragraph("\u2022 %s" % t, BULLET))
    story.append(Spacer(1, 3))


def note(text, kind, story):
    col = {"info": BLUE, "warn": AMBER, "ok": GREEN, "stop": RED}[kind]
    bg = {"info": colors.HexColor("#eef4fa"), "warn": colors.HexColor("#fdf6e3"),
          "ok": colors.HexColor("#eef7f0"), "stop": colors.HexColor("#fdeceb")}[kind]
    t = Table([[Paragraph(text, BODY_L)]], colWidths=[168 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, col),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Spacer(1, 4))
    story.append(KeepTogether([t]))
    story.append(Spacer(1, 10))


def table(header, rows, widths, story):
    data = [[Paragraph(esc(h), CELLH) for h in header]]
    for r in rows:
        data.append([Paragraph(esc(str(c)), CELL) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(style))
    story.append(Spacer(1, 3))
    story.append(t)
    story.append(Spacer(1, 12))


def fig(name, caption, story):
    """Bild nur einhaengen, wenn es existiert und nicht leer ist."""
    path = os.path.join(SHOTS, "de", name)
    if not os.path.exists(path) or os.path.getsize(path) < 8000:
        return
    img = Image(path)
    ratio = img.imageHeight / float(img.imageWidth) if img.imageWidth else 0.6
    img.drawWidth = 168 * mm
    img.drawHeight = 168 * mm * ratio
    if img.drawHeight > 72 * mm:
        img.drawHeight = 72 * mm
        img.drawWidth = 72 * mm / ratio
    story.append(KeepTogether([img, Paragraph(esc(caption), CAP)]))


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 52 * mm, A4[0], 52 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 23)
    canvas.drawString(22 * mm, A4[1] - 28 * mm, "MAGYC DRINKS GmbH")
    canvas.setFont("Helvetica", 11.5)
    canvas.drawString(22 * mm, A4[1] - 37 * mm, doc.title_line)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(22 * mm, A4[1] - 45 * mm, doc.subtitle_line)
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(22 * mm, 14 * mm, "Projekt S00132, Stand 19.11.2026")
    canvas.restoreState()


def page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(22 * mm, A4[1] - 16 * mm, A4[0] - 22 * mm, A4[1] - 16 * mm)
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(22 * mm, A4[1] - 13 * mm, "MAGYC DRINKS GmbH, " + doc.title_line)
    canvas.line(22 * mm, 15 * mm, A4[0] - 22 * mm, 15 * mm)
    canvas.drawString(22 * mm, 10 * mm, "Projekt S00132, Stand 19.11.2026")
    canvas.drawRightString(A4[0] - 22 * mm, 10 * mm, "Seite %d" % doc.page)
    canvas.restoreState()


def build(path, title_line, subtitle_line, story):
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=21 * mm, rightMargin=21 * mm,
                          topMargin=21 * mm, bottomMargin=19 * mm,
                          title=title_line, author="PassForm Digital")
    doc.title_line = de(title_line)
    doc.subtitle_line = de(subtitle_line)
    fc = Frame(21 * mm, 19 * mm, A4[0] - 42 * mm, A4[1] - 78 * mm, id="cover")
    fb = Frame(21 * mm, 19 * mm, A4[0] - 42 * mm, A4[1] - 44 * mm, id="body")
    doc.addPageTemplates([PageTemplate(id="Cover", frames=[fc], onPage=cover),
                          PageTemplate(id="Body", frames=[fb], onPage=page)])
    doc.build(story)
    print("wrote", path)


def manual():
    s = []
    para("<b>Handbuch</b>", s, ParagraphStyle("ct", parent=BODY, fontName="Helvetica-Bold",
                                            fontSize=12, textColor=NAVY, spaceAfter=10))
    para("Anleitung fuer den taeglichen Betrieb, die Einrichtung, den Monatsabschluss "
         "und die Fehlerbehebung. Jedes Kapitel beschreibt einen Arbeitsgang so, dass "
         "eine Person ohne Vorkenntnisse ihn ausfuehren kann: Menuepfad, Feld, Wert, "
         "Ergebnis, Kontrolle.", s)
    para("Grundlage sind das Vertriebs- und Lieferkonzept vom 09.11.2026 und die "
         "Onboarding-Unterlagen vom 29.10.2026. Der Soll-Ablauf hat Vorrang vor "
         "aelteren Beschreibungen.", s)
    note("<b>So liest man dieses Handbuch.</b> Menuepfade stehen als "
         "<b>Magyc &gt; Kioske</b>. Werte, die eingetippt oder ausgewaehlt werden, "
         "stehen in <b>Fettdruck</b>. Jeder Arbeitsgang endet mit einer Kontrolle. "
         "Kapitel 27 sagt, was zu tun ist, wenn eine Kontrolle nicht stimmt.", "info", s)
    para("Inhalt in Kurzform:", s)
    table(["Teil", "Kapitel", "Inhalt"],
          [["A", "1 bis 5", "Grundlagen: Ablauf, Rollen, Datenmodell, Bedienung"],
           ["B", "6 bis 12", "Einrichtung: Firma, Artikel, Lager, Kioske, Benutzer, Texte"],
           ["C", "13 bis 23", "Tagesgeschaeft: Postfach, Bestueckung, Tour, Abverkauf, Pfand, Rechnung"],
           ["D", "24 bis 26", "Abschluss: Tagescheck, Monatsabschluss, DATEV, Auswertungen"],
           ["E", "27 bis 30", "Betrieb: Fehlerbehebung, Pruefstand, Funktionsmatrix, Ausblick"]],
          [14 * mm, 24 * mm, 130 * mm], s)
    s.append(NextPageTemplate("Body"))
    s.append(PageBreak())

    s.append(Paragraph("Teil A. Grundlagen", PART))

    para("1. Wozu dieses Handbuch da ist", s, H1)
    para("MAGYC stellt Getraenke in Kiosken im Kommissionsverfahren bereit. Das "
         "Unternehmen liefert, der Kiosk verkauft, MAGYC rechnet den verkauften Anteil "
         "ab. Odoo bildet diesen Ablauf ab: Bestand, Kioskstammdaten, Abverkauf, Pfand, "
         "Rechnung, Buchhaltung und DATEV-Export.", s)
    bullets(["Die Geschaeftsfuehrung, die den Ablauf versteht und Auswertungen liest.",
             "Die Lagerleitung, die Lieferungen, Touren und Abverkauf bucht.",
             "Die Buchhaltung, die Rechnungen prueft und den Monatsabschluss macht."], s)
    para("Das Handbuch ist kein Lehrbuch zu Odoo. Wo Standardfunktionen verwendet "
         "werden, steht der Menuepfad und was dort zu tun ist.", s)

    para("2. Der Soll-Ablauf in acht Schritten", s, H1)
    table(["Nr.", "Schritt", "Wer", "Wo in Odoo", "Ergebnis"],
          [["1", "Bewerbung eines Kiosks kommt an", "Akquisiteur, Kiosk", "Magyc > Kiosk-Postfach", "Vorgang mit Status Neu"],
           ["2", "Kiosk anlegen, Vertrag kommt zurueck", "Innendienst", "Magyc > Kioske", "Kontakt mit Kundentyp Kiosk"],
           ["3", "Erstbestueckung liefern", "Fahrer", "Magyc > Nachschub / Erstbestueckung", "Ware im Kommissionslager"],
           ["4", "Tour planen und fahren", "Lagerleitung, Fahrer", "Magyc > Touren", "Stopps in Reihenfolge, Lieferscheine"],
           ["5", "Abverkauf zaehlen und buchen", "Aussendienst", "Magyc > Abverkauf Kiosk", "Menge, Differenz, Rechnung mit Pfand"],
           ["6", "Pfand kommt zurueck", "Kiosk, Innendienst", "Magyc > Pfand-Ruecknahme", "Gutschrift"],
           ["7", "Ware kommt beschaedigt zurueck", "Lager", "Lager > Scrap", "Bestand korrigiert, Verlust markiert"],
           ["8", "Monatsabschluss und DATEV", "Buchhaltung", "Buchhaltung > DATEV DTVF Export", "Exportdateien fuer die Kanzlei"]],
          [9 * mm, 42 * mm, 26 * mm, 46 * mm, 45 * mm], s)
    note("<b>Wichtig.</b> Der Abverkauf wird nie geschaetzt und nie frei eingetippt. Er "
         "entsteht aus dem gezaehlten Bestand im Kiosk. Umsatzsteuer und Pfand entstehen "
         "erst beim Abverkauf, nicht bei der Lieferung. Deshalb erfolgt die Lieferung an "
         "den Kiosk ohne Rechnung.", "stop", s)

    para("3. Rollen und Rechte", s, H1)
    para("Jede Person bekommt eine eigene Anmeldung. Geteilte Konten sind nicht "
         "vorgesehen, weil sonst im Verlauf nicht erkennbar ist, wer gebucht hat.", s)
    table(["Rolle", "Personen", "darf", "darf nicht"],
          [["Geschaeftsfuehrung", "2", "alles, Freigabe Schadensverlust, Sperrdaten setzen", "nichts einschraenken"],
           ["Lagerleitung", "1", "Touren, Lieferungen, Abverkauf, Pfand, Stammdaten", "Buchhaltung sperren"],
           ["Aussendienst (SSM)", "1", "Abverkauf erfassen, eigene Kioske sehen", "Preise aendern, Rechnungen stornieren"],
           ["Fahrer", "2", "eigene Tour sehen, Lieferschein drucken", "Abverkauf buchen, Preise sehen"],
           ["Akquisiteur", "extern", "keine Anmeldung, Provision wird gepflegt", "Anmeldung"]],
          [30 * mm, 18 * mm, 66 * mm, 54 * mm], s)
    para("Rechte werden ueber Gruppen gesteuert: <b>Einstellungen &gt; Benutzer &amp; "
         "Unternehmen &gt; Benutzer</b>, Feld <b>Zugriffsrechte</b>. Wer Lager buchen "
         "soll, braucht <b>Lagerung / Administrator</b>. Wer nur lesen soll, bekommt "
         "<b>Lagerung / Benutzer</b>.", s)

    para("4. Datenmodell ohne Technik", s, H1)
    table(["Begriff", "Was es in Odoo ist", "Woran man es erkennt"],
          [["Kiosk", "Kontakt (res.partner) mit Kundentyp Kiosk", "Kiosk-ID, Kiosk-Status, Gebiet"],
           ["Kommissionslager", "Lagerort beim Kiosk, Ware gehoert MAGYC", "Lagerort heisst wie der Kiosk"],
           ["Abverkauf", "eigener Vorgang mit Positionen je Artikel", "Entwurf, Pruefung, Bestaetigt, Abgerechnet"],
           ["Charge", "Los mit Mindesthaltbarkeitsdatum", "MHD steuert die Auswahl beim Liefern"]],
          [30 * mm, 66 * mm, 72 * mm], s)
    para("FEFO heisst: die Charge mit dem naechsten MHD wird zuerst ausgeliefert. Odoo "
         "macht das beim Reservieren automatisch, wenn die Charge ein Ablaufdatum hat. "
         "Deshalb ist das MHD beim Wareneingang Pflicht.", s)
    para("Pfand ist ein eigener Artikel mit eigenem Preis. Er wird nicht in den "
         "Getraenkepreis eingerechnet, sondern als separate Rechnungsposition gefuehrt. "
         "Dadurch bleibt die Pfandrueckzahlung nachvollziehbar.", s)

    para("5. Anmelden und bedienen", s, H1)
    para("5.1 Anmelden", s, H2)
    steps(["Adresse im Browser oeffnen: <b>https://magyc.cloudpepper.site</b>.",
           "E-Mail und Passwort eingeben, <b>Anmelden</b>.",
           "Oben rechts Avatar, <b>Einstellungen</b>, Sprache <b>Deutsch</b>, Zeitzone "
           "<b>Europe/Berlin</b>.",
           "Kontrolle: Die Menueleiste zeigt die Apps, in der Mitte steht <b>Magyc</b>."], s)
    para("5.2 Die vier Bedienelemente", s, H2)
    bullets(["<b>App-Menue</b> oben links: Wechsel zwischen Buchhaltung, Lager, Kontakte, Magyc.",
             "<b>Untermenue</b> in der Leiste: die Kapitel der gewaehlten App.",
             "<b>Suchleiste</b> mit Filter, etwa <i>Status = Aktiv</i> oder <i>Gebiet = Berlin</i>.",
             "<b>Chatter</b> rechts im Datensatz: Verlauf, Notizen, Anhaenge."], s)
    para("5.3 Listen bedienen", s, H2)
    steps(["Auf eine Spaltenueberschrift klicken, um zu sortieren.",
           "Filter-Symbol rechts oben: <b>Status = Aktiv</b> oder <b>Gebiet = Berlin</b>.",
           "Drei Punkte je Zeile: Aktionen wie <b>Loeschen</b> oder <b>Duplizieren</b>.",
           "Unten <b>Exportieren</b> liefert CSV fuer Excel. Spalten vorher auswaehlen."], s)
    note("Aenderungen werden sofort gespeichert. Es gibt keinen Speichern-Knopf. Wer "
         "einen Wert versehentlich aendert, korrigiert ihn sofort, sonst steht die "
         "falsche Zahl im Verlauf.", "info", s)

    s.append(CondPageBreak(70 * mm))
    s.append(Spacer(1, 8))
    s.append(Paragraph("Teil B. Einrichtung", PART))

    para("6. Firma, Steuern und Kontenrahmen", s, H1)
    para("Diese Einrichtung ist einmalig und bereits erfolgt. Die Schritte dienen der "
         "Pruefung und der Einrichtung einer neuen Gesellschaft.", s)
    steps(["<b>Einstellungen &gt; Unternehmen &gt; Unternehmen bearbeiten</b>.",
           "Name <b>MAGYC DRINKS GmbH</b>, Anschrift Berlin, USt-IdNr. eintragen.",
           "<b>Kontenrahmen</b> pruefen: <b>SKR04</b>. Waehrung <b>EUR</b>.",
           "<b>Buchhaltung &gt; Konfiguration &gt; Steuern</b>: 19 und 7 Prozent, je "
           "Satz Konto und DATEV-Schluessel.",
           "Kontrolle: <b>Kontenplan</b> zeigt 1312 Konten, Feld <b>DATEV-Konto</b> ist "
           "gefuellt."], s)
    note("Der Kontenrahmen laesst sich nach dem ersten gebuchten Beleg nicht mehr "
         "wechseln. Vor der ersten Rechnung pruefen.", "warn", s)

    para("7. Artikel und Preise", s, H1)
    para("7.1 Getraenkeartikel anlegen", s, H2)
    steps(["<b>Lager &gt; Artikel &gt; Artikel</b>, <b>Neu</b>.",
           "<b>Artikelbezeichnung</b>: zum Beispiel <b>Lemon Zero 0,33 l</b>.",
           "<b>Verkaufspreis</b> aus der Preislage, nicht schaetzen.",
           "<b>Steuern (Verkauf)</b>: 19 Prozent, bei Lebensmitteln der passende Satz.",
           "Reiter <b>Bestand</b>: <b>Verfolgung</b> auf <b>Charge</b>. Ohne "
           "Chargenverfolgung funktioniert FEFO nicht.",
           "Reiter <b>Lager</b>: <b>MHD erforderlich</b> aktivieren.",
           "Kontrolle: Der Artikel steht in der Liste mit Preis und Verfolgung Charge."], s)
    note("Ein Artikel ohne Chargenverfolgung wird beim Liefern nicht nach MHD sortiert. "
         "Das ist der haeufigste Einrichtungsfehler.", "warn", s)
    para("7.2 Pfandartikel anlegen", s, H2)
    steps(["<b>Lager &gt; Artikel</b>, <b>Neu</b>, Bezeichnung <b>Pfand 0,25 EUR</b>.",
           "Typ <b>Dienstleistung</b>, damit kein Lagerbestand entsteht.",
           "<b>Verkaufspreis 0,25</b>, Steuern wie beim Getraenk.",
           "Kontrolle: Der Artikel wird beim Abverkauf als eigene Zeile vorgeschlagen."], s)
    para("7.3 Preislage pflegen", s, H2)
    steps(["<b>Verkauf &gt; Konfiguration &gt; Preislagen</b>, Preislage <b>Kiosk</b>.",
           "Je Artikel eine Zeile mit <b>Mindestmenge 1</b> und Netto-Preis.",
           "Kontrolle: Im Abverkauf ist der Preis ausgegraut und nicht aenderbar."], s)
    para("Der Abverkauf uebernimmt den Preis aus der Preislage. Wer einen Preis aendern "
         "will, aendert ihn dort. Damit ist ausgeschlossen, dass zwei Kioske "
         "unterschiedliche Preise bekommen, ohne dass es jemand merkt.", s)

    para("8. Lager, Fahrzeuglager und Chargen", s, H1)
    steps(["<b>Lager &gt; Konfiguration &gt; Lager</b>: <b>BER</b> und <b>KOE</b> "
           "pruefen, Anschrift steht am zugehoerigen Kontakt.",
           "Je Fahrer ein <b>Fahrzeuglager</b>: <b>Neu</b>, Name <b>Fahrzeug 1</b>, "
           "Lagerort <b>Fahrzeug 1</b>.",
           "Kontrolle: <b>Lager &gt; Berichte &gt; Bestand</b> zeigt das Fahrzeuglager "
           "als eigene Zeile."], s)
    para("Das Fahrzeuglager ist noetig, weil Ware waehrend der Tour im Auto liegt. Wird "
         "sie direkt vom Hauptlager gebucht, stimmt der Bestand nicht mehr, sobald ein "
         "Kiosk nicht beliefert wird.", s)
    para("8.1 Wareneingang mit MHD und Stellplatz", s, H2)
    steps(["<b>Einkauf &gt; Bestellung</b> bestaetigen. <b>Lager &gt; Vorgaenge &gt; Wareneingang</b> oeffnen, "
           "<b>Wareneingang buchen</b> klicken.",
           "Je Position <b>Charge neu</b>, <b>MHD</b>, <b>Menge</b> und <b>Stellplatz</b> eintragen. "
           "Vorbelegt ist das Quarantaenelager oder das erste freie Fach. Eine Position darf auf "
           "mehrere Zeilen mit je einer Charge aufgeteilt werden.",
           "<b>Buchen</b>. Optional vorher <b>Etiketten drucken</b> mit Anzahl waehlen.",
           "Kontrolle: <b>Lager &gt; Berichte &gt; Bestand</b> zeigt Menge, Charge, MHD und "
           "Stellplatz in einer Zeile."], s)
    para("8.2 Zonen und Stellplaetze", s, H2)
    para("Das Lager ist in fuenf Zonen geteilt. Jede Zone ist ein Lagerort mit Feld <b>Lagerzone</b>.", s)
    table(["Zone", "Zweck", "Regel"],
          [["Allgemeinlager", "885 Stellplaetze im Muster R08-01-20 (Regal, Fach, Hoehe)", "Einlagerung, Reserve"],
           ["Quarantaenelager", "gesperrte oder abgelaufene Ware", "keine Auslieferung"],
           ["Pickzone", "je Artikel ein Pickplatz, z. B. PICK-MAG-LEM-250", "einzige Quelle fuer Kundenlieferungen"],
           ["Kundenlager", "Ware beim Kunden", "Kommission"],
           ["Verbrauchslager", "Material und Verpackung", "Abschreibung ohne Wert"]],
          [34 * mm, 80 * mm, 54 * mm], s)
    para("Der Stellplatzcode ist zugleich der Barcode. Das Regal R03 hat oberhalb von Platz 27 "
         "nur Hoehe 10. Die Plaetze legt die Installation einmalig an.", s)
    para("8.3 Etiketten drucken", s, H2)
    steps(["<b>Lager &gt; Etiketten drucken</b>, Zone waehlen, Anzahl eintragen (0 = alle) oder Plaetze auswaehlen.",
           "<b>Drucken</b>. Jedes Etikett zeigt Code und Strichcode (Code128).",
           "Kontrolle: Scan des Etiketts in der Lager-Barcode-App oeffnet den Stellplatz."], s)
    para("8.4 Umlagerung von Fach zu Fach", s, H2)
    steps(["<b>Lager &gt; Umlagerung</b>.",
           "<b>Von Stellplatz</b>, <b>Auf Stellplatz</b>, <b>Artikel</b>, <b>Menge</b> eintragen.",
           "<b>Umlagern</b>. Der Vorgang bucht einen internen Transfer und erledigt ihn sofort.",
           "Kontrolle: Bestand der beiden Plaetze unter <b>Lager &gt; Berichte &gt; Bestand</b>."], s)
    note("Der Scanner ist nicht angebunden. Die Codes werden getippt oder ueber die "
         "Barcode-App gescannt.", "warn", s)
    para("8.5 Regeln, die das System erzwingt", s, H2)
    bullets(["<b>FEFO</b>: die Ware mit dem fruehesten MHD wird zuerst reserviert (Kategorie Getraenke).",
             "<b>Pickzone</b>: Kundenlieferungen werden nur aus der Pickzone kommissioniert, sonst Fehler mit Hinweis auf Umlagerung. Kiosk-Kommission ist ausgenommen.",
             "<b>Abgelaufene Chargen</b> duerfen nicht an Kunden gehen. Ein taeglicher Lauf verschiebt sie in die Quarantaene.",
             "<b>Tray-Pruefung</b>: Anzahl Trays mal 24 muss der gelieferten Dosenzahl entsprechen.",
             "<b>Verpackung</b>: Dose 0,35 kg, Tray 24er 8,4 kg (40 x 27 x 13 cm), Europalette 25 kg (120 x 80 x 15 cm)."], s)
    para("8.6 Rollen im Lager", s, H2)
    table(["Rolle", "Darf"],
          [["MAGYC Warehouse", "Wareneingang, Umlagerung, Etiketten, Quarantaene"],
           ["MAGYC Driver", "Lieferung und Uebergabe, keine Abrechnung"],
           ["MAGYC Store Success Manager", "Zaehlung, Nachschub anfordern"]],
          [60 * mm, 108 * mm], s)
    para("8.7 Verbrauch abschreiben und Pfandrueckstellung", s, H2)
    para("Verbrauchsmaterial wird in das Verbrauchslager gebucht und ist damit ohne Wert aus dem "
         "Bestand. Die Pfandrueckstellung bucht den nicht zurueckgenommenen Teil netto auf Konto "
         "3071 gegen 4000. Beispiel: 1000 Dosen, 500 zurueck, 125,00 EUR brutto offen, Rueckstellung "
         "105,04 EUR netto. Pfand in Verkehr bucht brutto auf 4401, die USt entsteht ueber das Automatikkonto.", s)

    para("9. Kioskstammdaten", s, H1)
    para("Ein Kiosk ist ein Kontakt mit Kundentyp Kiosk. Alle kioskspezifischen Felder "
         "stehen im Reiter <b>Magyc</b>.", s)
    steps(["<b>Magyc &gt; Kioske</b>, <b>Neu</b>.",
           "<b>Name</b>: zum Beispiel <b>Kiosk am Kottbusser Tor</b>.",
           "<b>Kundentyp</b>: <b>Kiosk (Kommission)</b>. Ohne diesen Wert erscheint "
           "der Kontakt nicht in der Kioskliste.",
           "Anschrift, Telefon, E-Mail. Diese Daten stehen auf Lieferschein und Rechnung.",
           "<b>Kiosk-ID</b>: Schema <b>K-BER-0056</b>, wird mit Vertrag vergeben.",
           "<b>Gebiet</b>: <b>Berlin</b> oder <b>Koeln</b>. Steuert die Tour.",
           "<b>Kiosk-Status</b>: mit <b>Interessent</b> beginnen, siehe Kapitel 14.",
           "<b>GLN Kiosk</b> und <b>IBAN Kiosk</b> fuellen, wenn vorhanden.",
           "Kontrolle: Der Kiosk steht in <b>Magyc &gt; Kioske</b> mit Status und Gebiet."], s)
    table(["Feld", "Bedeutung", "Regel"],
          [["Kundentyp", "Art des Kontakts", "Kiosk, B2B oder Onlineshop, steuert Preise und Belege"],
           ["Kiosk-Status", "Fortschritt", "Interessent, Vertrag eingegangen, Erstbestueckung geplant, Aktiv, Inaktiv"],
           ["Liefersperre ignorieren", "Ausnahme von der Sperre", "Nur GF setzt das, Standard aus"],
           ["Provision je Kiosk", "Akquisiteursprovision", "50 EUR netto monatlich, Kapitel 12"],
           ["Startpraemie", "Status der Praemie", "Offen oder Ausgezahlt, mit Datum"]],
          [34 * mm, 54 * mm, 80 * mm], s)

    para("10. Benutzer, Gruppen und Postfach-Alias", s, H1)
    steps(["<b>Einstellungen &gt; Benutzer &gt; Benutzer</b>, <b>Neu</b>.",
           "Name, E-Mail, dann <b>Zugriffsrechte</b> nach Kapitel 3.",
           "Passwort setzen, Person bittet um Aenderung beim ersten Anmelden.",
           "Kontrolle: Die Person sieht genau die Menues ihrer Rolle."], s)
    para("10.1 Postfach-Alias einrichten", s, H2)
    steps(["<b>Einstellungen &gt; Technisch &gt; Eingehende Mailserver</b>: Server, "
           "Port, Benutzer, Passwort des Postfachs.",
           "<b>Alias-Domains</b>: <b>magyc.cloudpepper.site</b> eintragen.",
           "<b>Magyc &gt; Kiosk-Postfach</b>: Spalte <b>Alias</b> wird je Vorgang "
           "automatisch erzeugt.",
           "Testmail senden. Kontrolle: neuer Vorgang mit Status <b>Neu</b> binnen "
           "einer Minute."], s)
    note("Ohne eingehenden Mailserver bleibt das Postfach leer. Bewerbungen kommen dann "
         "per Telefon und werden manuell erfasst.", "warn", s)

    para("11. Belegtexte", s, H1)
    steps(["<b>Magyc &gt; Belegtexte</b>, <b>Neu</b>.",
           "<b>Belegtyp</b> waehlen, zum Beispiel <b>Rechnung Kiosk (Abverkauf)</b>.",
           "<b>Einleitungstext</b> und <b>Schlusstext</b> fuellen, Formatierung erlaubt.",
           "Kontrolle: Eine neue Rechnung des Typs zeigt beide Texte."], s)
    table(["Belegtyp", "Verwendung"],
          [["Angebot (B2B)", "Angebote an gewerbliche Kunden"],
           ["Auftragsbestaetigung", "Bestaetigung eines B2B-Auftrags"],
           ["Rechnung B2B", "Rechnung an B2B-Kunden"],
           ["Rechnung Kiosk (Abverkauf)", "Monatsrechnung aus dem Abverkauf"],
           ["Rechnung Onlineshop", "Rechnung an Endkunden"],
           ["Gutschrift / Storno", "Pfandruecknahme und Korrekturen"],
           ["Lieferschein", "Begleitpapier der Lieferung"]],
          [52 * mm, 116 * mm], s)

    para("12. Provision und Startpraemie", s, H1)
    steps(["<b>Magyc &gt; Startpraemien</b> zeigt Kioske mit Status <b>Offen</b>.",
           "<b>Provision je Kiosk</b> pruefen: 50 EUR netto monatlich.",
           "Nach Auszahlung Status <b>Ausgezahlt</b> und Datum setzen.",
           "Kontrolle: Der Kiosk verschwindet aus der Liste der offenen Praemien."], s)

    s.append(CondPageBreak(70 * mm))
    s.append(Spacer(1, 8))
    s.append(Paragraph("Teil C. Tagesgeschaeft", PART))

    para("13. Bewerbung im Kiosk-Postfach bearbeiten", s, H1)
    steps(["<b>Magyc &gt; Kiosk-Postfach</b> oeffnen.",
           "Zeile mit Status <b>Neu</b> anklicken. Rechts die Nachricht, unten Anhaenge.",
           "Anschrift und Telefon in die Felder uebernehmen, falls sie fehlen.",
           "Passt der Standort: Knopf <b>Kiosk anlegen</b>. Es oeffnet sich ein "
           "vorausgefuellter Kontakt.",
           "Im Kontakt <b>Kundentyp</b> auf <b>Kiosk (Kommission)</b>, <b>Kiosk-Status</b> "
           "auf <b>Vertrag eingegangen</b>, <b>Gebiet</b> waehlen, speichern.",
           "Zurueck im Postfach: Status <b>Kiosk angelegt</b>.",
           "Passt der Standort nicht: Status <b>Abgelehnt</b> und Grund als Notiz."], s)
    note("Es entsteht kein Kiosk automatisch. Bewusst ein Klick, damit niemand "
         "versehentlich Dubletten anlegt.", "info", s)
    para("Kontrolle: Der Kiosk steht in <b>Magyc &gt; Kioske</b> mit Status <b>Vertrag "
         "eingegangen</b>, der Postfachvorgang auf <b>Kiosk angelegt</b>.", s)

    para("14. Kiosk anlegen und Vertrag fuehren", s, H1)
    table(["Status", "Bedeutung", "Naechster Schritt"],
          [["Interessent", "Kontakt besteht, Vertrag fehlt", "Vertrag senden, nachfassen"],
           ["Vertrag eingegangen", "unterschriebener Vertrag liegt vor", "Erstbestueckung planen"],
           ["Erstbestueckung geplant", "Lieferung eingeplant", "Liefern, dann auf Aktiv"],
           ["Aktiv", "Kiosk wird beliefert und abgerechnet", "Tour, Abverkauf, Rechnung"],
           ["Inaktiv", "keine Belieferung", "Grund notieren, Ware zurueckbuchen"]],
          [40 * mm, 62 * mm, 66 * mm], s)
    steps(["<b>Magyc &gt; Kioske</b>, Kiosk oeffnen.",
           "Reiter <b>Magyc</b>: Status auf den naechsten Wert setzen.",
           "Vertrag als PDF ueber den Chatter hochladen.",
           "Notiz mit Datum und Ansprechpartner eintragen.",
           "Kontrolle: Status passt zum tatsaechlichen Stand, Vertrag ist sichtbar."], s)

    para("15. Erstbestueckung buchen", s, H1)
    steps(["<b>Magyc &gt; Nachschub / Erstbestueckung</b>, <b>Neu</b>.",
           "<b>Kiosk</b> waehlen.",
           "<b>Modus</b>: <b>Erstbestueckung</b>.",
           "<b>Fahrzeuglager</b>: Lager des Fahrers.",
           "<b>Trays Lemon</b> und <b>Trays Berry</b>: Anzahl. Ein Tray enthaelt 24 Dosen.",
           "<b>Bestaetigen</b>. Odoo legt die Lieferung an und reserviert die Charge mit "
           "dem naechsten MHD.",
           "Lieferung oeffnen, <b>Validieren</b>.",
           "Kiosk-Status auf <b>Aktiv</b>."], s)
    table(["Feld", "Wert", "Bedeutung"],
          [["Modus", "Erstbestueckung", "Erstlieferung ohne Mindestmenge"],
           ["Trays Lemon", "ganze Zahl", "Trays Lemon Zero, mal 24 Dosen"],
           ["Trays Berry", "ganze Zahl", "Trays Berry Zero, mal 24 Dosen"],
           ["Mindestmenge Nachschub", "nur Nachschub", "Warnschwelle, Kapitel 16"],
           ["Fahrzeuglager", "Lager des Fahrers", "Quelle der Ware"]],
          [38 * mm, 40 * mm, 90 * mm], s)
    note("Kontrolle: <b>Lager &gt; Berichte &gt; Bestand</b> zeigt die Menge im "
         "Kommissionslager, das Hauptlager ist um dieselbe Menge kleiner. Stimmt das "
         "nicht, wurde die Lieferung nicht validiert.", "ok", s)

    para("16. Nachschub buchen", s, H1)
    steps(["<b>Magyc &gt; Nachschub / Erstbestueckung</b>, <b>Neu</b>.",
           "Kiosk waehlen, Modus <b>Nachschub</b>.",
           "<b>Mindestmenge Nachschub (Trays)</b>: liegt der Bestand darunter, ist "
           "Nachschub faellig.",
           "Trays Lemon und Berry eintragen, <b>Bestaetigen</b>, Lieferung validieren.",
           "Kontrolle: Bestand im Kommissionslager steigt um die gelieferte Menge."], s)

    para("17. Tour planen und fahren", s, H1)
    steps(["<b>Magyc &gt; Touren</b>, <b>Neu</b>.",
           "<b>Name</b>: zum Beispiel <b>Tour Berlin Nord</b>.",
           "<b>Datum</b>, <b>Fahrer</b>, <b>Fahrzeuglager</b>, <b>Gebiet</b> setzen.",
           "Reiter <b>Stopps</b>: Kioske hinzufuegen. Reihenfolge nach Postleitzahl, "
           "dann Name.",
           "Speichern. <b>Anzahl Stopps</b> zeigt die Summe.",
           "Lieferscheine: Stopp oeffnen, <b>Drucken &gt; Lieferschein</b>.",
           "Nach der Tour je Kiosk den Abverkauf buchen, Kapitel 18."], s)
    note("Die Reihenfolge laesst sich je Stopp ueber <b>Stop-Reihenfolge</b> "
         "ueberschreiben, in Zehnerschritten. Gedacht fuer Baustellen und "
         "Einbahnstrassen.", "info", s)

    para("18. Abverkauf erfassen und abrechnen", s, H1)
    para("18.1 Zaehlen und erfassen", s, H2)
    steps(["<b>Magyc &gt; Abverkauf Kiosk</b>, <b>Neu</b>.",
           "<b>Kiosk</b> waehlen, <b>Zeitraum von</b> und <b>Zeitraum bis</b> setzen.",
           "<b>Positionen laden</b>. Odoo fuellt je Artikel <b>Bestand laut System</b>, "
           "<b>Gezählt (SSM)</b> und <b>Abverkauf</b>.",
           "<b>Gezählt (SSM)</b> je Artikel mit dem gezaehlten Bestand im Kuehlschrank "
           "fuellen. Nichts anderes eintippen.",
           "Odoo rechnet <b>Abverkauf = Bestand laut System minus gezaehlt</b>. Der Wert "
           "ist nicht editierbar.",
           "<b>Rueckgabe (Stk)</b> fuellen, wenn Ware zurueckkommt. Die <b>Differenz</b> "
           "erscheint automatisch.",
           "<b>Kuehlschrankreihen</b>, <b>Platzierung ok</b> und Foto im Reiter "
           "<b>Platzierung</b>.",
           "Speichern. Bei Differenz wechselt der Status auf <b>Pruefung Differenz</b>."], s)
    table(["Feld", "Herkunft", "Regel"],
          [["Bestand laut System", "Odoo", "Bestand im Kommissionslager am Zeitraumbeginn"],
           ["Gezählt (SSM)", "Eingabe", "Zaehlergebnis im Kiosk, Pflicht"],
           ["Abverkauf (Stk)", "berechnet", "System minus gezaehlt, nicht editierbar"],
           ["Rueckgabe (Stk)", "Eingabe", "nur wenn Ware physisch zurueckkommt"],
           ["Differenz", "berechnet", "Abverkauf plus Rueckgabe minus System"],
           ["Preis netto", "Preislage", "nicht editierbar"]],
          [40 * mm, 30 * mm, 98 * mm], s)
    para("18.2 Differenz klaeren", s, H2)
    steps(["Vorgang mit Status <b>Pruefung Differenz</b> oeffnen.",
           "Ursache pruefen: Zaehlfehler, Schwund, nicht gebuchte Rueckgabe.",
           "Notiz mit Ergebnis eintragen, <b>Differenz geklaert</b> setzen.",
           "<b>Bestaetigen</b>. Status <b>Bestaetigt</b>.",
           "Kontrolle: <b>Differenz gesamt</b> steht fest, Rechnung im naechsten Schritt."], s)
    note("Ohne <b>Differenz geklaert</b> laesst sich nicht bestaetigen. Absicht: keine "
         "Rechnung ohne Erklaerung.", "warn", s)
    para("18.3 Rechnung erzeugen", s, H2)
    steps(["Im bestaetigten Abverkauf <b>Rechnung erzeugen</b>.",
           "Odoo legt die Rechnung an: Getraenke netto, Umsatzsteuer, Pfand als eigene "
           "Zeile.",
           "Status <b>Abgerechnet</b>, Feld <b>Rechnung</b> verweist auf den Beleg.",
           "Rechnung pruefen unter <b>Buchhaltung &gt; Kunden &gt; Rechnungen</b>, dann "
           "<b>Bestaetigen</b>.",
           "Kontrolle: Rechnungsbetrag gleich Abverkaufswert plus Pfand."], s)

    para("19. Pfandruecknahme", s, H1)
    steps(["<b>Magyc &gt; Pfand-Ruecknahme</b>, <b>Neu</b>.",
           "<b>Kunde / Kiosk</b> und <b>Datum</b> setzen.",
           "Position: <b>Pfandartikel</b>, <b>Menge (Stk)</b>, Preis aus dem Artikel.",
           "<b>Bestaetigen</b>. Odoo erzeugt eine <b>Gutschrift</b>.",
           "Kontrolle: <b>Gutschrift</b> gefuellt, Status <b>Abgerechnet</b>, Betrag "
           "netto gleich Menge mal Pfand."], s)
    note("Die Pfandruecknahme senkt den offenen Posten des Kiosks. Sie ist keine "
         "Ausgabe und kein Verlust.", "info", s)

    para("20. Rueckgabe und Qualitaetssperre", s, H1)
    table(["Marke", "Bedeutung", "Freigabe"],
          [["RAN/MUSTER", "Muster oder Ansichtsexemplar", "Lagerleitung"],
           ["RAN/SCHADEN", "beschaedigte Ware", "Geschaeftsfuehrung"]],
          [30 * mm, 70 * mm, 68 * mm], s)
    steps(["<b>Lager &gt; Vorgaenge &gt; Scrap</b>, <b>Neu</b>.",
           "Artikel, Menge und <b>Quelle</b> (Kommissionslager oder Fahrzeug) waehlen.",
           "<b>Verlustmarke</b>: <b>RAN/MUSTER</b> oder <b>RAN/SCHADEN</b>.",
           "Bei <b>RAN/SCHADEN</b> traegt Odoo die Freigabe der Geschaeftsfuehrung ein. "
           "Ohne diese Rolle laesst sich nicht speichern.",
           "Kontrolle: Bestand sinkt, Vorgang steht in der Verlustliste."], s)
    note("Scrap ist unumkehrbar. Bei Vertippern ist eine Korrekturbuchung noetig. Vor "
         "dem Speichern Menge und Quelle pruefen.", "stop", s)

    para("21. Speditionstransfer", s, H1)
    steps(["<b>Magyc &gt; Speditionstransfer</b>, <b>Neu</b>.",
           "<b>Quelle</b> und <b>Ziel</b> waehlen (BER nach KOE oder umgekehrt).",
           "<b>Paletten</b>: Anzahl. <b>Trays je Palette</b> bleibt auf dem Standardwert, "
           "solange die Spedition nichts anderes meldet.",
           "<b>Speditionsreferenz</b>: Sendungsnummer.",
           "<b>Bestaetigen</b>, erzeugte Lieferung <b>Validieren</b>.",
           "Kontrolle: Bestand im Ziellager steigt um Paletten mal Trays mal 24 Dosen."], s)

    para("22. Belegtexte verwenden und drucken", s, H1)
    steps(["Beleg oeffnen, zum Beispiel eine Rechnung.",
           "<b>Drucken</b>, Vorlage <b>Rechnung</b> waehlen.",
           "Kontrolle: Einleitung und Schlusstext des passenden Belegtyps stehen im PDF."], s)
    para("Die Vorlagen bleiben ohne Rahmen und Farbflaechen auch in Schwarzweiss "
         "lesbar. Wichtig fuer Versand per Fax und Ablage bei der Kanzlei.", s)

    para("23. Zahlungen, Mahnwesen und Sperren", s, H1)
    steps(["<b>Buchhaltung &gt; Kunden &gt; Rechnungen</b>: offene Rechnungen sind rot.",
           "Zahlung: Rechnung oeffnen, <b>Zahlung registrieren</b>, Datum und Betrag "
           "pruefen.",
           "Mahnung: Filter <b>Ueberfaellig</b>, dann <b>Mahnung senden</b>.",
           "Kiosk sperren: Feld <b>Liefersperre</b> im Kiosk setzen, naechste Lieferung "
           "wird blockiert.",
           "Kontrolle: Der Kiosk erscheint nicht mehr in der Tourenauswahl, bis die "
           "Sperre aufgehoben ist."], s)
    note("Die Liefersperre ist ein Hinweis, kein technisches Verbot. Die GF kann sie je "
         "Kiosk mit <b>Liefersperre ignorieren</b> uebergehen. Jede Ausnahme steht "
         "danach im Verlauf.", "warn", s)

    s.append(CondPageBreak(70 * mm))
    s.append(Spacer(1, 8))
    s.append(Paragraph("Teil D. Abschluss und Auswertung", PART))

    para("24. Tagesabschluss in zehn Minuten", s, H1)
    bullets(["Alle Touren des Tages stehen auf <b>Erledigt</b>.",
             "Alle Abverkaeufe sind <b>Bestaetigt</b> oder <b>Abgerechnet</b>.",
             "Keine Lieferung steht auf <b>Entwurf</b>.",
             "Kein Postfachvorgang ist aelter als zwei Tage und noch <b>Neu</b>.",
             "Kein Scrap ohne Verlustmarke.",
             "Fahrzeuglager leer oder Bestand erklaert."], s)

    para("25. Monatsabschluss und DATEV-Export", s, H1)
    para("25.1 Vorbereiten", s, H2)
    steps(["Alle Abverkaeufe des Monats bestaetigen und Rechnungen erzeugen.",
           "Alle Pfandruecknahmen bestaetigen.",
           "Alle Rechnungen pruefen und bestaetigen.",
           "Kontrolle: <b>Buchhaltung &gt; Berichte &gt; Bilanz</b> laeuft ohne Warnung."], s)
    para("25.2 Export erzeugen", s, H2)
    steps(["<b>Buchhaltung &gt; Buchhaltung &gt; DATEV DTVF Export</b> oeffnen.",
           "<b>Neu</b>, Zeitraum erster bis letzter Tag des Monats.",
           "<b>Beraternummer</b> und <b>Mandantennummer</b> aus den Offenen Angaben, "
           "<b>Sachkontenlaenge</b> 4.",
           "<b>Export erzeugen</b>.",
           "Drei Dateien herunterladen: Buchungsstapel, Debitoren/Kreditoren, "
           "Kontenbeschriftungen.",
           "Kontrolle: Dateinamen beginnen mit <b>EXTF_</b>, Summe im Buchungsstapel "
           "gleich Summe der Journalposten des Monats."], s)
    table(["Datei", "Inhalt", "Empfaenger"],
          [["EXTF_Buchungsstapel_*.csv", "alle Buchungen des Zeitraums", "Kanzlei, Import in DATEV"],
           ["EXTF_DebKred_Stamm.csv", "Kontenstamm Debitoren und Kreditoren", "Kanzlei, einmalig"],
           ["EXTF_Kontenbeschriftungen.csv", "Sachkontenbezeichnungen", "Kanzlei, einmalig"]],
          [54 * mm, 62 * mm, 52 * mm], s)
    para("25.3 Sperren", s, H2)
    steps(["<b>Buchhaltung &gt; Buchhaltung &gt; Sperrdaten</b> oeffnen.",
           "Sperrdatum auf den letzten Tag des abgeschlossenen Monats setzen.",
           "Kontrolle: Buchungen davor sind nicht mehr aenderbar."], s)
    note("Das Sperrdatum erst setzen, wenn die Kanzlei den Export geprueft hat. "
         "Zuruecknehmen kann es nur die Geschaeftsfuehrung.", "stop", s)

    para("26. Auswertungen lesen", s, H1)
    table(["Frage", "Wo", "Filter"],
          [["Umsatz je Kiosk im Monat", "Buchhaltung > Berichte > Rechnungsanalyse", "Zeitraum, Kundentyp Kiosk"],
           ["Abverkauf je Artikel", "Magyc > Abverkauf Kiosk", "Zeitraum, nach Artikel gruppieren"],
           ["Differenzen je Kiosk", "Magyc > Abverkauf Kiosk", "Status Pruefung Differenz oder Differenz gesamt ungleich 0"],
           ["Bestand je Kiosk", "Lager > Berichte > Bestand", "Lagerort des Kiosks"],
           ["Faellige Nachschuebe", "Magyc > Kioske", "Bestand kleiner Mindestmenge"],
           ["Offene Startpraemien", "Magyc > Startpraemien", "Status Offen"]],
          [44 * mm, 62 * mm, 62 * mm], s)
    para("Fuer den Versand an Dritte die Liste ueber <b>Exportieren</b> als CSV ausgeben. "
         "Spalten vorher auswaehlen: Kiosk, Zeitraum, Menge, Betrag.", s)

    s.append(CondPageBreak(70 * mm))
    s.append(Spacer(1, 8))
    s.append(Paragraph("Teil E. Betrieb", PART))

    para("27. Fehlerbehebung", s, H1)
    para("Erst pruefen, dann handeln. Die meisten Meldungen haben eine der Ursachen in "
         "dieser Tabelle.", s)
    table(["Beobachtung", "Ursache", "Massnahme"],
          [["Kiosk fehlt in der Kioskliste", "Kundentyp nicht gesetzt", "Kontakt oeffnen, Kundentyp Kiosk (Kommission) setzen"],
           ["Abverkauf bleibt leer", "Gezählt (SSM) fehlt", "Zaehlwert eintragen, speichern"],
           ["Bestaetigen nicht moeglich", "Differenz nicht geklaert", "Differenz geklaert setzen, Notiz ergaenzen"],
           ["Lieferung nicht validierbar", "Kein Bestand oder Charge fehlt", "Wareneingang pruefen, Charge mit MHD anlegen"],
           ["Falsche Charge geliefert", "Artikel ohne Chargenverfolgung", "Verfolgung auf Charge stellen, neu reservieren"],
           ["Rechnung ohne Pfandzeile", "Pfandartikel fehlt in der Preislage", "Preislage Kiosk ergaenzen"],
           ["Postfach bleibt leer", "Mailserver oder Alias fehlt", "Kapitel 10.1, Testmail senden"],
           ["Keine Berechtigung", "Gruppe fehlt", "Benutzer, Zugriffsrechte pruefen"],
           ["Scrap nicht speicherbar", "RAN/SCHADEN ohne GF-Rolle", "GF bucht oder erteilt Freigabe"],
           ["DATEV-Export leer", "Zeitraum falsch oder keine Buchungen", "Zeitraum pruefen, Buchungen bestaetigen"]],
          [44 * mm, 48 * mm, 76 * mm], s)
    para("Steht die Meldung nicht in der Tabelle: Bildschirmfoto, Uhrzeit und letzten "
         "Arbeitsschritt notieren und an PassForm Digital geben. Diese drei Angaben "
         "reichen in der Regel, um die Ursache im Protokoll zu finden.", s)

    para("28. Pruefstand", s, H1)
    para("Das System ist mit 36 automatischen Tests geprueft, die bei jeder Aenderung "
         "erneut laufen.", s)
    table(["Bereich", "Tests", "Ergebnis"],
          [["Kommission, Abverkauf, Pfand, Tour (magyc_commission, magyc_ops)", "27", "bestanden"],
           ["DATEV-Export DTVF (datev_export, datev_export_dtvf)", "9", "bestanden"]],
          [110 * mm, 26 * mm, 32 * mm], s)
    bullets(["Abverkauf erzeugt Rechnung mit korrekter Steuer und Pfandzeile.",
             "Abverkauf ohne geklaerte Differenz laesst sich nicht bestaetigen.",
             "FEFO liefert die Charge mit dem naechsten MHD zuerst.",
             "Pfandruecknahme erzeugt Gutschrift in Hoehe Menge mal Pfand.",
             "Erstbestueckung und Nachschub buchen auf das Kommissionslager.",
             "Tourauswahl sortiert nach Postleitzahl, dann Name.",
             "DATEV-Export schreibt drei Dateien mit EXTF-Kopf."], s)

    para("29. Funktionsmatrix S00132", s, H1)
    table(["Enthalten", "Mehraufwand"],
          [["SKR04 einrichten, Steuersaetze, Preislagen", "DPG-Clearing nach Paragraf 17 UStG"],
           ["Kioskstammdaten, Vertrag, Statuskette", "Logik fuer 24-Dosen-Gebinde-Uebertrag"],
           ["Erstbestueckung und Nachschub", "Liefersperre mit Ausnahmen je Kiosk"],
           ["Uebergabeprotokoll, Abverkauf mit FEFO", "Pfandruecknahme-Ausnahme beim Kiosk"],
           ["Pfand auf der Abverkaufsrechnung", "KI-gestuetzte Mailerfassung"],
           ["Qualitaetssperre und Rueckgabe", "Fahrer-App"],
           ["Kommissionierliste, Mahntexte", "Anbindung Speditionen und Shop"],
           ["Touren, Akquisiteurprovision", "Lager Koeln ueber Platzhalter hinaus"],
           ["Lagerzonen, 885 Stellplaetze, Etiketten, FEFO", "Scanner-Hardware, Labeldrucker-Anbindung"],
           ["DATEV-Export", ""]],
          [84 * mm, 84 * mm], s)

    para("30. Naechste Schritte", s, H1)
    steps(["Offene Angaben liefern (separates Dokument), zuerst die Kanzlei: Berater- "
           "und Mandantennummer, Konten fuer Pfand und DPG.",
           "Testkiosk anlegen und einen Monat durchbuchen: Erstbestueckung, zwei "
           "Abverkaeufe, eine Pfandruecknahme, DATEV-Export.",
           "Entscheidung der Kanzlei: Kontenrahmen SKR03 oder SKR04 (siehe Offene Angaben, Punkt 1).",
           "Benutzer anlegen: zwei GF, Lagerleitung, ein SSM, zwei Fahrer.",
           "Schulung von 90 Minuten anhand dieses Handbuchs, danach zwei Wochen "
           "Begleitung im Tagesgeschaeft.",
           "Produktivsetzung, danach monatlicher Abschluss nach Kapitel 25."], s)

    s.append(CondPageBreak(90 * mm))
    para("Anhang. Begriffe und Menueindex", s, H1)
    table(["Begriff", "Bedeutung"],
          [["Kommission", "Ware bleibt Eigentum von MAGYC, bis der Kiosk sie verkauft"],
           ["Abverkauf", "gezaehlter Verkauf eines Zeitraums, Grundlage der Rechnung"],
           ["Differenz", "Abweichung zwischen Systembestand und Zaehlung"],
           ["FEFO", "First Expired First Out, aelteste Charge zuerst"],
           ["MHD", "Mindesthaltbarkeitsdatum der Charge"],
           ["Tray", "Gebinde mit 24 Dosen"],
           ["SSM", "Aussendienstmitarbeiter, zaehlt im Kiosk"],
           ["Sperrdatum", "Buchhaltungssperre, verhindert Aenderungen"]],
          [34 * mm, 134 * mm], s)
    table(["Menue", "Kapitel"],
          [["Magyc > Kiosk-Postfach", "13"],
           ["Magyc > Kioske", "9, 14"],
           ["Magyc > Nachschub / Erstbestueckung", "15, 16"],
           ["Magyc > Touren", "17"],
           ["Magyc > Abverkauf Kiosk", "18"],
           ["Magyc > Pfand-Ruecknahme", "19"],
           ["Magyc > Speditionstransfer", "21"],
           ["Magyc > Startpraemien", "12"],
           ["Magyc > Belegtexte", "11"],
           ["Buchhaltung > DATEV DTVF Export", "25"],
           ["Lager > Scrap", "20"],
           ["Lager > Wareneingang, Umlagerung, Etiketten", "8.1 bis 8.4"],
           ["Lager > Berichte > Bestand", "15, 26"]],
          [84 * mm, 84 * mm], s)
    illustrated(s)
    para("Ende des Handbuchs. Aenderungswuensche an PassForm Digital, Projekt S00132.", s, SMALL)
    return s


def illustrated(s):
    """Bildanleitung: je Screenshot Titel, Einleitung, Bild mit roten Markierungen, nummerierte Legende."""
    f = os.path.join(SHOTS, "shots.json")
    if not os.path.exists(f):
        return
    s.append(PageBreak())
    head = [Paragraph("<b>Bildanleitung: Einstellungen und Bedienung Schritt für Schritt</b>", H1),
            Paragraph("Jedes Bild zeigt den echten Bildschirm. Rote Rahmen mit Nummer zeigen, wo geklickt oder "
                      "eingetragen wird. Die Legende unter dem Bild nennt die Reihenfolge.", BODY)]
    for i, sh in enumerate(json.load(open(f, encoding="utf-8")), 1):
        block = head + [Paragraph("<b>%d. %s</b>" % (i, sh["title"]), H2), Paragraph(sh["intro"], BODY)]
        head = []
        story_before = len(s)
        fig(sh["file"], "", block)
        rows = [[str(n), t] for n, t in sh["legend"]]
        if rows:
            t = Table([[Paragraph("<b>%s</b>" % a, BODY), Paragraph(b_, BODY)] for a, b_ in rows], colWidths=[10 * mm, 158 * mm])
            t.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#dc2626")),
                                   ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINE),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            block.append(t)
        s.append(KeepTogether(block))
        s.append(Spacer(1, 10))


def open_items():
    s = []
    para("<b>Offene Angaben</b>", s, ParagraphStyle("ot", parent=BODY, fontName="Helvetica-Bold",
                                                  fontSize=12, textColor=NAVY, spaceAfter=10))
    para("Diese Liste enthaelt alles, was das System von MAGYC braucht und noch nicht "
         "vorliegt. Jede Zeile nennt, wofuer die Angabe gebraucht wird und was solange "
         "nicht funktioniert. Die Reihenfolge ist eine Empfehlung.", s)
    table(["Nr.", "Angabe", "Wer", "wofuer", "was solange nicht geht"],
          [["1", "Kontenrahmen: Mandant nutzt SKR04, System laeuft auf SKR03. Entscheidung und Umstellung", "TU Treuhand", "Pfand- und Steuerkonten nach Schreiben vom 13.11.", "Konten 4401, 3071, 4000, 3806 sind angelegt, aber im SKR03-Rahmen"],
           ["2", "Bestaetigung DPG-Clearing: eigene Konten oder gebuendelt mit Pfand", "TU Treuhand", "Clearing DPG", "Clearing nur ueber die Pfandkonten"],
           ["3", "DATEV-Schluessel je Sachkonto", "TU Treuhand", "Kontenbeschriftung", "Kanzlei wusste nicht, was gemeint ist, Rueckfrage noetig"],
           ["4", "USt-IdNr. und Steuernummer", "MAGYC", "Rechnungskopf", "Rechnungen ohne vollstaendige Pflichtangaben"],
           ["5", "IBAN und Bankverbindung", "MAGYC", "Rechnung, Zahlungsabgleich", "Zahlungen manuell zuordnen"],
           ["6", "Einkaufspreise je Artikel", "MAGYC", "Wareneingang, Marge", "Marge nicht auswertbar"],
           ["7", "Anschrift Lager Koeln-Rodenkirchen", "MAGYC", "Lager KOE, Lieferscheine", "Platzhalteranschrift in Belegen"],
           ["8", "Regalplan je Kiosktyp", "MAGYC", "Platzierung, Kuehlschrankreihen", "Platzierung nur als Freitext und Foto"],
           ["9", "Preislisten B2B und Onlineshop", "MAGYC", "Preislagen", "nur Kioskpreise gepflegt"],
           ["10", "Eine echte Flixcheck-Mail", "MAGYC", "Felder der Kiosk-Mail zuordnen", "Postfach legt Kiosk nach Standardfeldern an"],
           ["11", "Eingehende Mail (Catch-all) auf der Testumgebung", "MAGYC", "Test des Kiosk-Postfachs", "Postfach nur lokal getestet"],
           ["12", "Zugaenge DSV, UPS, DPD, DHL, Shopify, Marktplaetze", "MAGYC", "Versandetiketten, Shop", "Etikettenaufruf meldet fehlende Zugangsdaten, Belege manuell"]],
          [9 * mm, 40 * mm, 20 * mm, 34 * mm, 65 * mm], s)
    note("<b>Was trotzdem laeuft.</b> Kioskverwaltung, Erstbestueckung, Nachschub, "
         "Touren, Abverkauf, Pfand, Rueckgabe, Lagerzonen, Stellplaetze und DATEV-Export sind "
         "funktionsfaehig. Ohne die Angaben oben fehlen Pflichtangaben auf Belegen, die "
         "kaufmaennische Bewertung und die Anbindung an Dritte.", "ok", s)
    para("<b>Empfohlene Reihenfolge.</b> Zuerst die Punkte 1 bis 3 bei der Kanzlei, weil "
         "sie den Monatsabschluss blockieren. Danach 5 bis 7 von MAGYC, weil sie auf "
         "jedem Beleg stehen. Die Punkte 8 bis 12 sind Ausbaustufen und blockieren den "
         "Start nicht.", s)
    return s


if __name__ == "__main__":
    build(os.path.join(HERE, "MAGYC-Handbuch-De.pdf"),
          "Handbuch und Status", "Anleitung fuer den taeglichen Betrieb", manual())
    build(os.path.join(HERE, "MAGYC-Offene-Angaben-De.pdf"),
          "Offene Angaben", "Was MAGYC liefern muss, damit alles laeuft", open_items())
