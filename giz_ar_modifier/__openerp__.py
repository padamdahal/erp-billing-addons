# -*- coding: utf-8 -*-
{
    'name':'Nepali Access Rights',
    'version':'1.0',
    'category' : 'base',
    'summary': 'Nepali User Role Base Access Rights' ,
    'description' : """This module help to set the role base access rights for the Pharmacy, Billing and Store Users.""",
    'author':'Satvix Informatics / GYB IT SOLUTIONS',
    'website':'https://www.satvix.com/',
    'depends':['base','sale','account','stock','purchase','giz_base_modifier','hr_timesheet_invoice','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
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
