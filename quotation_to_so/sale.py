# -*- coding: utf-8 -*-

#import time
#import decimal_precision as dp
#from dateutil.relativedelta import relativedelta
#import uuid
#from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime, timedelta, date
from osv import fields, osv
from tools.translate import _
from openerp import netsvc
from decimal import Decimal
import logging
_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        sale_discount = order.discount if order.discount > 0 else order.calculated_discount
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'shop_id': order.shop_id.id,
            'discount_acc_id':order.discount_acc_id.id,
            'service_charge_type_id':order.service_charge_type_id.id,
            'discount_method':'per',
            'discount_per':order.discount_percentage,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'discount': sale_discount,
            'round_off': order.round_off,
            'discount_acc_id':order.discount_acc_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'group_id':order.group_id.id,
            'group_description':order.group_description,
            'name': order.provider_name or '',


        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

    def action_button_confirm(self, cr, uid, ids, context=None):
        _logger.info("\n\n\n****action_button_confirm called.")
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'

        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                sale_price = line.price_subtotal + self._amount_line_tax(cr, uid, line, context=context)
                if line.batch_id:
                    mrp = line.batch_id.mrp * line.product_uom_qty
                    if Decimal('0.0') < Decimal(str(mrp)) < Decimal(str(sale_price)):
                        raise osv.except_osv(_('Error!'), """Unit price plus the taxes for {PRODUCTNAME} is more than batch {BATCHNO} MRP.

                        Update the MRP for the given batch before proceeding.
                        """.format(PRODUCTNAME = line.product_id.name,BATCHNO = line.batch_id.name))
        for order in self.browse(cr, uid, ids, context=context):
            _logger.info("\n\n****in function, order.service_charge_type_id=%s",order.service_charge_type_id)
            #sale.sale_shop_1
            pharm_loc_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'sale_shop_1')[1]
            _logger.info("\n\n****pharm_loc_id=%s",pharm_loc_id)
            _logger.info("\n\n****order.shop_id.id=%s",order.shop_id.id)
            if order.amount_total > 100 and order.shop_id.id == pharm_loc_id and (not (order.service_charge_type_id or order.discount_percentage)):
                discount_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service_charge_sale', 'hospital_disc')[1]
                _logger.info("\n\n****discount_id=%s",discount_id)
                if discount_id:
                    dis_obj = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context)
                    percentage = dis_obj.percentage
                    discount_acc_id = dis_obj.discount_acc_id.id
                    calc_disc = (order.amount_untaxed * percentage/100)
                    order.write({
                                'service_charge_type_id':discount_id,
                                'discount_percentage':percentage,
                                'calculated_discount':calc_disc,
                                'discount_acc_id':discount_acc_id,
                                })
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        voucher_wiz_vals = self.action_invoice_create(cr, uid, ids, False, None,False, context)
        voucher_context = voucher_wiz_vals.get('context')
        partner_id = voucher_context.get('default_partner_id')
        account_id = self.pool.get('res.partner').browse(cr, uid, partner_id, context).property_account_receivable.id
        voucher_vals = {'partner_id':voucher_context.get('default_partner_id'),
                        'amount':voucher_context.get('default_amount'),
                        'type':voucher_context.get('default_type'),
                        'account_id':account_id,
                        'invoice_id':voucher_context.get('default_invoice_id'),
                        'tag': 'onchange_partner_id',}
        #_logger.info("\n\n****voucher_vals=%s",voucher_vals)
        voucher_pool = self.pool.get('account.voucher')
        voucher_id = voucher_pool.create(cr, uid, voucher_vals, context)
        voucher_obj = voucher_pool.browse(cr, uid, voucher_id, context)
        _logger.info("\n\n****voucher_obj=%s",voucher_obj.invoice_id)
        invoice_obj = voucher_obj.invoice_id
        _logger.info("\n\n****invoice_obj=%s",invoice_obj)
        move_obj = invoice_obj.move_id
        move_line_obj = self.pool.get('account.move.line')
        _logger.info("\n\n***move_obj.id=%s",move_obj.id)
        move_lines = move_line_obj.search(cr, uid, [('move_id','=',move_obj.id)], context=context)
        _logger.info("\n\n***move_line id=%s",move_lines)
        period_obj = self.pool.get('account.period')
        date = move_obj.date
        ids = period_obj.find(cr, uid, dt=date, context=context)
        if ids:
            period_id = ids[0]
        move_line_obj.reconcile(cr, uid, move_lines, 'manual', account_id,period_id, move_obj.journal_id.id, context=context)
        self.pool.get('account.voucher').proforma_voucher(cr, uid, [voucher_id], context)
        invoice_obj.confirm_paid()
        wf_service.trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
        return True

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        _logger.info("\n\n\n****action_invoice_create called.")
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        if context is None:
            context = {}
            # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context['date_invoice'] = date_invoice
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                if line.invoiced:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                inv_ids = [res]
                invoice_ids.append(res)
                invoice.action_move_create(cr, uid, inv_ids, context)
                invoice.invoice_validate( cr, uid, inv_ids, context)
                invoice_ref = ''
                for o, l in val:
                    invoice_ref += o.name + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                invoice.write(cr, uid, [res], {'origin': invoice_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(cr, uid, order, il, context=context)
                    inv_ids = [res]
                    invoice.action_move_create(cr, uid, inv_ids, context)
                    invoice.invoice_validate(cr, uid, inv_ids, context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))

            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_form')
            inv = invoice.browse(cr, uid, invoice_ids[0], context=context)

            self.publish_sale_order(cr, uid, ids, context)

            return {
                'name':_("Pay Invoice"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'account.voucher',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'create':False,
                'edit':False,
                #'url':final_url
                'tag': 'onchange_partner_id',
                'domain': '[]',
                'context': {
                    'default_partner_id': inv.partner_id.id,
                    'default_reference': inv.name,
                    'close_after_process': True,
                    'invoice_type': inv.type,
                    'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                    'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                    'active_ids':'',
                    'active_id':'',
                    'default_amount':inv.amount_total,
                    'default_invoice_id':inv.id,
                    'create':False,
                    'edit':False,
                    }
                }
                
    def create(self, cr, uid, vals, context=None):
        sale_id = super(sale_order,self).create(cr, uid, vals, context)
        if vals.get('partner_id',False):
            if self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context).hiv:
                discount_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service_charge_sale', 'plhiv')[1]
                if discount_id:
                    dis_obj = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context)
                    percentage = dis_obj.percentage
                    discount_acc_id = dis_obj.discount_acc_id.id
                    order = self.browse(cr, uid, sale_id, context)
                    calc_disc = (order.amount_untaxed * percentage/100)
                    amount_total = (order.amount_untaxed + order.amount_tax) - calc_disc
                    cr.execute("update sale_order set service_charge_type_id=%s,discount_percentage=%s,calculated_discount=%s,discount_acc_id=%s,amount_total=%s where id=%s",(discount_id,percentage,calc_disc,discount_acc_id,amount_total,sale_id))
        return sale_id
        
    def button_dummy(self, cr, uid, ids, context=None):
        hiv_dis_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service_charge_sale', 'plhiv')[1]
        if isinstance(ids,(list)):
            ids = ids[0]
        if self.browse(cr, uid, ids, context).service_charge_type_id.id == hiv_dis_id:
            cr.execute("update sale_order set amount_total=%s where id=%s",(0,ids))
        return True
