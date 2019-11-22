from datetime import datetime, timedelta, date
from osv import fields, osv
from tools.translate import _
from openerp import netsvc
from decimal import Decimal
import logging
_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    
    def create_credit_note(self, cr, uid, ids, context=None):
        _logger.info("\n\n****method called")
        if isinstance(ids,(list)):
            ids = ids[0]
        purchase = self.browse(cr, uid, ids, context)
        view,form_view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_purchase_receipt_form')
        view_ids = [form_view_id]
        voucher_ids = self.pool.get('account.voucher').search(cr, uid, [('purchase_id','=',purchase.id)], context=context)
        _logger.info("\n***voucher_ids=%s",voucher_ids)

        if any(voucher_ids):
            view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_voucher_tree')[1]
            view_ids.append(view_id)

            return {
                'name': _("Credit Note"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.voucher',
                'views': [(view_id, 'tree'),(form_view_id, 'form')],
                'target': 'current',
                'domain': [('id','in',voucher_ids)],
            }
        else:
            return {
                    'name':_("Credit Note"),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(form_view_id, 'form')],
                    'res_model': 'account.voucher',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'context': {
                        'partner_id': purchase.partner_id.id,
                        'reference': purchase.name,
                        'type': 'purchase',
                        'amount':purchase.amount_total,
                        'journal_id':5,
                        'purchase_id':purchase.id,
                        'line_dr_ids':[(0,0,{'name': 'Credit note for return of ' + str(purchase.name),
                                                     'amount': purchase.amount_total,
                                                     'account_id':30})],
                         'narration':'Credit note for return of ' + str(purchase.name),
                        }
                    }

#class account_voucher(osv.osv):
#    _inherit = "account.voucher"
#    
#    def default_get(self, cr, uid, fields, context=None):
#        if context is None:
#            context = {}
#        res = super(account_voucher, self).default_get(cr, uid, fields, context=context)
#        _logger.info("\n\nDefault get called context=%s",context)
#        line = tuple(res.get('line_dr_ids')[0])
#        res.update({'line_dr_ids':[line],'amount':context.get('default_amount',0.0)})
#        _logger.info("\n\nresult=%s",res)
#        return res

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
    _columns = {
    
        'purchase_id':fields.many2one('purchase.order','Purchase Order',readonly=True)
    }
