# magyc-odoo

Odoo 20 customisations for MAGYC DRINKS GmbH (PassForm Digital, Auftrag S00132).

## Modules

| Module | Scope |
|---|---|
| `magyc_custom` | Kiosk/commission master data on partners (Kiosk-ID, Kundentyp, Gebiet, Akquisiteur, Store Success Manager) |

Planned, not yet implemented:

- `magyc_commission` — Kommissionsware bei Kiosken, monatliche Abverkaufsabrechnung
- `magyc_pfand` — Einwegpfand 0,25 € (eigene Zeile, 19 % USt), DPG-Clearing, Rückzahlungsverpflichtung
- Belegtexte je Belegtyp (Angebot, AB, Lieferschein, Übergabeprotokoll, Rechnungen, Mahnungen)

## Installation

```
addons_path = /path/to/odoo/addons,/path/to/magyc-odoo/addons
odoo-bin -c odoo.conf -d <db> -i magyc_custom --stop-after-init
```

## Layout

```
addons/magyc_custom/
├── __manifest__.py
├── models/res_partner.py
└── views/res_partner_views.xml
```
