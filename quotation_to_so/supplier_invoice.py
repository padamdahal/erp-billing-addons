from datetime import datetime, timedelta, date
from osv import fields, osv
from tools.translate import _
from openerp import netsvc
from decimal import Decimal
import logging
_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int,long)):
            ids = [ids]
        inv_obj = self.browse(cr, uid, ids[0], context)
        if inv_obj.type == 'in_invoice':
            vat13 = self.pool['ir.model.data'].get_object_reference(cr, uid, 'quotation_to_so', 'vat13')
            _logger.info("\n\n***vat13=%s",vat13)
            if vat13 and inv_obj.amount_total > 20000:
                tax_id = vat13[1]
                for line in inv_obj.invoice_line:
                    cr.execute("select * from account_invoice_line_tax where invoice_line_id=%s and tax_id=%s",(line.id,tax_id))
                    if not cr.fetchall():
                        cr.execute("insert into account_invoice_line_tax(invoice_line_id,tax_id) values(%s,%s)",(line.id,tax_id))
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        return res
