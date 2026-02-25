# -*- coding: utf-8 -*-
{
    "name": "ZNS Config",
    "version": "1.0",
    "summary": "zen8labs zns config module",
    "description": "zen8labs zns config module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 1,
    "depends": ["z_web", "z_appointment"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "data/ir_cron_data.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}
