# -*- coding: utf-8 -*-

{
    'name': 'Service Charge Types',
    'version': '1.0',
    'category': 'sale',
    'description': """
Support different service charge types like
===========================================
*   Medico-legal case
*   OCMC 
*   Delivery cases
*   Ultra-poor patient
*   PLHIV
*   Hospital Discount
*   Staff Discount
""",
    'author': "Satvix Informatics / Anand Patel",
    'website': 'https://www.satvix.com',
    'license': 'AGPL-3',
    'data': [
            'security/ir.model.access.csv',
            'data/data.xml',
            'service_charge_type_view.xml',
            'sale_view.xml',
            'invoice_view.xml'
            ],
    'depends': ['base','sale','bahmni_sale_discount','account'],
    'installable': True,
    'auto_install': False,
}
