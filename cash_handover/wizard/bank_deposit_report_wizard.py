# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.osv import fields, osv
from openerp.tools.translate import _
import dateutil.relativedelta as relativedelta
import time
import pytz
import xlwt
from xlsxwriter.workbook import Workbook
from tools.translate import _
from cStringIO import StringIO
import base64
import netsvc
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
from openerp.tools.amount_to_text_en import amount_to_text

from dateutil import tz,parser
from datetime import date,datetime, timedelta
import calendar

class bank_deposit_report_wizard(osv.osv_memory):
    _name = "bank.deposit.report.wizard"
    _columns={
              
        'start_date': fields.datetime('Start Date', required=True),
        'end_date': fields.datetime('End Date', required=True),
        'shop_id':fields.many2one('sale.shop',"Location",required=True),
        
    }
    def print_report(self,cr, uid, ids, context=None):
        if context is None:
           context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
            'ids': [data.get('id')],
            'model': 'cash.handover',
            'form': data
            }
        self_browse = self.browse(cr, uid, ids)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'bank.deposit.report',
            'datas': datas,
            'name': 'Bank Deposit Report'
            }
    
    # code by GYB for convert date from english to nepali
    def _get_nepali_date(self, cr, uid, ids, date, context=None):
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
        startingEngMonth = 01
        startingEngDay = 01
        dayOfWeek = calendar.SATURDAY  # 1944 is a saturday

        # Let's define the equivalent Nepali date 2000/09/17.
        startingNepYear = 2000
        startingNepMonth = 9
        startingNepday = 17

        # Let's calculate the number of days between the two English dates as follows:
        
        date0 = datetime.strptime(str(str(engYear)+'-'+str(engMonth)+'-'+str(engDate)), "%Y-%m-%d").date()
        #date0 = datetime.date(engYear, engMonth, engDate)
        date1 = datetime.strptime(str(str(startingEngYear)+'-'+str(startingEngMonth)+'-'+str(startingEngDay)), "%Y-%m-%d").date()
        #date1 = datetime.date(startingEngYear, startingEngMonth, startingEngDay)
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
    
    #Method for the Print Deposite Report in Excel Format
    def print_excel_report(self, cr, uid, ids, context=None):
        import base64
        wizard = self.browse(cr, uid, ids[0], context=context)
        filename = 'Bank-Deposit.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') # 36pt

        # Create a font to use with the style
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        style.font = font

        center_bold_style = xlwt.easyxf("align: horiz centre; font: bold on")
        left_bold_style = xlwt.easyxf("align: horiz right; font: bold on")
        bold_style = xlwt.easyxf("font: bold on")
        left_style = xlwt.easyxf("align: horiz right;")

        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0,0,0,6,'District (Trishuli) Hospital', center_bold_style)
        worksheet.write_merge(1,1,0,6,'Bidur-09, Nuwakot',center_bold_style)
        worksheet.write_merge(3,3,0,6,'Bank Deposit Report',center_bold_style)
        
        period = 'Period: ' + wizard.start_date + ' To ' + wizard.end_date
        worksheet.write_merge(4,4,0,2,period,bold_style)
        location = 'Location: ' + wizard.shop_id.name
        worksheet.write_merge(4,4,5,6,location,bold_style)
        
        nepali_start_date = self._get_nepali_date(cr,uid,ids,wizard.start_date,context)
        nepali_start_time = str(wizard.start_date).split(' ')[1]
        nepali_end_date = self._get_nepali_date(cr,uid,ids,wizard.end_date,context)
        nepali_end_time = str(wizard.end_date).split(' ')[1]
        nepali_period = 'Period: '+ nepali_start_date +' '+ nepali_start_time +' To '+ nepali_end_date +' '+ nepali_end_time
        worksheet.write_merge(5,5,0,2,nepali_period,bold_style)
        
        worksheet.write(7,0, 'SN', bold_style)
        worksheet.write(7,1, 'Date', bold_style)
        worksheet.write(7,2, 'Reference', bold_style)
        worksheet.write(7,3, 'User', bold_style)
        worksheet.write(7,4, 'Shop', bold_style)
        worksheet.write(7,5, 'Amount', bold_style)
        worksheet.write(7,6, 'Remarks', bold_style)

        row = 8
        count = 1
        total_deposited_amount = 0.0
        handover_ids = self.pool.get('cash.handover').search(cr, uid, [('deposited_date','>=',wizard.start_date),
                  ('deposited_date','<=',wizard.end_date),('shop_id', '=', wizard.shop_id.id)])
        if handover_ids:
            for handover_obj in self.pool.get('cash.handover').browse(cr, uid, handover_ids, context=context):
                worksheet.write(row,0,count)
                user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
                if handover_obj.deposited_date:
                    #user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context)
                    tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
                    dt = pytz.utc.localize(datetime.strptime(str(handover_obj.deposited_date), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
                    return_date = str(dt).split('+')
                    worksheet.col(1).width = 20 * 256
                    worksheet.write(row,1,return_date[0])
                if handover_obj.name:
                    worksheet.col(2).width = 45 * 256
                    worksheet.write(row,2,handover_obj.name)
                if handover_obj.user_id:
                    worksheet.col(3).width = 18 * 256
                    worksheet.write(row,3,handover_obj.user_id.name)
                if handover_obj.shop_id:
                    worksheet.write(row,4,handover_obj.shop_id.name)
                if handover_obj.bank_deposit_amount:
                    worksheet.write(row,5,handover_obj.bank_deposit_amount,left_style)
                    total_deposited_amount += handover_obj.bank_deposit_amount
                count += 1
                row += 1
            row = row + 4
            worksheet.write(row,3,'Total',bold_style)
            worksheet.write(row,5,total_deposited_amount,left_bold_style)
            amount_in_words = amount_to_text_en.amount_to_text(total_deposited_amount, currency='INR')
            amount_in_words1 = amount_in_words.replace('INR', 'Rupees')
            final_words = amount_in_words1.replace('Cents', 'Paisa')
            final_words = amount_in_words1.replace('Cent', 'Paisa')
            worksheet.write_merge(row+3,row+3,0,6,'Amount in words: ' + final_words,bold_style)
            
            worksheet.write_merge(row+5,row+5,0,6,'Generated By: '+ user.name,bold_style)
            
            nepali_date = self._get_nepali_date(cr,uid,ids,str(datetime.today()).split('.')[0],context)
            nepali_datetime = nepali_date +' '+ str(str(datetime.today()).split('.')[0]).split(' ')[1]
            generated_on = 'Report Generated on: ' + str(datetime.today()).split('.')[0] +' ('+ nepali_datetime +')'
            worksheet.write_merge(row+6,row+6,0,6, generated_on,bold_style)

        fp = StringIO()
        workbook.save(fp)
        export_id = self.pool.get('download.excel.wizard').create(cr, uid, {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename}, context=context)
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': export_id,
            'res_model': 'download.excel.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }
        return True
        
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
