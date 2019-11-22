# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
import dateutil.relativedelta as relativedelta
import time
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


class discarded_items_wizard(osv.osv_memory):
    _name = "discarded.items.wizard"
    _columns={
        'start_date': fields.date('Start Date', required=True,),
        'end_date': fields.date('End Date', required=True),
        'location_id':fields.many2one('stock.location',"Location",required=True)
    }

    def print_pdf_report(self,cr, uid, ids, context=None):
        if context is None:
           context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
            'ids': [data.get('id')],
            'model': 'stock.production.lot',
            'form': data
            }
        self_browse = self.browse(cr, uid, ids)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'discarded.items.report',
            'datas': datas,
            'name': 'Discarded Items'
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
    
    def print_excel_report(self, cr, uid, ids, context=None):
        import base64
        wizard = self.browse(cr, uid, ids[0], context=context)
        filename = 'Discarded-Items.xls'
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
        right_bold_style = xlwt.easyxf("align: horiz right; font: bold on")
        bold_style = xlwt.easyxf("font: bold on")
        left_style = xlwt.easyxf("align: horiz right;")

        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0,0,0,5,'District (Trishuli) Hospital', center_bold_style)
        worksheet.write_merge(1,1,0,5,'Bidur-09, Nuwakot',center_bold_style)
        worksheet.write_merge(3,3,0,5,'Discarded Items',center_bold_style)
        
        period = 'Period: ' + wizard.start_date + ' To ' + wizard.end_date
        nepali_start_date = self._get_nepali_date(cr,uid,ids,wizard.start_date,context)
        nepali_end_date = self._get_nepali_date(cr,uid,ids,wizard.end_date,context)
        nepali_period = 'Period: '+ nepali_start_date +' To '+ nepali_end_date
        
        worksheet.write_merge(4,4,0,1,period,bold_style)
        location = 'Location: ' + wizard.location_id.name
        worksheet.write_merge(4,4,4,5,location,bold_style)
        worksheet.write_merge(5,5,0,1,nepali_period,bold_style)
        
        worksheet.write(7,0, 'SN', right_bold_style)
        worksheet.write(7,1, 'Item/Drug(Unit)', bold_style)
        worksheet.write(7,2, 'Serial Number', bold_style)
        worksheet.write(7,3, 'Discarded Date', bold_style)
        worksheet.write(7,4, 'Quantity', right_bold_style)
        worksheet.write(7,5, 'Notes', right_bold_style)

        row = 8
        count = 1
        production_lot_obj_list = []
        production_lot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('removal_date','>=',wizard.start_date),('removal_date','<=',wizard.end_date),('is_discarded', '=', True)], order="removal_date desc")
        if production_lot_ids:
            for production_lot_obj in self.pool.get('stock.production.lot').browse(cr, uid, production_lot_ids, context=context):
                if production_lot_obj.move_ids:
                    for move_id in production_lot_obj.move_ids:
                        if move_id.location_dest_id.id == wizard.location_id.id:
                            if production_lot_obj not in production_lot_obj_list:
                                production_lot_obj_list.append(production_lot_obj)
        
        for lot in production_lot_obj_list:
            worksheet.write(row,0,count)
            worksheet.col(1).width = 50 * 256
            worksheet.write(row,1,lot.product_id.name_get()[0][1])
            worksheet.col(2).width = 14 * 256
            worksheet.write(row,2,lot.name)
            dt = datetime.strptime(lot.removal_date, '%Y-%m-%d %H:%M:%S')
            worksheet.col(3).width = 14 * 256
            worksheet.write(row,3,dt.strftime('%d/%m/%Y'))
            worksheet.col(4).width = 18 * 256
            discarded_qty = 0
            for move_id in lot.move_ids:
                if move_id.location_dest_id.id == wizard.location_id.id:
                    discarded_qty += move_id.product_qty
            worksheet.write(row,4,discarded_qty)
            worksheet.write(row,5,' ')
            count += 1
            row += 1
        
        row = row - 2
        user = self.pool.get('res.users').browse(cr,uid,uid,context=context).name
        worksheet.write_merge(row+5,row+5,0,5,'Generated By: '+user,bold_style)
        
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

discarded_items_wizard()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
