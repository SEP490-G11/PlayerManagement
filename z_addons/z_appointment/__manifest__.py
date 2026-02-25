# -*- coding: utf-8 -*-
{
    "name": "Lịch hẹn",
    "version": "1.0",
    "summary": "zen8labs appointment module",
    "description": "zen8labs appointment module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "depends": ["z_web", "z_hr", "z_partner"],
    "data": [
        "security/ir.model.access.csv",
        "views/appointment_views.xml",
        "views/appointment_menu_views.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_appointment/static/src/config/*.js",
            "z_appointment/static/src/views/*/*.js",
            "z_appointment/static/src/fields/*/*.js",
            "z_appointment/static/src/views/*/*.xml",
            "z_appointment/static/src/fields/*/*.xml",
            "z_appointment/static/src/xml/*.xml",
            "z_appointment/static/src/validators/*.js",
            "z_appointment/static/src/constants/*.js",
            "z_appointment/static/scss/*.scss",
        ],
        "web.assets_common": [
            ("include", "web._assets_common_styles"),
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
