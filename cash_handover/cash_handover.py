﻿# -*- coding: utf-8 -*-

from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from dateutil import tz,parser
import pytz
import calendar
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import xlwt
from xlsxwriter.workbook import Workbook
from cStringIO import StringIO
import base64
import itertools
from operator import itemgetter
from openerp.tools import amount_to_text_en
from openerp.tools.amount_to_text_en import amount_to_text
import logging
logger = logging.getLogger(__name__)


class cash_handover(osv.osv):
    _name = 'cash.handover'
    _description = "Cash Handover"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _get_default_shop(self, cr, uid, context=None):
        shop_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).shop_id
        if shop_id:
            return shop_id.id
    
    def _display_name(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
            dt = pytz.utc.localize(datetime.strptime(str(cash_id.start_time), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
            result[cash_id.id] = str(str(dt).split('+')[0]) + ' - ' + str(cash_id.user_id.name) +' - ' + str(cash_id.shift_type)
        return result
    
    def _get_searched_invoices(self, cr, uid, cash_id, invoice_type, context=None):
        domain = [
            ('create_date', '>=', cash_id.start_time),
            ('create_date', '<=', cash_id.end_time),
            ('user_id', '=', cash_id.user_id.id),
            ('shop_id', '=', cash_id.shop_id.id),
            ('state', '=', 'paid'),
            ('type', '=', invoice_type),
        ]
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, domain)
		
        #padam
        #this one is for registration fees, where user is administrator, so get all the invoices generated by administrator for the same period??? better way to implement it?
        domain2 = [
            ('create_date', '>=', cash_id.start_time),
            ('create_date', '<=', cash_id.end_time),
            ('user_id', '=', 1),
            ('shop_id', '=', cash_id.shop_id.id),
            ('state', '=', 'paid'),
            ('type', '=', invoice_type),
        ]
        invoice_ids2 = self.pool.get('account.invoice').search(cr, uid, domain2)
        #End padam

        return invoice_ids + invoice_ids2
    
	#Padam - function for refunds, same function is used in line 114 and 157 to replace _get_searched_invoices
    #open state is used here as open itself is validated state and we are not using the full accounting features
    def _get_searched_customer_refunds(self, cr, uid, cash_id, invoice_type, context=None):
        domain = [
            ('create_date', '>=', cash_id.start_time),
            ('create_date', '<=', cash_id.end_time),
            ('user_id', '=', cash_id.user_id.id),
            ('shop_id', '=', cash_id.shop_id.id),
            ('state', '=', 'open'),
            ('type', '=', invoice_type),
        ]
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, domain)
        return invoice_ids
    #End Padam
	
    def _get_searched_payments(self, cr, uid, cash_id, payment_type, context=None):
        domain = [
            ('create_date', '>=', cash_id.start_time),
            ('create_date', '<=', cash_id.end_time),
            ('create_uid', '=', cash_id.user_id.id),
            ('state', '=', 'posted'),
            ('type', '=', payment_type),
            ('invoice_id', '>', 0),
        ]
        payment_ids = self.pool.get('account.voucher').search(cr, uid, domain)
        return payment_ids
    
    def _get_customer_invoices(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = self._get_searched_invoices(cr, uid, cash_id, 'out_invoice', context=context)
        return result
        
    def _get_supplier_invoices(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = self._get_searched_invoices(cr, uid, cash_id, 'in_invoice', context=context)
        return result
        
    def _get_customer_refunds(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = self._get_searched_customer_refunds(cr, uid, cash_id, 'out_refund', context=context)
        return result
        
    def _get_supplier_refunds(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = self._get_searched_invoices(cr, uid, cash_id, 'in_refund', context=context)
        return result
        
    def _get_customer_payments(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = self._get_searched_payments(cr, uid, cash_id, 'receipt', context=context)
        return result
        
    def _get_supplier_payments(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = self._get_searched_payments(cr, uid, cash_id, 'payment', context=context)
        return result
        
    def _get_total_income_amount(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        income_amount = 0
        for cash_id in self.browse(cr, uid, ids):
            invoice_ids = self._get_searched_invoices(cr, uid, cash_id, 'out_invoice', context=context)
            supplier_refund_ids = self._get_searched_invoices(cr, uid, cash_id, 'in_refund', context=context)
            final_invoices = sorted(sorted(invoice_ids) + sorted(supplier_refund_ids))
            for invoice_id in final_invoices:
                invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
                income_amount += invoice_obj.amount_total
            customer_payments_ids = self._get_searched_payments(cr, uid, cash_id, 'receipt', context=context)
            for payment_id in customer_payments_ids:
                payment_obj = self.pool.get('account.voucher').browse(cr, uid, payment_id, context=context)
                income_amount += payment_obj.amount
            result[cash_id.id] = income_amount
        return result
        
    def _get_total_out_amount(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        out_amount = 0
        for cash_id in self.browse(cr, uid, ids):
            invoice_ids = self._get_searched_invoices(cr, uid, cash_id, 'in_invoice', context=context)
            customer_refund_ids = self._get_searched_customer_refunds(cr, uid, cash_id, 'out_refund', context=context)
            supplier_payments_ids = self._get_searched_payments(cr, uid, cash_id, 'payment', context=context)
            final_invoices = sorted(sorted(invoice_ids) + sorted(customer_refund_ids))
            for invoice_id in final_invoices:
                invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
                out_amount += invoice_obj.amount_total
            supplier_payments_ids = self._get_searched_payments(cr, uid, cash_id, 'payment', context=context)
            for payment_id in supplier_payments_ids:
                payment_obj = self.pool.get('account.voucher').browse(cr, uid, payment_id, context=context)
                out_amount += payment_obj.amount
            result[cash_id.id] = out_amount
        return result
    
    def _get_closing_amount(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for cash_id in self.browse(cr, uid, ids):
            result[cash_id.id] = cash_id.total_income_amount + cash_id.opening_balance - cash_id.total_out_amount - cash_id.bank_deposit_amount
        return result
    
    _columns = {
        'name': fields.function(_display_name, type='char', string='Name', store=True),
        #'name': fields.char(string='Name',required=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('handover', 'Handovered')],
            'Status', readonly=True, track_visibility='onchange',help="Gives the status of the cash handover.", select=True),
        'shift_type': fields.selection([
            ('First Shift', 'First Shift'),
            ('Second Shift', 'Second Shift'),
            ('Third Shift', 'Third Shift')], 'Shift', required=True, track_visibility='onchange',help="Shift of the user.", select=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True, track_visibility='onchange'),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, states={'draft': [('readonly', False)]}),
        'start_time': fields.datetime('Start Time', required=True, states={'draft': [('readonly', False)]}, track_visibility='onchange'),
        'end_time': fields.datetime('End Time', required=True, states={'draft': [('readonly', False)]}, track_visibility='onchange'),
        'handover_to_user_id': fields.many2one('res.users', 'Hand Over To', readonly=True, track_visibility='onchange'),
        'handover_time': fields.datetime('Hand Over On', readonly=True, track_visibility='onchange'),
        'customer_invoices':fields.function(_get_customer_invoices, type='one2many', relation='account.invoice', string='Customer Invoices'),
        'supplier_invoices':fields.function(_get_supplier_invoices, type='one2many', relation='account.invoice', string='Supplier Invoices'),
        'customer_refunds':fields.function(_get_customer_refunds, type='one2many', relation='account.invoice', string='Customer Refunds'),
        'supplier_refunds':fields.function(_get_supplier_refunds, type='one2many', relation='account.invoice', string='Supplier Refunds'),
        'customer_payments':fields.function(_get_customer_payments, type='one2many', relation='account.voucher', string='Customer Payments'),
        'supplier_payments':fields.function(_get_supplier_payments, type='one2many', relation='account.voucher', string='Supplier Payments'),
        'opening_balance': fields.float('Opening Balance', readonly=True),
        'bank_deposit_amount': fields.float('Bank Deposit Amount', readonly=True),
        'total_income_amount':fields.function(_get_total_income_amount, type='float', string='Total Income Amount', digits_compute= dp.get_precision('Account'), store=True),
        'total_out_amount':fields.function(_get_total_out_amount, type='float', string='Total Out Amount', digits_compute= dp.get_precision('Account'), store=True),
        'closing_amount':fields.function(_get_closing_amount, type='float', string='Closing Amount', digits_compute= dp.get_precision('Account'), store=True),
        'dummy_boolean': fields.boolean('Dummy Boolean', readonly=True),
        'handover_amount': fields.float('Hand Over Amount', readonly=True),
        'difference_amount': fields.float('Difference Amount', readonly=True),
        'difference_amount_reason': fields.text('Difference Amount Reason', readonly=True),
        'bank_depositor_name': fields.char('Bank Depositor Name', readonly=True),
        'bank_depositor_number': fields.char('Depositor Mobile Number', readonly=True),
        'deposited_date': fields.datetime('Deposit Date', readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'shop_id': _get_default_shop,
    }
    _sql_constraints = [
        ('name_uniq', 'unique(shift_type,user_id,start_time)', 'User can handover only single record at the same time and shift !'),
    ]
    _order = 'start_time desc, id desc'
    
    
    def button_dummy(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'dummy_boolean': True}, context=context)
        return True
        
    def unlink(self, cr, uid, ids, context=None):
        for cash_id in ids:
            cash_obj = self.browse(cr, uid, cash_id, context=context)
            if cash_obj.bank_deposit_amount > 0 or cash_obj.state == 'handover':
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete deposited or handovered records.'))
        return super(cash_handover, self).unlink(cr, uid, ids, context=context)
    
    def get_formated_date(self, cr, uid, ids, date, context=None):
        str_date = str(date).split(' ')
        date_str = str(str_date[0]).split('-')
        final_date = date_str[0] +'-'+ date_str[1] +'-'+ date_str[2] +' '+ str_date[1]
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        tz = user.partner_id.tz and pytz.timezone(user.partner_id.tz) or pytz.utc
        dt = pytz.utc.localize(datetime.strptime(str(final_date), "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        return_date = str(dt).split('+')
        return return_date[0]
    
    def get_groupby_products(self, cr, uid, ids, obj, context=None):
        invoice_objs = []
        for invoice in obj.customer_invoices:
            invoice_objs.append(invoice)
        res = []
        for invoice in invoice_objs:
            for line in invoice.invoice_line:
                res.append({'product_name': line.name , 'amount': line.price_subtotal})
        
        sorted_data = sorted(res, key=itemgetter('product_name'))
        product_list = []
        for key, group in itertools.groupby(sorted_data, key=lambda x:x['product_name']):
            product_list.append({key: list(group)})
        final_list = []
        for product in product_list:
            for key,amount_lst in product.items():
                amount = 0
                for lst in amount_lst:
                    amount += lst['amount']
                final_list.append([key, amount])
        tax_amount = 0.0
        for invoice in invoice_objs:
            tax_amount += invoice.amount_tax
        if tax_amount > 0:
            tax_list = [ 'Tax', tax_amount]
            final_list.append(tax_list)
        discount_amount = 0.0
        for invoice in invoice_objs:
            discount_amount += invoice.discount
        if discount_amount > 0:
            tax_list = [ 'Discount', discount_amount]
            final_list.append(tax_list)
        return final_list
    
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
    def download_billing_excel(self, cr, uid, ids, context=None):
        import base64
        filename = 'Cash-Handover-Billing.xls'
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
        right_style = xlwt.easyxf("align: horiz right;")
        bold_style_right = xlwt.easyxf("font: bold on; align: horiz right;")

        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0,0,0,3,'District (Trishuli) Hospital', center_bold_style)
        worksheet.write_merge(1,1,0,3,'Bidur-09, Nuwakot',center_bold_style)
        worksheet.write_merge(3,3,0,3,'Cash Handover Report',center_bold_style)
        
        handover_obj = self.browse(cr, uid, ids[0], context=context)
        start_time = self.get_formated_date(cr,uid,ids,handover_obj.start_time,context)
        end_time = self.get_formated_date(cr,uid,ids,handover_obj.end_time,context)
        period = 'Period: ' + start_time + ' To ' + end_time
        
        nepali_start_date = self._get_nepali_date(cr,uid,ids,start_time,context)
        nepali_start_time = str(start_time).split(' ')[1]
        nepali_end_date = self._get_nepali_date(cr,uid,ids,end_time,context)
        nepali_end_time = str(end_time).split(' ')[1]
        nepali_period = 'Period: '+ nepali_start_date +' '+ nepali_start_time +' To '+ nepali_end_date +' '+ nepali_end_time
        
        worksheet.write_merge(4,4,0,1,period,bold_style)
        location = 'Location: ' + handover_obj.shop_id.name
        worksheet.write_merge(4,4,2,3,location,bold_style_right)
        worksheet.write_merge(5,5,0,1,nepali_period,bold_style)
        
        worksheet.write(7,0, 'SN', bold_style_right)
        worksheet.write(7,1, 'Particular', bold_style)
        worksheet.write(7,2, 'Amount', bold_style_right)
        worksheet.write(7,3, 'Remarks', bold_style_right)
        
        product_list = self.get_groupby_products(cr,uid,ids,handover_obj,context)
        user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
        row = 8
        count = 1
        if product_list:
            for product in product_list:
                worksheet.write(row,0,count)
                worksheet.col(1).width = 50 * 256
                worksheet.write(row,1,product[0])
                worksheet.col(2).width = 45 * 256
                worksheet.write(row,2,product[1], right_style)
                count += 1
                row += 1
            row = row + 4
            
            worksheet.write(row+1,1, 'Opening Balance (A)', bold_style)
            worksheet.write(row+2,1, 'Total (B)', bold_style)
            worksheet.write(row+3,1, 'Paid Out Amount (C)', bold_style)
            worksheet.write(row+4,1, 'Bank Deposite Amount (D)', bold_style)
            worksheet.write(row+5,1, 'Grand Total (A+B-C-D)', bold_style)
            
            worksheet.write(row+1,2, handover_obj.opening_balance, right_bold_style)
            worksheet.write(row+2,2, handover_obj.total_income_amount, right_bold_style)
            worksheet.write(row+3,2, handover_obj.total_out_amount, right_bold_style)
            worksheet.write(row+4,2, handover_obj.bank_deposit_amount, right_bold_style)
            worksheet.write(row+5,2, handover_obj.closing_amount, right_bold_style)
            
            amount_in_words = amount_to_text_en.amount_to_text(handover_obj.closing_amount, currency='INR')
            amount_in_words1 = amount_in_words.replace('INR', 'Rupees')
            final_words = amount_in_words1.replace('Cents', 'Paisa')
            final_words = amount_in_words1.replace('Cent', 'Paisa')
            worksheet.write_merge(row+8,row+8,0,6,'Amount in words: ' + final_words,bold_style)
            
            worksheet.write_merge(row+9,row+9,0,6,'Generated By: '+ user.name,bold_style)
            
            nepali_date = self._get_nepali_date(cr,uid,ids,str(datetime.today()).split('.')[0],context)
            nepali_datetime = nepali_date +' '+ str(str(datetime.today()).split('.')[0]).split(' ')[1]
            generated_on = 'Report Generated on: ' + str(datetime.today()).split('.')[0] +' ('+ nepali_datetime +')'
            worksheet.write_merge(row+10,row+10,0,6, generated_on,bold_style)

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
    
cash_handover()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
