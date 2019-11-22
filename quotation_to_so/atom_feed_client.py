from datetime import datetime
import json
import uuid
from psycopg2._psycopg import DATETIME
from openerp import netsvc
from openerp.osv import fields, osv
import logging
import datetime
_logger = logging.getLogger(__name__)

class atom_event_worker(osv.osv):
    _inherit = 'atom.event.worker'
    
    def process_event(self, cr, uid, vals,context=None):
        _logger.info("vals")
        _logger.info(vals)
        category = vals.get("category")
        patient_ref = vals.get("ref")
        if(category == "create.customer"):
            self._create_or_update_customer( cr, patient_ref, uid, vals,context)
        if(category == "registration.fee"):
            self.pool.get('order.save.service').create_sale_order(cr,uid,vals,context)
        if(category == "create.sale.order"):
            self.pool.get('order.save.service').create_orders(cr,uid,vals,context)
        if(category == "create.drug"):
            self.pool.get('drug.service').create_or_update_drug(cr,uid,vals,context)
        if(category == "create.drug.category"):
            self.pool.get('drug.service').create_or_update_drug_category(cr,uid,vals,context)
        if(category == "create.drug.uom"):
            self.pool.get('product.uom.service').create_or_update_product_uom(cr,uid,vals,context)
        if(category == "create.drug.uom.category"):
            self.pool.get('product.uom.service').create_or_update_product_uom_category(cr,uid,vals,context)
        if(category == "create.radiology.test"):
            self.pool.get('radiology.test.service').create_or_update_reference_data(cr, uid, vals, context)
        if(category == "create.lab.test"):
            self.pool.get('lab.test.service').create_or_update_reference_data(cr,uid,vals,context)
        if(category == "create.lab.panel"):
            self.pool.get('lab.panel.service').create_or_update_reference_data(cr, uid, vals, context)

        self._create_or_update_marker(cr, uid, vals)
        return {'success': True}
