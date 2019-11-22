{
    "name": "Bahmni  Quotaion to Sale Order",
    "version": "1.0",
    "depends": ["sale","bahmni_atom_feed","bahmni_sale_discount","service_charge_sale"],
    "author": "Satvix Informatics / Anand Patel",
    "website": "https://www.satvix.com",
    "category": "Sale",
	"summary": "Confirm sale from Quotation",
    "description": """
*   Confirm sale from Quotation
*   Pass the Shop and discount details from Sale Order to Cusomer Invoice
    """,
    'data': ['data/product.product.csv','data/data.xml'],
    'demo': [],
    'css' : [
        ],

    'auto_install': False,
    'application': True,
    'installable': True,
}
