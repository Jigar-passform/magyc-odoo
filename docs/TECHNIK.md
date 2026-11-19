# MAGYC DRINKS – technische Dokumentation (Odoo 20)

Stand: 10.11.2026. Zielgruppe: Entwicklung und Betrieb. Die Anwendersicht steht im Handbuch
(`MAGYC-Handbuch-De.pdf`), der Projektstand im Statusbericht (`MAGYC-Statusbericht-De.pdf`).

## 1. Voraussetzungen

| Punkt | Wert |
| --- | --- |
| Odoo | 20.0 (lokal `D:\Program Files\Odoo\20`, DB `magyc_dev`) |
| Python | mitgeliefertes `D:\Program Files\Odoo\20\python\python.exe` |
| Datenbank | PostgreSQL, Rolle `openpg`, Passwort in `odoo.conf` |
| Buchhaltung | SKR04, Land DE, Währung EUR |
| Addons-Pfad | `D:\Program Files\Odoo\20\server\odoo\addons,C:\Users\ABC\magyc-odoo,C:\Users\ABC\oca-addons` |

## 2. Module

| Modul | Version | Abhängigkeiten | Inhalt |
| --- | --- | --- | --- |
| `magyc_custom` | 20.0.1.0.0 | base, contacts, sale_management, stock, account | Kiosk-Stammdaten, Kundentyp, Preislisten, Felder an Firma und Auftrag |
| `magyc_commission` | 20.0.1.0.0 | magyc_custom, sale_management, stock, account, product_expiry | Abverkaufsmeldung, Buchung, Rechnung |
| `magyc_pfand` | 20.0.1.0.0 | magyc_custom, magyc_commission, sale_management, account | Pfandzeile, Pfand-Rücknahme, Einstellungen |
| `magyc_documents` | 20.0.1.1.0 | magyc_custom, sale_management, stock, account, account_followup | Belegtexte, Mahnstufen |
| `magyc_ops` | 20.0.1.0.0 | magyc_custom, magyc_commission, magyc_pfand, stock, sale_management, account, mail | Kiosk-Postfach, Lieferungen, Touren, Verluste, Prämien, Rücknahme |

Installationsreihenfolge: `magyc_custom`, `magyc_commission`, `magyc_pfand`, `magyc_documents`,
`magyc_ops`. DATEV zusätzlich: `date_range`, dann `datev_export`, dann `datev_export_dtvf`.

## 3. Datenmodell

| Modell | Typ | Zweck |
| --- | --- | --- |
| `magyc.abverkauf` | mail.thread | Abverkaufsmeldung je Kiosk und Zeitraum |
| `magyc.abverkauf.line` | – | Positionen mit erwarteter, gezählter und Rückgabemenge |
| `magyc.pfand.return` | mail.thread | Pfand-Rücknahme, erzeugt Gutschrift |
| `magyc.pfand.return.line` | – | Pfandartikel und Menge |
| `magyc.document.text` | – | Kopf- und Fußtexte je Belegart |
| `magyc.tour` | – | Tour mit Stopps, Sortierung nach Postleitzahl |
| `magyc.kiosk.application` | mail.thread, mail.alias.mixin | Kiosk-Postfach, Umwandlung in Kontakt |
| `magyc.ops` | – | Sammelmodell für Cron-Läufe (Akquisiteur, 6-Monats-Rücknahme) |
| `magyc.delivery.wizard` | TransientModel | Erstbestückung und Nachschub anlegen |
| `magyc.transfer.wizard` | TransientModel | Speditionstransfer Berlin nach Köln |

Erweiterte Standardmodelle: `res.partner` (Kiosk-ID, Kundentyp, Status, Gebiet, Akquisiteur,
Kommissionslager, IBAN, Liefersperre), `res.company` (Prämien, Pfand, Fristen, DATEV),
`stock.picking` (Übergabe, Erstbestückung, Rücknahme, Stop-Reihenfolge), `stock.move` (Verlust-
Kennzeichen, Freigabe), `sale.order` (Pfandzeile, Liefersperre), `product.template` (Pfandbetrag).

## 4. Automatiken

