# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Satvix Informatics (<https://www.satvix.com/>).
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

{
    'name':'Warehouse-Location Data',
    'version':'1.0',
    'category' : 'Warehouse',
    'description' : """
      Set up warehouses and shops for hospital and pharmacy billing.

        1. Billing
        2. Pharmacy

      Set up the following locations for hospital and pharmacy billing:

        1. Central Store (Warehouse)
        2. Pharmacy (Warehouse and Internal Location)
        3. General Ward (Internal Location)
        4. Gynaecology Ward (Internal Location)
        5. Emergency (Internal Location)

    """,
    'author':'Satvix Informatics / GYB IT SOLUTIONS',
    'website':'https://www.satvix.com/',
    'depends':['sale','stock','point_of_sale','bahmni_lab_seed_setup'],
    'data': [
        'data/warehouse_data.xml',
    ],
    'js': [],
    'css':[],
    'demo': [],
    'images':[],
    'test': [],
    'installable': True,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
