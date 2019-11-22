# -*- coding: utf-8 -*-
{
    'name':'Cash Handover',
    'version':'1.0',
    'category' : 'Accounting',
    'summary': 'Cash handover at end of every shift for Billing and Pharmacy',
    'description' : """
      Cash handover module covers the below functionalities.

        1. As a user, I want a Cash handover report at end of every shift so that I have the record of the amount of money collected at the Pharmacy and Biling in user specified period of time and date.
        2. As a user, I want a Cash collection report so that I have the record of the amount of money collected at the Pharmacy and Billing in user specified period of time and date.
        3. Cash handover report.
        4. Cash(Bank) deposit report for Billing and Pharmacy in Excel and PDF

    """,
    'author':'Satvix Informatics / GYB IT SOLUTIONS',
    'website':'https://www.satvix.com/',
    'depends':['sale','account','giz_base_modifier'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/shift_handover_wizard_view.xml',
        'wizard/bank_deposit_wizard_view.xml',
        'cash_handover_view.xml',
        'report_view.xml',
        'wizard/bank_deposit_report_wizard_view.xml',
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