| Automatik | Auslöser | Wirkung |
| --- | --- | --- |
| Kommissionslager | Anlegen oder Ändern eines Kontakts mit Kundentyp Kiosk | Lagerort `KOM/<Kiosk-ID>` wird erzeugt |
| Kiosk-Nummer | Anlegen ohne Kiosk-ID | Fortlaufende Nummer je Gebiet (`magyc.kiosk.BER`, `magyc.kiosk.KOE`) |
| FEFO | Lieferung an Kiosk | Charge mit frühestem MHD zuerst, ohne MHD zuletzt |
| Rückgabe in Sperre | Abverkauf bestätigen | Rückgabemenge geht in die Qualitätssperre |
| Pfandzeile | Auftrag mit Getränkeposition | Pfandposition je Menge, 19 % USt |
| Liefersperre | Überfällige Rechnung oder offene Differenz | Auftragsbestätigung wird blockiert |
| Startprämie | Erste Übergabe | Status am Kiosk auf offen |
| Akquisiteur-Rechnung | Cron, monatlich | Sammelrechnung je Akquisiteur |
| 6-Monats-Rücknahme | Cron, täglich | Rückholung ohne Abverkauf |

Crons sind mit `active = false` ausgeliefert und werden nach der Inbetriebnahme aktiviert.

## 5. Rechte

`magyc_ops/security/ir.access.csv` vergibt `crud` auf alle eigenen Modelle an `base.group_user`.
Die Schadensfreigabe (`RAN/SCHADEN`) prüft zusätzlich `stock.group_stock_manager`, die Aufhebung
einer Liefersperre ist protokolliert.

Wichtig: In `ir.access.csv` steht in der Spalte `model_id` der Modellname (`magyc.tour`), nicht die
External ID. Ein Eintrag `model_magyc_tour` lädt nicht und bricht die Modulinstallation ab.

## 6. Stammdaten und Datenrecords

| Datensatz | Datei | Inhalt |
| --- | --- | --- |
| Sequenzen | `magyc_ops/data/ir_sequence.xml` | `magyc.kiosk.BER`, `magyc.kiosk.KOE` |
| Verlust-Kennzeichen | `magyc_ops/data/ir_scrap_tags.xml` | `RAN/MUSTER`, `RAN/SCHADEN` |
| Postfach | `magyc_ops/data/mail_alias.xml` | Alias `kiosk`, Modell `magyc.kiosk.application` |
| Belegtexte | `magyc_documents/data/magyc_document_text_data.xml` | sieben Belegarten |
| Mahnstufen | `magyc_documents/data/magyc_dunning_data.xml` | drei Stufen |

Das Postfach setzt `alias_model_id` und `alias_defaults` selbst, weil `_alias_get_creation_values`
beim Anlegen sonst ohne Modellbezug bleibt.

## 7. Tests

| Bereich | Datei | Anzahl |
| --- | --- | --- |
| Erweiterungen | `magyc_ops/tests/test_ops.py` | 14 |
| Soll-Ablauf | `magyc_commission/tests/test_soll_ablauf.py` | 13 |
| DATEV | `oca-addons/datev_export*/tests` | 9 |

Aufruf:

```
cd "/d/Program Files/Odoo/20/server"
"./../python/python.exe" odoo-bin -c odoo.conf -d magyc_dev \
  -u magyc_ops,magyc_commission,datev_export,datev_export_dtvf \
  --test-enable --stop-after-init --http-port 10031
```

Erwartete Zeile: `0 failed, 0 error(s) of 36 tests`. Die Soll-Ablauf-Tests laufen mit
`post_install`, damit sie gegen die echten Stammdaten prüfen.

## 8. DATEV

Die Module stammen aus `OCA/l10n-germany` 19.0 und liegen portiert unter `C:\Users\ABC\oca-addons`
mit eigener Versionshistorie; die Unterschiede stehen in `PORTING-20.0.md`.

| Feld an der Firma | Zweck |
| --- | --- |
| `datev_consultant_number` | Beraternummer |
| `datev_client_number` | Mandantennummer |
| `datev_account_code_length` | Sachkontenlänge |
| `datev_partner_numbering` | Nummernkreis oder manuell |

