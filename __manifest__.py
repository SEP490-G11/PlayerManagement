{
    'name': 'Player Management',
    'version': '1.0',
    'summary': 'Quản lý cầu thủ bóng đá',
    'author': 'Nguyen Trung',
    'category': 'Sports',
    'depends': ['base'],
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
    'application': True,
}