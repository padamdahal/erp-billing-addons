# -*- coding: utf-8 -*-
import logging
from osv import fields, osv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.tools import pickle
import openerp.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    _columns = {
        'prod_cat':fields.selection([('Free','Free'),('Paid','Paid')],string="Product Category",required=True),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if(record.life_date):
                expiry_date = datetime.strptime(record.life_date, '%Y-%m-%d %H:%M:%S')
                expiry = expiry_date.strftime("%b,%Y")
                name = "%s [%s]" % (name,expiry)
            if(context.get('show_future_forcast', False)):
                name =  "%s %s" % (name, record.future_stock_forecast)
            if(record.prod_cat):
                name = name + '\t [%s]' % record.prod_cat
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        ids = []
        if(context.get('only_available_batch', False)):
            batch_stock_query = 'select prodlot_id from batch_stock_future_forecast where qty > 0'
            for column,operator,value in args:
                if(column == "product_id"):
                    batch_stock_query += " and product_id = %s" % value
            if context.get('location_id', False):
                batch_stock_query += " and location_id = %s" % context['location_id']
            cr.execute(batch_stock_query)
            args += [('id', 'in', [row[0] for row in cr.fetchall()])]

        if name:
            ids = self.search(cr, uid, [('prefix', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', 'ilike', name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        lot_ids = self.browse(cr, uid, ids, context=context)
        _logger.info("\n\n****lot_ids %s",lot_ids)
        lot_ids = sorted(lot_ids, key=lambda l: (l.prod_cat=='Free'),reverse=True)
        _logger.info("\n\n****sorted lot_ids %s",lot_ids)
        ids = [lot.id for lot in lot_ids]
        _logger.info("\n\n****Final IDs %s",ids)
        return self.name_get(cr, uid, ids, context)

stock_production_lot()

class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    
    #Override the method to pass the Free/Paid attribute in the serial no
    
    def split_lot(self, cr, uid, ids, context=None):
        """ To split a lot"""
        if context is None:
            context = {}
        res = self.split(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty

                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if data.use_exist:
                        prodlot_id = line.prodlot_id.id
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line.name,
                            'sale_price':line.sale_price * move.product_uom.factor,
                            'cost_price':line.cost_price * move.product_uom.factor,
                            'mrp':line.mrp * move.product_uom.factor,
                            'life_date':line.expiry_date,
                            'product_id': move.product_id.id,
                            'prod_cat':line.prod_cat},
                        context=context)

                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move
        
split_in_production_lot()  
     
class stock_move_split_lines(osv.osv_memory):
    _inherit = "stock.move.split.lines"
    _columns = {
        'prod_cat':fields.selection([('Free','Free'),('Paid','Paid')],string="Product Category",required=True),
    }
stock_move_split_lines()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}

        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined !'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')

        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                              'batch_id': None,
                              'price_unit': 0.0,
                              'product_uos_qty': qty}, 'domain': {'product_uom': [],
                                                                  'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        #-----------------populating batch id for sale order line item-----------------------------------------------------------
        stock_prod_lot = self.pool.get('stock.production.lot')
        sale_price = 0.0
        result['batch_name'] = None
        result['batch_id'] = None
        result['expiry_date'] = None

        prodlot_context = self._get_prodlot_context(cr, uid, context=context)
        for prodlot_id in stock_prod_lot.search(cr, uid,[('product_id','=',product_obj.id)],context=prodlot_context):
            prodlot = stock_prod_lot.browse(cr, uid, prodlot_id, context=prodlot_context)
            life_date = prodlot.life_date and datetime.strptime(prodlot.life_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if life_date and life_date < datetime.today():
                continue
            if qty <= prodlot.future_stock_forecast:
                sale_price = prodlot.sale_price
                result['batch_name'] = prodlot.name
                result['batch_id'] = prodlot.id
                result['expiry_date'] = life_date.strftime('%d/%m/%Y') if (type(life_date) == 'datetime.datetime') else None
                break
        #-----------------------------------------------------------------
        #---Anand Patel As this methos is already used in one of openerp-modules repo need to overide this so added below code-----
        lot_ids = stock_prod_lot._name_search(cr, uid, '', [('product_id','=',product_obj.id),('is_discarded','=',False)], context=context)
        #_logger.info("\n\nname search=%s",lot_ids)
        lot_ids = [l[0] for l in lot_ids]
        #_logger.info("\n\nname search ids=%s",lot_ids)
        lot_ids = stock_prod_lot.browse(cr, uid, lot_ids, context)
        #_logger.info("\n\nbrowse obj ids=%s",lot_ids)
        lot_ids = sorted(lot_ids, key=lambda l: (l.prod_cat=='Free'),reverse=True)
        #_logger.info("\n\n****sorted lot_ids%s",lot_ids)
        result['batch_id'] = lot_ids[0].id if any(lot_ids) else False
        #---Anand Patel Done---

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            tax_id = product_obj.taxes_id
            if not tax_id:
                search_criteria = [
                    ('key', '=', 'default'),
                    ('model', '=', 'product.product'),
                    ('name', '=', 'taxes_id'),
                ]
                ir_values_obj = self.pool.get('ir.values')
                defaults = ir_values_obj.browse(cr, uid, ir_values_obj.search(cr, uid, search_criteria))
                default_tax_id = pickle.loads(defaults[0].value.encode('utf-8')) if defaults else None
                if default_tax_id:
                    tax_id = self.pool.get('account.tax').browse(cr, uid, default_tax_id)

            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, tax_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                          [('category_id', '=', product_obj.uom_id.category_id.id)],
                      'product_uos':
                          [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
            # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                         'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom or result.get('product_uom'),
                    'date': date_order,
                    })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                             "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': self._price(price,sale_price)})
        if warning_msgs:
            warning = {
                'title': _('Configuration Error!'),
                'message' : warning_msgs
            }

        res = {'value': result, 'domain': domain, 'warning': warning}
        # Code extracted From sale_stock.py
        if not product:
            res['value'].update({'product_packaging': False})
            return res

        #update of result obtained in super function
        res_packing = self.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging, context=context)
        res['value'].update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''
        res['value']['delay'] = (product_obj.sale_delay or 0.0)
        res['value']['type'] = product_obj.procure_method
        return res