Export: Buchhaltung, Berichterstattung, DATEV DTVF Export. Ergebnis sind Buchungsstapel,
Debitoren und Kreditoren sowie Kontenbeschriftungen (CP1252, Semikolon, Kopfzeile 700/21).
Eine leere Debitorensequenz löst beim Aufruf von `_next()` einen Fehler aus; der Port fällt dann
auf die Kontakt-ID zurück. Vor dem Echtbetrieb Sequenzen oder manuelle Nummern konfigurieren.

## 9. Beispieldaten

`tools/demo_seed.py` legt Lager Köln, Akquisiteur, vier Kioske, Erstbestückung, Nachschub, eine
Rechnung und die DATEV-Konfiguration an. Das Skript ist wiederholbar.

```
cd "/d/Program Files/Odoo/20/server"
"./../python/python.exe" odoo-bin shell -c odoo.conf -d magyc_dev --no-http --log-level=warn \
  < /c/Users/ABC/magyc-odoo/tools/demo_seed.py
```

## 9a. Modul magyc_warehouse

| Teil | Inhalt |
| --- | --- |
| Zonen | `stock.location.magyc_zone`: general, quarantine, pick, customer, consumption |
| Stellplätze | `magyc_bin_code` = `barcode`, 885 Plätze per `post_init_hook` (`R03_TOP_TO = 27`) |
| Wareneingang | `magyc.receipt.wizard`, Stellplatz je Zeile, Charge bleibt an der Zeile, Reservierungszeile wird weiterverwendet |
| Umlagerung | `magyc.bin.transfer` ruft `stock.picking._magyc_transfer` aus `magyc_ops` |
| Etiketten | `magyc.label.wizard`, Bericht `magyc_warehouse.report_bin_label` auf `stock.location` (Code128) |
| Regeln | FEFO auf Kategorie Getränke, Pickzonenprüfung nur für Kundenlieferungen, Ablaufsperre, Tray-Prüfung, Cron `_cron_expired_to_quarantine` |
| Verbrauch | `stock.move.magyc_write_off_consumption(product, qty, location, reason)` |
| Rollen | MAGYC Warehouse, Driver, Store Success Manager |
| Konten | Pfand brutto auf 4401, Rückstellung netto 3071 gegen 4000 (Beispiel 1000/500 Dosen: 125,00 brutto, 105,04 netto) |

## 10. Bekannte Grenzen

| Thema | Stand |
| --- | --- |
| `stock.scrap` | In Odoo 20 nicht vorhanden, Verluste laufen über `stock.move`, Verbrauch über `magyc_write_off_consumption` |
| Palettenlogik | Transfer rechnet 24 Dosen je Tray als festen Wert, echte Palettenkonfiguration offen |
| Köln | Lager mit Platzhalteradresse, Regalplan und echte Anlieferung offen |
| Kontenrahmen | Staging läuft auf SKR03, Schreiben der Kanzlei nennt SKR04. Konten 4401, 3071, 4000, 3806 sind angelegt, Entscheidung offen |
| Pfand-Clearing | DPG-Konten nach Paragraf 17 UStG fehlen |
| Versand | DSV/UPS/DPD/DHL: Felder und `magyc_create_label` vorhanden, ohne Zugangsdaten Fehlermeldung |
| Scanner | Kein Hardwareanschluss, Stellplatzcodes sind zugleich Barcodes für `stock_barcode` |
| Kiosk-Postfach | `message_new` lokal getestet, Staging ohne eingehende Mail, Flixcheck-Feldformat unbekannt |
| Deployment | Instanz ohne SSH, Ausrollen über Upload der Modulpakete |
| DATEV | Strukturell geprüft, Import in DATEV mit echten Nummern noch offen |

## 11. Werkzeuge im Repository

| Datei | Zweck |
| --- | --- |
| `tools/demo_seed.py` | Beispieldaten und DATEV-Probelauf |
| `docs/build_docs.py` | erzeugt Handbuch und Liste der offenen Angaben als PDF |
| `oca-addons/PORTING-20.0.md` | Portierungsnotizen DATEV |

PDF-Erzeugung: `cd docs && uv run --with reportlab python build_docs.py` (schreibt
`MAGYC-Handbuch-De.pdf` und `MAGYC-Offene-Angaben-De.pdf`).
