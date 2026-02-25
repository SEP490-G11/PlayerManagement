# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

{
    "name": "Đơn kính",
    "version": "1.0",
    "summary": "zen8labs glass order module",
    "description": "zen8labs glass order module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 10,
    "depends": ["product", "z_invoice", "z_hr", "z_medical_record", "z_web"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/glass_order_views.xml",
        "views/glass_order_menu_views.xml",
        "views/visit_views.xml",
        "views/product_views.xml",
        "views/invoice_views.xml",
        "views/report/glass_order_template.xml",
        "views/report/glass_order_views.xml",
        "views/report/glass_order_pos_template.xml",
        "views/report/glass_order_pos_views.xml",
        "views/account_move_line_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_glass_order/static/src/fields/*/*.js",
            "z_glass_order/static/src/fields/*/*.xml",
            "z_glass_order/static/src/xml/web_list_renderer.xml",
            
        ]
    },
    "installable": True,
    "license": "LGPL-3",
}
