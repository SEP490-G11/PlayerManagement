{
    'name': 'Player Management',
    'version': '1.0',
    'summary': 'Quản lý cầu thủ bóng đá',
    'author': 'Nguyen Trung',
    'category': 'Sports',
    'depends': ['base', 'web'],

    'data': [
        'data/weekday_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/player_views.xml',
        'views/view_team.xml',
        'views/contract_views.xml',
        'views/match_views.xml',
        'views/season_views.xml',
        'views/menu.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'player_management/static/src/js/*.js',
            'player_management/static/src/xml/*.xml',
            'player_management/static/src/scss/*.scss',
            'https://cdn.jsdelivr.net/npm/chart.js',
            'player_management/static/src/js/season_loading.js',
        ],
    },

    'application': True,
}