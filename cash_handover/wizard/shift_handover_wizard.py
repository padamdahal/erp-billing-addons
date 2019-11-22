##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
logger = logging.getLogger(__name__)


class shift_handover_wizard(osv.osv_memory):
    _name = "shift.handover.wizard"
    _description = "Shift Handover Wizard"
    _columns = {
        'closing_amount': fields.float('Closing Amount', readonly=True),
        'handover_amount': fields.float('Hand Over Amount', required=True),
        'different_amount': fields.float('Different Amount', readonly=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'shift_type': fields.selection([
            ('First Shift', 'First Shift'),
            ('Second Shift', 'Second Shift'),
            ('Third Shift', 'Third Shift')], 'Shift', required=True, help="Shift of the user.", select=True),
        'difference_amount_reason': fields.text('Difference Amount Reason'),
    }
    
    def onchange_handover_amount(self, cr, uid, ids, closing_amount, handover_amount, context=None):
        different_amount = closing_amount - handover_amount
        return {'value': {'different_amount': different_amount}}
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(shift_handover_wizard,self).default_get(cr, uid, fields, context=context)
        active_id = context.get('active_id',False)
        cash_handover = self.pool.get('cash.handover').browse(cr, uid, active_id, context=context)
        if cash_handover.closing_amount <= 0:
            raise osv.except_osv(_('Warning!'),_('No any closing amount to handover!'))
        if cash_handover.handover_amount > 0:
            raise osv.except_osv(_('Warning!'),_('You have already handover the cash to the next sift!'))
        if cash_handover:
            res['closing_amount'] = cash_handover.closing_amount
        return res
    
    def make_handover(self, cr, uid, ids, context=None):
        active_id = context.get('active_id',False)
        cash_handover = self.pool.get('cash.handover').browse(cr, uid, active_id, context=context)
        wizard = self.browse(cr, uid, ids[0], context=context)
        new_vals = {
            'shift_type': wizard.shift_type,
            'start_time': fields.datetime.now(),
            'end_time': fields.datetime.now(),
            'user_id': wizard.user_id and wizard.user_id.id or False,
            'state': 'draft',
            'shop_id': cash_handover.shop_id and cash_handover.shop_id.id or False,
            'opening_balance': wizard.handover_amount,
        }
        self.pool.get('cash.handover').create(cr, uid, new_vals, context=context)
        
        old_vals = {
            'handover_to_user_id': wizard.user_id and wizard.user_id.id or False,
            'handover_time': fields.datetime.now(),
            'handover_amount': wizard.handover_amount,
            'difference_amount': wizard.closing_amount - wizard.handover_amount,
            'difference_amount_reason': wizard.difference_amount_reason,
            'state': 'handover',
        }
        
        
        
        self.pool.get('cash.handover').write(cr, uid, cash_handover.id, old_vals, context=context)
        return True

shift_handover_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
