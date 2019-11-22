{
    "name": "Create cerdit note",
    "version": "1.0",
    "depends": ["purchase","account_voucher","account"],
    "author": "Satvix Informatics / Anand Patel",
    "website": "https://www.satvix.com",
    "category": "Account",
	"summary": "Credit note against the return of the Purchase Order",
    "description": """
    Credit note against the return of the Purchase Order 
    """,
    'data': ['purchase_view.xml',
    ],
    'demo': [],
    'css' : [
        ],

    'auto_install': False,
    'application': True,
    'installable': True,
}
