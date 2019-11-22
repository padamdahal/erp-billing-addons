# -*- coding: utf-8 -*-
{
    'name':'Stock Reports',
    'version':'1.0',
    'category' : 'Reporting',
    'summary': 'Stock Reports' ,
    'description' : """
    Internal moves report so that I can track product movement by batch number [T87]

        1. As a user, I want a report on the internal moves of the product from the source location to the destination location so that 
           I can track the product movement by batch number.
        2. Report will be between selected two date range.
        3. The report will be available in Excel and PDF formats.
    
    Report on the stock expiry (by product) for Pharmacy and Central Store [T85]
    
        1. As a user, I want a report on the stock expiry of products for Pharmacy and Central Store such that the stock is placed in 
           the order of their time of expiry that is the product with the nearest expiry date shall be kept on the top followed by 
           the list of other products in the sequence.
        2. Report will be filtered based on the selected Location.
        3. The report will be available in Excel and PDF formats.
        
    Report on discarded items for Pharmacy and Central Store [T88]
    
        1. As a user, I want a report on discarded items for Pharmacy and Central Store
        2. Report will be between selected two date range and for the selected Location.
        3. The report will be available in Excel and PDF formats.
        
    Current Stock Report Ordered By Quantity [T84]
        1. As a user, I want the report on Current Stock in-hand arranged in the report in accordance to their quantity such that 
           the product with the least quantity stays on the top and the stock with the maximum quantity in kept at the last.
        2. Report will generated based on the selected Location.
        3. The report will be available in Excel and PDF formats.
        
    Consumption Trend Report for Last 3/6 Month [T79]
        
            1. As a user, I want a report on consumption trend for last three to six months
            2. The report should display a separate line item for each product/service. The report must display month wise 
               consumption data for each product/service.
            3. User should be able to define the start date-time, end date-time and location for the report.
            4. The report must be available in Excel and PDF formats.

    """,
    'author':'Satvix Informatics / GYB IT SOLUTIONS',
    'website':'https://www.satvix.com/',
    'depends':['stock','giz_base_modifier'],
    'data': [
        'wizard/movement_report_wizard_view.xml',
        'wizard/stock_expiry_report_wizard_view.xml',
        'wizard/discarded_items_wizard_view.xml',
        'wizard/current_stock_report_wizard_view.xml',
        'wizard/consumption_report_wizard_view.xml',
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
