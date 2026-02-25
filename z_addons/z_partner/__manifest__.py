# -*- coding: utf-8 -*-
{
    "name": "Khách hàng",
    "version": "1.0",
    "summary": "zen8labs partner module",
    "description": "zen8labs partner module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 10,
    "depends": [
        "base",
        "mail",
        "sms",  # sms is an auto installed module -> need to depend to remove it's view
        "z_web",
        "z_icd_10"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_views.xml",
        "views/group_views.xml",
        "views/partner_menu_views.xml",
        "views/menu_views.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_partner/static/scss/*.scss",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
