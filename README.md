# magyc-odoo

Odoo 20 customisations for MAGYC DRINKS GmbH (PassForm Digital, Auftrag S00132).

## Modules

| Module | Scope |
|---|---|
| `magyc_custom` | Kiosk/commission master data on partners (Kiosk-ID, Kundentyp, Gebiet, Akquisiteur, Store Success Manager) |
| `magyc_commission` | Abverkaufsmeldung je Kiosk: bestätigt Abverkauf, bucht Ware aus dem Kommissionslager aus, erzeugt die Monatsrechnung; Übergabeprotokoll (QWeb) |
| `magyc_pfand` | Einwegpfand 0,25 € als eigene Auftragszeile (19 % USt), automatisch je Getränkezeile |
| `magyc_documents` | Belegtexte je Belegtyp (Angebot, AB, Lieferschein, Rechnung Kiosk/B2B/Shop, Gutschrift) als pflegbare Datensätze + QWeb-Einbindung |

Open: Pfand-Rücknahme/DPG-Clearing (§17 UStG) und Pfandrückzahlungsverpflichtung, Mahnstufen-Texte.

## Installation

```
addons_path = /path/to/odoo/addons,/path/to/magyc-odoo
odoo-bin -c odoo.conf -d <db> -i magyc_custom,magyc_commission,magyc_pfand,magyc_documents --stop-after-init
```

Odoo 20 notes:

- Rechte liegen in `security/ir.access.csv` (Modell `ir.access`, Spalten `operation` + `domain`) — `ir.model.access` gibt es nicht mehr.
- `product.packaging` existiert nicht mehr; Gebinde über `stock.package.type` / `stock.package`.

## Status report

`docs/build_status.py` erzeugt den zweiseitigen Statusbericht (Englisch/Deutsch) mit Anforderungstabelle:

```
uv run --with reportlab python docs/build_status.py "docs/Magyc Odoo Status Report.pdf"
```
