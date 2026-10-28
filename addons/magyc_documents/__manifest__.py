{
    "name": "MAGYC Documents",
    "version": "20.0.1.0.0",
    "summary": "Belegtexte je Belegtyp (Angebot, AB, Rechnung, Gutschrift)",
    "author": "PassForm Digital",
    "category": "Sales/Sales",
    "license": "LGPL-3",
    "depends": ["magyc_custom", "sale_management", "stock", "account"],
    "data": [
        "security/ir.access.csv",
        "data/magyc_document_text_data.xml",
        "views/magyc_document_text_views.xml",
        "views/report_inherit.xml",
    ],
    "installable": True,
}
