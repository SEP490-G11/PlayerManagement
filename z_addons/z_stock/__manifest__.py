# -*- coding: utf-8 -*-
{
    "name": "Kho",
    "version": "1.0",
    "summary": "zen8labs stock module",
    "description": "zen8labs stock module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 10,
    "depends": ["stock", "purchase", "z_combo", "z_product", "z_place"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "data/product_data.xml",
        "views/stock_picking_views.xml",
        "views/general_form_views.xml",
        "views/report/picking_template_views.xml",
        "views/stock_vpick_views.xml",
        "views/z_usage_view.xml",
        "views/stock_warehouse_views.xml",
        "wizard/stock_inventory_report_wizard_views.xml",
        "report/stock_inventory_report_template.xml",
        "report/stock_inventory_report.xml",
        "views/stock_menu_views.xml",     
    ],
    "assets": {
        "web.assets_backend": [
            "z_stock/static/src/scss/*.scss",
        ]
    },
    "installable": True,
    "license": "LGPL-3",
}
