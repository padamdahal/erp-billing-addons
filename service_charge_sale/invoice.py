# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'service_charge_type_id' : fields.many2one('service.charge.type','Discount Head'),
    }
    
    def on_change_service_charge_type_id(self,cr, uid, ids, discount_id,context=None):
        res = {'value':{
                        'discount_per':0.0,
                        'discount':0.0,
                        }
                }
        if discount_id:
            percentage = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context=context).percentage
            dis_obj = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context=context)
            res['value'].update({'discount_per':dis_obj.percentage,'discount_method':'per','discount_acc_id':dis_obj.discount_acc_id.id})
        return res
