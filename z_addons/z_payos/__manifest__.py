{
    "name": "PayOS",
    "version": "1.0",
    "summary": "zen8labs payOS config module",
    "description": "zen8labs payOS config module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 1,
    "depends": ["z_web", "z_invoice"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/account_payment_register.xml",
        "views/qr_logs.xml",
        "views/account_move.xml",
        "views/counter_view.xml",
        "views/bank_account_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_payos/static/src/*/*.xml",
            "z_payos/static/src/*/*.js",
        ],
    },
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}