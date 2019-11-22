# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
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


class download_excel_wizard(osv.osv_memory):
    _name= "download.excel.wizard"
    _columns= {
        'excel_file': fields.binary('Excel File'),
        'file_name': fields.char('Excel File', size=64),
    }

download_excel_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
