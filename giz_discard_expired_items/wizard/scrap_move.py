# -*- coding: utf-8 -*-
import logging
import random
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class scrap_move_wizard(osv.osv_memory):
    _name = 'scrap.batch.wizard'
    _description = 'Scrap Serial No'

    _columns = {
        'scrap_location_id':fields.many2one('stock.location','Scrap Location',required=True),
    }
    
    def create_scrap_move(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        for lot_id in context.get('active_ids'):
            lot_obj = self.pool.get('stock.production.lot').browse(cr, uid, lot_id, context)
            if any(lot_obj.move_ids):
                move_vals = {
                    'name': lot_obj.product_id.name,
                    'product_qty': lot_obj.move_ids[0].product_qty,
                    'product_uom': lot_obj.move_ids[0].product_uom.id,
                    'product_id': lot_obj.product_id.id,
                    'location_id': lot_obj.move_ids[0].location_dest_id.id,
                    'location_dest_id': self.browse(cr, uid, ids, context)[0].scrap_location_id.id,
                    'date': datetime.now(),
                    'date_expected': datetime.now(),
                    'prodlot_id':lot_id,
                }
                lot_obj.write({'is_discarded':True, 'removal_date': datetime.now()})
                move_id = move_obj.create(cr, uid, move_vals, context)
                _logger.info("\n\n****move_id=%s",move_id)
                move_obj.action_done(cr, uid, [move_id], context)
            else:
                raise osv.except_osv(_('Warning!'), _('Batch No:- %s dose not contain any Quantiry assigned to move for scrap')%(lot_obj.name,))
        return True
