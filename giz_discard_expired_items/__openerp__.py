{
    "name": "Discard expired items",
    "version": "1.0",
    "depends": ["stock","bahmni_stock_batch_sale_price"],
    "author": "Satvix Informatics / Anand Patel",
    "website": "https://www.satvix.com",
    "category": "stock",
	"summary": "Discard expired items in Pharmacy and Central Store",
    "description": """
Acceptance Criteria
===================
* The users should be able to send the discarded items to 'Scrap location' in Bahmni ERP.
* The stock must be deducted at the location from which they are moved to Scrap.
* The system must also store details of the user who made the move.
    """,
    'data': ['lot_view.xml',
             'wizard/scrap_move_wiz_view.xml',
    ],
    'demo': [],
    'css' : [
        ],

    'auto_install': False,
    'application': True,
    'installable': True,
}
