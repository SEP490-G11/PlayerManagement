# -*- coding: utf-8 -*-
{
    "name": "System Monitor",
    "version": "1.0",
    "summary": "zen8labs monitor module",
    "description": "zen8labs monitor module",
    "category": "Z Monitor System/Z Monitor System",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 1,
    "depends": ["z_web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_system_monitor/static/src/services/*.js",
        ],
    },
    "auto_install": False,
    "application": True,
    "license": "LGPL-3",
}
