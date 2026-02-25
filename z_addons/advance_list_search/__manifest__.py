{
    "name": "Entrust Advanced List Search",
    "version": "17.0.2.0.0",
    "category": "Tools",
    "summary": "Module for advanced list search",
    "depends": ["web"],
    "data": [],
    "images": ["static/description/banner.png"],
    "assets": {
        "web.assets_backend": [
            "advance_list_search/static/src/js/*.js",
            "advance_list_search/static/src/css/*.scss",
            "advance_list_search/static/lib/daterangepicker/moment.min.js",
            "advance_list_search/static/lib/daterangepicker/daterangepicker.css",
            "advance_list_search/static/lib/daterangepicker/daterangepicker.js",

        ],
        "web.assets_common": [
            "advance_list_search/static/lib/daterangepicker/moment.min.js",
            "advance_list_search/static/lib/daterangepicker/daterangepicker.css",
            "advance_list_search/static/lib/daterangepicker/daterangepicker.js",
        ],
    },
    "application": True,
    "installable": True,
}
