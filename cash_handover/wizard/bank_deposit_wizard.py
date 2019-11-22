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

class bank_deposit_wizard(osv.osv_memory):
    _name = "bank.deposit.wizard"
    _description = "Bank Deposit Wizard"
    _columns = {
        'closing_amount': fields.float('Closing Amount', readonly=True),
        'deposit_amount': fields.float('Deposit Amount', required=True),
        'given_deposit_to': fields.char('Given Deposit To', required=True),
        'mobile': fields.char('Mobile Of Given Deposit To', required=True),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(bank_deposit_wizard,self).default_get(cr, uid, fields, context=context)
        active_id = context.get('active_id',False)
        cash_handover = self.pool.get('cash.handover').browse(cr, uid, active_id, context=context)
        cash_handover = self.pool.get('cash.handover').browse(cr, uid, active_id, context=context)
        if cash_handover.closing_amount <= 0:
            raise osv.except_osv(_('Warning!'),_('No any closing amount to deposit!'))
        if cash_handover.bank_deposit_amount > 0:
            raise osv.except_osv(_('Warning!'),_('You have already deposited the amount in Bank for this record !'))
        if cash_handover:
            res['closing_amount'] = cash_handover.closing_amount
        return res
    
    def make_deposit(self, cr, uid, ids, context=None):
        active_id = context.get('active_id',False)
        cash_handover = self.pool.get('cash.handover').browse(cr, uid, active_id, context=context)
        wizard = self.browse(cr, uid, ids[0], context=context)
        vals = {
            'bank_deposit_amount': wizard.deposit_amount,
            'bank_depositor_name': wizard.given_deposit_to,
            'bank_depositor_number': wizard.mobile,
            'deposited_date': fields.datetime.now(),
            'bank_deposited': True
        }
        self.pool.get('cash.handover').write(cr, uid, cash_handover.id, vals, context=context)
        return True

bank_deposit_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
