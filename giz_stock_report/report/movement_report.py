# -*- coding: utf-8 -*-

import time
from dateutil import tz
import pytz
import time
from openerp.osv import fields, osv, orm
from openerp.report import report_sxw
from dateutil import parser
from datetime import date
import datetime
import calendar
from openerp.tools import amount_to_text_en
from openerp.tools.amount_to_text_en import amount_to_text

class stock_movement_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(stock_movement_report, self).__init__(cr, uid, name, context=context)
        self.count = 0
        self.uid = uid
        self.cr = cr
        self.context = context
        self.localcontext.update({
            'time': time,
            #'get_start_date': self.get_start_date,
            #'get_end_date': self.get_end_date,
            'get_seq': self._get_seq,
            'get_stock_move_records': self.get_stock_move_records,
            'Get_Generated_By': self.Get_Generated_By,
            'Get_Generated_On': self.get_generated_on,
            'get_nepali_date': self._get_nepali_date,
            'get_nepali_generated_on': self.get_nepali_generated_on,
        })

    '''def get_start_date(self, data):
        dt = datetime.datetime.strptime(data['form']['start_date'], '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    
    def get_end_date(self, data):
        dt = datetime.datetime.strptime(data['form']['end_date'], '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')'''

    def _get_seq(self):
        self.count += 1
        return self.count
    
    def get_stock_move_records(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        stock_move_obj = self.pool.get('stock.move')
        stock_move_ids = stock_move_obj.search(self.cr, self.uid, [])
        ids_list = []
        for stock_move_id in stock_move_ids:
            creation_date = stock_move_obj.read(self.cr, self.uid, stock_move_id, ['create_date'])
            create_date = creation_date['create_date'].split(" ")[0]
            if create_date >= start_date and create_date <= end_date:
                ids_list.append(stock_move_obj.browse(self.cr, self.uid, stock_move_id))
        return ids_list

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
    'report.stock.movement.report',
    'stock.move',
    'giz_stock_report/report/movement.rml',
    parser=stock_movement_report,
    header="False"
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
