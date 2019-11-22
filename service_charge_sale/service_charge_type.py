# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class service_charge_type(osv.osv):
    _name = "service.charge.type"
    _description = "Service Charge Type"
    _columns = {
        'name': fields.char('Name',required=True),
        'percentage': fields.float('Percentage(%)',required=True),
        'discount_acc_id': fields.many2one('account.account','Discount Account Head',required=False),
        'active': fields.boolean('Active'),
        'note': fields.text('Notes'),
    }
    
    _defaults = {
        'active':True,
    }

