# -*- coding: utf-8 -*-

import time
from dateutil import tz
import pytz
from openerp.osv import fields, osv, orm
from openerp.report import report_sxw
from dateutil import parser
from datetime import date
import datetime
import random
import re
import calendar
from openerp.tools import amount_to_text_en
from openerp.tools.amount_to_text_en import amount_to_text
import logging
logger = logging.getLogger(__name__)

class current_stock(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(current_stock, self).__init__(cr, uid, name, context=context)
        self.count = 0
        self.uid = uid
        self.cr = cr
        self.context = context
        self.localcontext.update({
            'time': time,
            'get_seq': self.get_seq,
            'get_locations_name': self.get_locations_name,
            'get_lines': self.get_lines,
            'get_uom': self.get_uom,
            'get_formated_date': self.get_formated_date,
            'Get_Generated_By': self.Get_Generated_By,
            'Get_Generated_On': self.get_generated_on,
            'get_nepali_generated_on': self.get_nepali_generated_on,
        })
    
    def get_seq(self):
        self.count += 1
        return self.count
    
    def get_locations_name(self,location_ids):
        location = ''
        if location_ids:
            for location_id in location_ids:
                location_name = self.pool.get('stock.location').browse(self.cr, self.uid, location_id, context=self.context).name
                location = location + location_name +', '
        return location
    
    def get_lines(self, o):
        cr = self.cr
        uid = self.uid      
        result = []
        list_product = []
        location_outsource = tuple(o['location_ids'])
        sql_dk = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_dk
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id NOT IN %s
                AND sm.location_dest_id IN %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id IN %s
                AND sm.location_dest_id NOT IN %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code) table_dk GROUP BY product_id,name ,code
                    ''' % (location_outsource,location_outsource, location_outsource,location_outsource)

        sql_in_tk = '''
            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS qty_in_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id NOT IN %s
                AND sm.location_dest_id IN %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code
        '''% (location_outsource,location_outsource)

        sql_out_tk = '''
            SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS qty_out_tk
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id IN %s
                AND sm.location_dest_id NOT IN %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code
        '''% (location_outsource,location_outsource)

        sql_ck = '''SELECT product_id,name, code, sum(product_qty_in - product_qty_out) as qty_ck
                FROM  (SELECT sm.product_id,pt.name , pp.default_code as code,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_in,
                    0 AS product_qty_out
                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE sm.state = 'done'
                --AND sp.location_type = 'outsource_out'
                AND sm.location_id NOT IN %s
                AND sm.location_dest_id IN %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code

                UNION ALL

                SELECT sm.product_id,pt.name , pp.default_code as code,
                    0 AS product_qty_in,
                    COALESCE(sum(sm.product_qty),0) AS product_qty_out

                FROM stock_picking sp
                LEFT JOIN stock_move sm ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON sm.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_location sl ON sm.location_id = sl.id
                WHERE sm.state = 'done'
                --AND sp.location_type = 'outsource_in'
                AND sm.location_id IN %s
                AND sm.location_dest_id NOT IN %s
                --AND usage like 'internal'
                GROUP BY sm.product_id,
                pt.name ,
                pp.default_code) table_ck GROUP BY product_id,name ,code
                    ''' % (location_outsource,location_outsource, location_outsource,location_outsource)

        sql = '''
            SELECT ROW_NUMBER() OVER(ORDER BY table_ck.code DESC) AS num ,
                    table_ck.product_id, table_ck.name, table_ck.code,
                    COALESCE(sum(qty_dk),0) as qty_dk,
                    COALESCE(sum(qty_in_tk),0) as qty_in_tk,
                    COALESCE(sum(qty_out_tk),0) as qty_out_tk,
                    COALESCE(sum(qty_ck),0)  as qty_ck
            FROM  (%s) table_ck
                LEFT JOIN (%s) table_in_tk on table_ck.product_id = table_in_tk.product_id
                LEFT JOIN (%s) table_out_tk on table_ck.product_id = table_out_tk.product_id
                LEFT JOIN (%s) table_dk on table_ck.product_id = table_dk.product_id
                GROUP BY table_ck.product_id, table_ck.name, table_ck.code
        ''' %(sql_ck,sql_in_tk, sql_out_tk, sql_dk)
        self.cr.execute(sql)
        data = self.cr.dictfetchall()
        for i in data:
            list_product.append({   'num': i['num'],
                                    'product_id': i['product_id'],
                                    'name': i['name'],
                                    'code': i['code'],
                                    'qty_dk': i['qty_dk'],
                                    'qty_in_tk': i['qty_in_tk'],
                                    'qty_out_tk': i['qty_out_tk'],
                                    'qty_ck': i['qty_ck'],
                                 })
        return list_product
    
    def get_uom(self,product_id):
        product_uom = self.pool.get('product.product').browse(self.cr, self.uid, product_id, context=self.context).uom_id.name
        return product_uom
    
    def get_formated_date(self, date):
        dt = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d/%m/%Y')
    
    def get_date(self, date):
        date_list = str(date).split('-')
        dt = date_list[2] +'-'+ date_list[1] +'-'+ date_list[0]
        return str(dt)
    
    def Get_Generated_By(self):
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).name
        return user    

    def get_generated_on(self):
        now = datetime.datetime.now()
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context)
        tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
        dt = pytz.utc.localize(datetime.datetime.strptime(str(str(now).split('.')[0]), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        return str(dt).split('+')[0]
        
    def get_nepali_generated_on(self):
        now = datetime.datetime.now()
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context)
        tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
        dt = pytz.utc.localize(datetime.datetime.strptime(str(str(now).split('.')[0]), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        date_time = str(str(dt).split('+')[0]).split(' ')
        date = self._get_nepali_date(str(date_time[0]))
        nepali_date_time = date +' '+ date_time[1]
        return nepali_date_time
        
    # code by GYB for convert date from english to nepali
    def _get_nepali_date(self, date):
        parse_date = parser.parse(date)
        string_date = parse_date.strftime('%m/%d/%Y')
        english_date = string_date.replace("/", " ")

        # Below is a List of no. of days in each month  of each year within a valid range
        # where, 2000, 2001, 2002 and so on are the Nepali years and 30, 32, 31 and so on are the total days in months
        # Nepali year-month List
        nepaliMonths = [
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],  # 2000
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],  # 2001
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
            [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],  # 2071
            [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],  # 2072
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],  # 2073
            [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
            [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
            [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
            [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],  # 2090
            [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
            [30, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 31, 32, 31, 31, 31, 30, 29, 30, 30, 30, 30],
            [30, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
            [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
            [31, 31, 32, 31, 31, 31, 29, 30, 29, 30, 29, 31],
            [31, 31, 32, 31, 31, 31, 30, 29, 29, 30, 30, 30]  # 2099
        ]

        # engMonth=int(input('Enter birth month in A.D.'))
        # engDate=int(input('Enter birth date in A.D.'))
        # engYear=int(input('Enter birth year in A.D.'))
        engMonth, engDate, engYear = map(int, english_date.split())

        # define the least possible English date 1944/01/01 Saturday.
        startingEngYear = 1944
        startingEngMonth = 1
        startingEngDay = 1
        dayOfWeek = calendar.SATURDAY  # 1944 is a saturday

        # Let's define the equivalent Nepali date 2000/09/17.
        startingNepYear = 2000
        startingNepMonth = 9
        startingNepday = 17

        # Let's calculate the number of days between the two English dates as follows:
        date0 = datetime.date(engYear, engMonth, engDate)
        date1 = datetime.date(startingEngYear, startingEngMonth, startingEngDay)
        diff = (date0 - date1).days

        # initialize required nepali date variables with starting  nepali date
        nepYear = startingNepYear
        nepMonth = startingNepMonth
        nepDay = startingNepday

        # decreament delta.days until its value becomes zero
        while diff != 0:
            # getting total number of days in month nepMonth in a year nepYear
            daysInMonth = nepaliMonths[nepYear - 2000][nepMonth - 1]
            nepDay += 1  # incrementing nepali day
            if (nepDay > daysInMonth):
                nepMonth += 1
                nepDay = 1
            if (nepMonth > 12):
                nepYear += 1
                nepMonth = 1
            dayOfWeek += 1  # counting the days in terms of 7 days
            if (dayOfWeek > 7):
                dayOfWeek = 1
            diff -= 1

        # finally we print the converted date
        nepali_date = str(nepYear) + '-' + str(nepMonth) + '-' + str(nepDay)
        return nepali_date
        
report_sxw.report_sxw(
    'report.current.stock.report',
    'stock.move',
    'giz_stock_report/report/current_stock.rml',
    parser=current_stock,
    header="False"
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
