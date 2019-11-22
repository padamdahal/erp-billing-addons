# -*- coding: utf-8 -*-
{
    'name':'Nepali Base Modifier',
    'version':'1.0',
    'category' : 'base',
    'summary': 'Nepali Base Customization' ,
    'description' : """This module help to add a new fields in base addons views like Invoicing,Stock,Users,Customers, etc...""",
    'author':'Satvix Informatics / GYB IT SOLUTIONS',
    'website':'https://www.satvix.com/',
    'depends':['sale','account','account_voucher','bahmni_customer_payment','bahmni_sale_discount'],
    'data': [
        'base_models_view.xml',
        'security/security.xml',
        'wizard/excel_download_wizard_view.xml',
    ],
    'js': [],
    'css':[],
    'demo': [],
    'images':[],
    'test': [],
    'installable': True,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
