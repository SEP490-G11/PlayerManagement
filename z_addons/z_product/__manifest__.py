# -*- coding: utf-8 -*-
{
    "name": "Product",
    "version": "1.0",
    "summary": "zen8labs product module",
    "description": "update fields for product",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "sequence": 20,
    "depends": ["product", "z_web"],
    "data": [
        "security/ir.model.access.csv",
        "data/product_data.xml",
        "views/product_views.xml",
        "views/product_categ_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
