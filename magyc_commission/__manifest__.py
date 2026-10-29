{
    "name": "MAGYC Commission",
    "version": "20.0.1.0.0",
    "summary": "Kommissionsware bei Kiosken und monatliche Abverkaufsabrechnung",
    "author": "PassForm Digital",
    "category": "Sales/Sales",
    "license": "LGPL-3",
    "depends": ["magyc_custom", "sale_management", "stock", "account"],
    "data": [
        "security/ir.access.csv",
        "reports/report_uebergabeprotokoll.xml",
        "reports/report_abverkauf.xml",
        "views/magyc_abverkauf_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
