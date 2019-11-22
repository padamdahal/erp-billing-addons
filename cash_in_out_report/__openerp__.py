# -*- coding: utf-8 -*-
{
    'name':'Cash In-Out Report',
    'version':'1.0',
    'category' : 'Reporting',
    'summary': 'Cash In-Out Report' ,
    'description' : """
        Cash collection report at end of every shift for Billing and Pharmacy [T77]

            1. As a user, I want a report on the amount of money collected by all the users in user specified period of time and date
            2. Balance is the difference between the Amount In and Amount Out
            3. The report should display a separate line item for each product/service against which money was collected at the 
               cash counter.
            2. Report will be in PDF and Excel format
        
        Amount of money collected for each service in a user defined time period [T82]
            
            1. As a user, I want a report on the amount of money collected for each product/service 
               (Labs, Pharmacy, X-Ray, USG, Bed charges etc.) in a user defined time period
            2. Reprot for the both shop Billing and Pharmacy
            3. Report will be in PDF and Excel format
            
        Amount of money lost in providing free services / per discount head in a user defined time period [T83]
        
            1. As a user, I want a report on the amount of money lost in providing free services / per discount head in a user 
               defined time period. The amount of money lost in providing free services/per discount head is visible to the admin.
            2. Discount Amount refers to the amount lost due to providing discounts.
            3. Total Amount refers to the total before the discount head
            4. The report should display a separate line item for each discount head against which discount was given to the customer 
               at the cash counter (Pharmacy/Billing).
            5. User should be able to define the start date-time and end date-time for the report.
            6. The report must be available in Excel and PDF formats.
            
    """,
    'author':'Satvix Informatics / GYB IT SOLUTIONS',
    'website':'https://www.satvix.com/',
    'depends':['sale','account','giz_base_modifier','service_charge_sale'],
    'data': [
        'wizard/cash_inout_report_wizard_view.xml',
        'wizard/shop_collection_report_wizard_view.xml',
        'wizard/discount_head_report_wizard_view.xml',
        'report_view.xml',
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
