{
    "name": "MAGYC Pfand",
    "version": "20.0.1.0.0",
    "summary": "Einwegpfand 0,25 € als eigene Belegzeile, 19 % USt",
    "author": "PassForm Digital",
    "category": "Sales/Sales",
    "license": "LGPL-3",
    "depends": ["magyc_custom", "magyc_commission", "sale_management", "account"],
    "data": [
        "security/ir.access.csv",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
        "views/magyc_pfand_return_views.xml",
    ],
    "installable": True,
}
