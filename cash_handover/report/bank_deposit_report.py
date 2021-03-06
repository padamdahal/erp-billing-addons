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
import itertools
from operator import itemgetter

class bank_deposit_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bank_deposit_report, self).__init__(cr, uid, name, context=context)
        self.count = 0
        self.uid = uid
        self.cr = cr
        self.context = context
        self.total_deposited_amount = 0
        self.localcontext.update({
            'time': time,
            'get_seq': self._get_seq,
            'get_formated_date': self.get_formated_date,
            'get_bank_deposit_ids': self.get_bank_deposit_ids,
            'get_total_deposited_amount': self.get_total_deposited_amount,
            'get_amount_in_words': self.get_amount_in_words,
            'get_report_generator': self.get_report_generator,
            'get_generated_on': self.get_generated_on,
            'get_nepali_date': self._get_nepali_date,
            'get_nepali_datetime': self.get_nepali_datetime,
            'get_nepali_generated_on': self.get_nepali_generated_on,
        })
    
    def _get_seq(self):
        self.count += 1
        return self.count
        
    def get_formated_date(self, date):
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context)
        tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
        dt = pytz.utc.localize(datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        return_date = str(dt).split('+')
        return return_date[0]
        
    def get_bank_deposit_ids(self,data):
        start_date = data['start_date']
        end_date = data['end_date']
        shop_id = data['shop_id'][0]
        self.cr.execute("select id from cash_handover ai "\
                   "WHERE (ai.deposited_date >= %s) AND (ai.deposited_date <= %s) AND (ai.shop_id = %s)", (start_date, end_date, shop_id))
        cash_handover_ids = self.cr.fetchall()
        cash_handover_list = [i[0] for i in cash_handover_ids]
        cash_handover_obj = self.pool.get('cash.handover')
        handover_objs = []
        for handover_id in cash_handover_list:
            handover_objs.append(cash_handover_obj.browse(self.cr, self.uid, handover_id ))
        for handover_obj in handover_objs:
            self.total_deposited_amount += handover_obj.bank_deposit_amount
        return handover_objs
    
    def get_total_deposited_amount(self):
        return self.total_deposited_amount
    
    def get_amount_in_words(self):
        amount_in_words = amount_to_text_en.amount_to_text(self.total_deposited_amount, currency='INR')
        amount_in_words1 = amount_in_words.replace('INR', 'Rupees')
        final_words = amount_in_words1.replace('Cents', 'Paisa')
        final_words = amount_in_words1.replace('Cent', 'Paisa')
        return final_words
    
    def get_generated_on(self):
        now = datetime.datetime.now()
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context)
        tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
        dt = pytz.utc.localize(datetime.datetime.strptime(str(str(now).split('.')[0]), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        return str(dt).split('+')[0]
        
    def get_report_generator(self):
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).name
        return user
        
    def get_nepali_generated_on(self):
        now = datetime.datetime.now()
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context)
        tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
        dt = pytz.utc.localize(datetime.datetime.strptime(str(str(now).split('.')[0]), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        date_time = str(str(dt).split('+')[0]).split(' ')
        date = self._get_nepali_date(str(date_time[0]))
        nepali_date_time = date +' '+ date_time[1]
        return nepali_date_time
    
    def get_nepali_datetime(self,datetime):
        date_time = str(datetime).split(' ')
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
    'report.bank.deposit.report',
    'cash.handover',
    'cash_handover/report/bank_deposit_report.rml',
    parser=bank_deposit_report,
    header="False"
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

