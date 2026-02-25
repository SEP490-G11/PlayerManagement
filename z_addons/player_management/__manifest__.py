{
    'name': 'Player Management',
    'version': '1.0',
    'summary': 'Quản lý cầu thủ bóng đá',
    'author': 'Nguyen Trung',
    'category': 'Sports',
    'depends': ['base'],
    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/player_views.xml',
    'views/view_team.xml', 
    'views/contract_views.xml',   
    'views/menu.xml',
            
],
    'application': True,
}