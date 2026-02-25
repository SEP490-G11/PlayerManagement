# -*- coding: utf-8 -*-
{
    "name": "Hồ sơ bệnh án",
    "version": "1.0",
    "summary": "zen8labs medical record module",
    "description": "zen8labs medical record module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "depends": ["z_appointment", "product", "z_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/drug_views.xml",
        "views/visit_views.xml",
        "views/icd_views.xml",
        "views/medical_record_menu_views.xml",
        "views/icd_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_medical_record/static/src/fields/*/*.js",
            "z_medical_record/static/src/fields/*/*.xml",
            "z_medical_record/static/src/medical_record_tree/*.js",
            "z_medical_record/static/src/xml/web_list_renderer.xml",
            "z_medical_record/static/src/scss/*.scss",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
