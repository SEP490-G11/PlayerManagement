# -*- coding: utf-8 -*-
{
    "name": "Nhân viên",
    "version": "1.0",
    "summary": "zen8labs employee module",
    "description": "zen8labs human module",
    "category": "zen8labs/zen8labs",
    "author": "zen8labs",
    "website": "https://www.zen8labs.com",
    "depends": [
        "spreadsheet_dashboard",
        "hr",
        "hr_org_chart",
        "z_web",
        "z_place",
        "web_notify",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/employee_views.xml",
        "views/resource_views.xml",
        "views/resource_calendar_attendance_views.xml",
        "views/employee_menu_views.xml",
        "views/hr_job_views.xml",
        "data/default_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "z_hr/static/src/fields/*/*.js",
            "z_hr/static/src/fields/*/*.xml",
            "z_hr/static/src/js/*.js",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
