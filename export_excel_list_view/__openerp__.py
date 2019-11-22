# -*- coding: utf-8 -*-

{
    'name': 'Export as Excel in list view',
    'version': '1.0',
    'category': 'Web',
    'description': """
Export Excel in list view
=========================
After you installed it, you’ll find an additional link ‘Export List View’
right below the ‘Export’ one. By clicking on it you’ll get a XLS file contains
the same data of the tree view you are looking at, headers included.
""",
    'author': "Satvix Informatics / Anand Patel",
    'website': 'https://www.satvix.com',
    'license': 'AGPL-3',
    'depends': ['web'],
    'js': ['static/*/*.js', 'static/*/js/*.js'],
    'qweb': ['static/xml/export_excel_list_view.xml'],
    'installable': True,
    'auto_install': False,
    'web_preload': False,
}
