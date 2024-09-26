{
    'name': 'Restaurant Reservation',
    'version': '1.0',
    'summary': 'Restaurant Reservation',
    'category': 'Tools',
    'author': 'Your Name',
    'website': 'http://yourwebsite.com',
    'depends': ['calendar', 'contacts'], 
    'data': [
        'views/reservation_views.xml', 
        'security/ir.model.access.csv', 
        'data/restaurant_reservation_sequence.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}