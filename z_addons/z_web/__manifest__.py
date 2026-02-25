# -*- coding: utf-8 -*-
{
    "name": "Web",
    "version": "1.0",
    "summary": "zen8labs web module",
    "description": "zen8labs web module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 1,
    "depends": ["web", "base"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/report_layout.xml",
        "views/paperformat_data.xml",
        "data/report_layout.xml",
        "views/res_company_views.xml",
        "wizard/iframe_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_web/static/views/icons.xml",
            "z_web/static/src/constants/*.js",
            "z_web/static/src/fields/*/*.xml",
            "z_web/static/src/fields/*/*.js",
            "z_web/static/src/shared/*/*.xml",
            "z_web/static/src/shared/*/*.js",
            "z_web/static/src/shared/*.js",
            "z_web/static/src/utils/*.js",
            "z_web/static/src/hook/*.js",
            "z_web/static/src/services/*.js",
            "z_web/static/src/validators/*.js",
            "z_web/static/scss/*.scss",
            "z_web/static/css/*.css",
        ],
        "web.report_assets_common":[
            "z_web/static/scss/*.scss",
        ],
        "web.assets_common": [
            ("include", "web._assets_common_styles"),
        ],
        "web._assets_primary_variables": [
            (
                "after",
                "web/static/src/scss/primary_variables.scss",
                "z_web/static/scss/variables.scss",
            ),
        ],
    },
    "auto_install": False,
    "license": "LGPL-3",
}
