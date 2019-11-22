import logging

from openerp.osv import fields, osv
from openerp import pooler
from openerp.tools.translate import _
import math

_logger = logging.getLogger(__name__)

class rounding_off(osv.osv_memory):
    _name = 'rounding.off'

    def round_off_to_nearest_configured_value(self, cr, uid, value):
        _logger.info("\n\n******value=%s",value)
        if value:
            val,decimal = str(value).split('.')
            _logger.info("\n\n\n*****val=%s,decimal=%s",val,decimal)
            #decimal = decimal[0]
            if int(decimal) >= 5:
                return (1 - float('0.'+ decimal))
            if int(decimal) < 5:
                return -float('0.'+ decimal)
        else:
            return 0
        #round_off_by = self.pool.get('ir.values').get_default(cr, uid, 'sale.config.settings', 'round_off_by')
        #if(round_off_by > 0):
        #    half_round_off_by = round_off_by / 2.0
        #    remainder = value % round_off_by
        #    return  -remainder if remainder < half_round_off_by else round_off_by - remainder
        #return 0
