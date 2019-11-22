# -*- coding: utf-8 -*-

from osv import fields, osv
from datetime import datetime
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    _columns = {
        'is_expired':fields.boolean('Expired',readonly=True),
        'is_discarded':fields.boolean('Discarded',readonly=True),
    }
    
    def cron_is_batch_expired(self, cr, uid, context=None):
        _logger.info("\n\n*****Cron Job Called..")
        lot_ids = self.search(cr, uid, [('is_expired','=',False)], context=context)
        for lot_id in lot_ids:
            life_date = self.browse(cr, uid, lot_id, context=context).life_date
            if life_date:
                life_date = str(life_date.split(' ')[0])
                today = str(datetime.today().date())
                _logger.info("\n**life date:-%s",life_date)
                _logger.info("\n**Today date:-%s",today)
                if today > life_date:
                    _logger.info("\n***Date is Expired and lot id=%s",lot_id)
                    self.write(cr, uid, [lot_id], {'is_expired':True}, context=context)
                
        return True

stock_production_lot()
