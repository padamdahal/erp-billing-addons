# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'service_charge_type_id' : fields.many2one('service.charge.type','Discount Head'),
    }
    
    def on_change_service_charge_type_id(self,cr, uid, ids, discount_id,context=None):
        res = {'value':{'discount_percentage':0.0,'calculated_discount':0.0}}
        if discount_id:
            dis_obj = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context=context)
            res['value'].update({'discount_percentage':dis_obj.percentage,'discount_acc_id':dis_obj.discount_acc_id.id})
        return res

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    _columns = {
        'hiv' : fields.boolean('HIV+'),
    }
    
