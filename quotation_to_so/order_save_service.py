import json
import logging

from psycopg2._psycopg import DATETIME
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from itertools import groupby
from datetime import date, datetime
from openerp.tools import pickle


_logger = logging.getLogger(__name__)


class order_save_service(osv.osv):
    _inherit = 'order.save.service'
    
    def create_sale_order(self, cr, uid, vals, context=None):
        _logger.info("\n\n\n*****vals=%s",vals)
        partner_id = self.pool.get('res.partner').search(cr, uid, [('ref','=',vals.get('customer_id'))], context=context)
        _logger.info("\n\n\n*****partner_id=%s",partner_id)
        product_id = self.pool.get('product.product').search(cr, uid, [('name','=','Registration Fee')],context=context)
        _logger.info("\n\n\n*****product_id=%s",product_id)
        orders_string = vals.get("orders")
        order = json.loads(orders_string)
        if any(order.get('openERPOrders')):
            order_details = order.get('openERPOrders')[0]
            visit_type = str(order_details.get('visitType'))
            if visit_type == 'OPD':
                care_setting = 'opd'
            if visit_type == 'IPD':
                care_setting = 'ipd'
            provider_name = str(order_details.get('providerName'))
            _logger.info("\n\n\n*****care_setting=%s",care_setting)
            reg_fee = order_details.get('fee')
            _logger.info("\n\n\n*****reg_fee=%s",reg_fee)
            shop_id = self.pool.get('sale.shop').search(cr, uid, [('name','=','Billing')],context)
            _logger.info("\n\n\n*****shop_id=%s",shop_id)
            so_vals = {
                        'partner_id':partner_id[0],
                        'care_setting':care_setting,
                        'provider_name':provider_name,
                        'pricelist_id': 1,
                        'partner_invoice_id': partner_id[0],
                        'partner_shipping_id': partner_id[0],
                        'shop_id':shop_id[0],
                        'order_line': [(0,0,{'product_id':product_id[0],
                                             'name':'Registration Fee',
                                                'product_uom_qty':1.0,
                                                'price_unit':reg_fee}
                                       )],
                        }
            sale_pool = self.pool.get('sale.order')
            reg_sale_id = sale_pool.create(cr, uid, so_vals, context)
            _logger.info("\n\n\n*****reg_sale_id=%s",reg_sale_id)
            result = sale_pool.action_button_confirm(cr, uid, [reg_sale_id], context)
            _logger.info("\n\n\n*****result=%s",result)
        return True
        
    #Below method is for Passing FEFO based Batch no in the sale order line.
    def _create_sale_order_line_function(self, cr, uid, name, sale_order, order, context=None):
        _logger.info( "\n\n\n****_create_sale_order_line_function From Quotation_to_so")
        stored_prod_ids = self._get_product_ids(cr, uid, order, context=context)

        if(stored_prod_ids):
            prod_id = stored_prod_ids[0]
            prod_obj = self.pool.get('product.product').browse(cr, uid, prod_id)
            sale_order_line_obj = self.pool.get('sale.order.line')
            prod_lot = sale_order_line_obj.get_available_batch_details(cr, uid, prod_id, sale_order, context=context)

            actual_quantity = order['quantity']
            comments = " ".join([str(actual_quantity), str(order.get('quantityUnits', None))])

            default_quantity_object = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'bahmni_sale_discount', 'group_default_quantity')[1]
            default_quantity_total = self.pool.get('res.groups').browse(cr, uid, default_quantity_object, context=context)
            default_quantity_value = 1
            if default_quantity_total and len(default_quantity_total.users) > 0:
                default_quantity_value = -1

            order['quantity'] = self._get_order_quantity(cr, uid, order, default_quantity_value)
            product_uom_qty = order['quantity']
            if(prod_lot != None and order['quantity'] > prod_lot.future_stock_forecast):
                product_uom_qty = prod_lot.future_stock_forecast
            #-----------------------------------------------------------------
            #---Anand Patel As this methos is already used in one of openerp-modules repo need to overide this so added below code-----
            stock_prod_lot = self.pool.get('stock.production.lot')
            lot_ids = stock_prod_lot._name_search(cr, uid, '', [('product_id','=',prod_id),('is_discarded','=',False)], context=context)
            lot_ids = [l[0] for l in lot_ids]
            lot_ids = stock_prod_lot.browse(cr, uid, lot_ids, context)
            lot_ids = sorted(lot_ids, key=lambda l: (l.prod_cat=='Free'),reverse=True)
            batch_id = lot_ids[0].id if any(lot_ids) else False
            sale_order_line = {
                'product_id': prod_id,
                'price_unit': prod_obj.list_price,
                'comments': comments,
                'product_uom_qty': product_uom_qty,
                'product_uom': prod_obj.uom_id.id,
                'order_id': sale_order.id,
                'external_id':order['encounterId'],
                'external_order_id':order['orderId'],
                'name': prod_obj.name,
                'type': 'make_to_stock',
                'state': 'draft',
                'dispensed_status': order.get('dispensed', False),
                'batch_id':batch_id,

            }
            if batch_id:
                sale_order_line['expiry_date'] = stock_prod_lot.browse(cr, uid, batch_id, context).life_date
            #Commented the below code since we are not using default functionality as its not getching the Batch values.
            #if prod_lot != None:
            #    life_date = prod_lot.life_date and datetime.strptime(prod_lot.life_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            #    sale_order_line['price_unit'] = prod_lot.sale_price if prod_lot.sale_price > 0.0 else sale_order_line['price_unit']
            #    sale_order_line['batch_name'] = prod_lot.name
            #    sale_order_line['batch_id'] = prod_lot.id
            #    sale_order_line['expiry_date'] = life_date and life_date.strftime('%d/%m/%Y')
            #---Anand Patel Done---
            sale_order_line_obj.create(cr, uid, sale_order_line, context=context)

            sale_order = self.pool.get('sale.order').browse(cr, uid, sale_order.id, context=context)

            if product_uom_qty != order['quantity']:
                order['quantity'] = order['quantity'] - product_uom_qty
                self._create_sale_order_line_function(cr, uid, name, sale_order, order, context=context)
                
    def _get_shop_and_local_shop_id (self, cr, uid, orderType, location_name, context):
        shop_list_with_orderType = []
        if (location_name):
            shop_list_with_orderType = self.pool.get('order.type.shop.map').search(cr, uid, [('order_type', '=', orderType), ('location_name', '=', location_name)], context=context)

        if (len(shop_list_with_orderType) == 0):
            shop_list_with_orderType = self.pool.get('order.type.shop.map').search(cr, uid, [('order_type', '=', orderType),  ('location_name', '=', None)], context=context)

        if(len(shop_list_with_orderType) == 0):
            return (False, False)
        else:
            order_type_map_object = self.pool.get('order.type.shop.map').browse(cr, uid, shop_list_with_orderType[0], context=context)
            if(order_type_map_object['shop_id']):
                shop_id = order_type_map_object['shop_id'].id
            else:
                shop_id_list = self.pool.get('sale.shop').search(cr, uid,[], context=context)
                first_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id_list[0], context=context)
                shop_id= first_shop['id']

            if(order_type_map_object['local_shop_id']):
                local_shop_id = order_type_map_object['local_shop_id'].id
            else:
                local_shop_id = False
        if orderType:
            order_type_id = self.pool.get('order.type.shop.map').search(cr, uid,[('order_type','=',orderType)], context=context, limit=1)[0]
            shop_id = self.pool.get('order.type.shop.map').browse(cr, uid, order_type_id, context).shop_id.id
        _logger.info('\n\n\n*****Shop_id=%s%s',shop_id,orderType)
        return (shop_id, local_shop_id)
        
    def create_orders(self, cr,uid,vals,context):
        discount = str(vals.get("discount_type"))
        customer_id = vals.get("customer_id")
        _logger.info("\n\n*****discount=%s||..Customer=%s",discount,customer_id)
        if discount in ['Delivery','HIV']:
            _logger.info("\n\n*****if discount%s,%s",discount,type(discount))
            if discount == 'Delivery':
                product_id = self.pool.get('product.product').search(cr, uid, [('name','=','Delivery cases')], context)
                description = 'Delivery cases'
                if product_id:
                    product_id = product_id[0] or False
                discount_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service_charge_sale', 'delivery')[1]
                if discount_id:
                    dis_obj = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context)
                    percent = dis_obj.percentage
                    discount_acc_id = dis_obj.discount_acc_id.id
            if discount == 'HIV':
                customer_ids = self.pool.get('res.partner').search(cr, uid, [('ref', '=', customer_id)], context=context)
                if(customer_ids):
                    cus_id = customer_ids[0]
                    self.pool.get('res.partner').write(cr, uid, cus_id, {'hiv':True}, context)
                #product_id = self.pool.get('product.product').search(cr, uid, [('name','=','HIV disease')], context)
                #description = 'HIV disease'
                #if product_id:
                #    product_id = product_id[0] or False
                #discount_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service_charge_sale', 'plhiv')[1]
                #if discount_id:
                #    dis_obj = self.pool.get('service.charge.type').browse(cr, uid, discount_id, context)
                #    percent = dis_obj.percentage
                #    discount_acc_id = dis_obj.discount_acc_id.id
            _logger.info("\n\n****Discount(Delivery/HIV) update sale order method called")
            customer_ids = self.pool.get('res.partner').search(cr, uid, [('ref', '=', customer_id)], context=context)
            if(customer_ids):
                cus_id = customer_ids[0]
                sale_order_ids = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id),('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)
                _logger.info("\n\n****sale_order_ids=%s",sale_order_ids)
                #if not sale_order_ids and discount == 'HIV':
                    
                for order_id in sale_order_ids:
                    _logger.info("\n\n****Order ID=%s",order_id)
                    order_line_vals = {}
                    if product_id:
                        order_line_vals.update({'product_id':product_id,
                                                'name':description,
                                                'comments':description,
                                                'product_uom_qty':1.0,
                                                'price_unit':0.0,
                                                'order_id':order_id})
                    _logger.info("\n\n****order_line_vals=%s",order_line_vals)
                    line_id = self.pool.get('sale.order.line').create(cr, uid, order_line_vals, context)
                    _logger.info("\n\n****new line id=%s is created for Sale order id=%s",line_id,order_id)
                    sale_pool = self.pool.get('sale.order')
                    sale_pool.write(cr, uid, order_id, {
                                                   'service_charge_type_id':service_charge_type_id,
                                                   'discount_percentage':percent,
                                                   'disc_account_id':discount_acc_id},context)
                    sale_pool.button_dummy(cr, uid, order_id, context)
        customer_id = vals.get("customer_id")
        location_name = vals.get("locationName")
        all_orders = self._get_openerp_orders(vals)
        _logger.info( "\n\n\n***create_orders")
        if(not all_orders):
            return ""

        customer_ids = self.pool.get('res.partner').search(cr, uid, [('ref', '=', customer_id)], context=context)
        if(customer_ids):
            cus_id = customer_ids[0]

            for orderType, ordersGroup in groupby(all_orders, lambda order: order.get('type')):

                orders = list(ordersGroup)
                care_setting = orders[0].get('visitType').lower()
                provider_name = orders[0].get('providerName')
                unprocessed_orders = self._filter_processed_orders(context, cr, orders, uid)

                tup = self._get_shop_and_local_shop_id(cr, uid, orderType, location_name, context)
                _logger.info("\n\n type tuple value=%s",tup)
                shop_id = tup[0]
                local_shop_id = tup[1]

                if(not shop_id):
                    continue

                name = self.pool.get('ir.sequence').get(cr, uid, 'sale.order')
                #Adding both the ids to the unprocessed array of orders, Separating to dispensed and non-dispensed orders
                unprocessed_dispensed_order = []
                unprocessed_non_dispensed_order = []
                for unprocessed_order in unprocessed_orders :
                    unprocessed_order['custom_shop_id'] = shop_id
                    unprocessed_order['custom_local_shop_id'] = local_shop_id
                    if(unprocessed_order.get('dispensed', 'false') == 'true') :
                        unprocessed_dispensed_order.append(unprocessed_order)
                    else :
                        unprocessed_non_dispensed_order.append(unprocessed_order)

                if(len(unprocessed_non_dispensed_order) > 0 ) :
                    sale_order_ids = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_non_dispensed_order[0]['custom_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    if(not sale_order_ids):
                        #Non Dispensed New
                        self._create_sale_order(cr, uid, cus_id, name, unprocessed_non_dispensed_order[0]['custom_shop_id'], unprocessed_non_dispensed_order, care_setting, provider_name, context)
                    else:
                        #Non Dispensed Update
                        self._update_sale_order(cr, uid, cus_id, name, unprocessed_non_dispensed_order[0]['custom_shop_id'], care_setting, sale_order_ids[0], unprocessed_non_dispensed_order, provider_name, context)

                    sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_non_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    if(len(sale_order_ids_for_dispensed) > 0):
                        if(sale_order_ids_for_dispensed[0]) :
                            sale_order_line_ids_for_dispensed = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order_ids_for_dispensed[0])], context=context)
                            if(len(sale_order_line_ids_for_dispensed) == 0):
                                self.pool.get('sale.order').unlink(cr, uid, sale_order_ids_for_dispensed, context=context)


                if(len(unprocessed_dispensed_order) > 0 and local_shop_id) :
                    sale_order_ids = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    if(not sale_order_ids_for_dispensed):
                        #Remove existing sale order line
                        self._remove_existing_sale_order_line(cr,uid,sale_order_ids[0],unprocessed_dispensed_order,context=context)

                        #Removing existing empty sale order
                        sale_order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order_ids[0])], context=context)

                        if(len(sale_order_line_ids) == 0):
                            self.pool.get('sale.order').unlink(cr, uid, sale_order_ids, context=context)

                        #Dispensed New
                        self._create_sale_order(cr, uid, cus_id, name, unprocessed_dispensed_order[0]['custom_local_shop_id'], unprocessed_dispensed_order, care_setting, provider_name, context)

                        if(self._allow_automatic_convertion_to_saleorder (cr,uid)):
                            sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)
                            self.pool.get('sale.order').action_button_confirm(cr, uid, sale_order_ids_for_dispensed, context)

                    else:
                        #Remove existing sale order line
                        self._remove_existing_sale_order_line(cr,uid,sale_order_ids[0],unprocessed_dispensed_order,context=context)

                        #Removing existing empty sale order
                        sale_order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order_ids[0])], context=context)
                        if(len(sale_order_line_ids) == 0):
                            self.pool.get('sale.order').unlink(cr, uid, sale_order_ids, context=context)

                        #Dispensed Update
                        self._update_sale_order(cr, uid, cus_id, name, unprocessed_dispensed_order[0]['custom_local_shop_id'], care_setting, sale_order_ids_for_dispensed[0], unprocessed_dispensed_order, provider_name, context)
        else:
            raise osv.except_osv(('Error!'), ("Patient Id not found in openerp"))
