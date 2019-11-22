{
    "name": "Nepali Datepicker",
    'version': '1.0',
    'summary': 'Web tool',
    "description":
        """
OpenERP Web Nepali Calendar.
============================
This module provides Nepali DatePicker in Web Interface.
""",
    'author': "Satvix Informatics / Anand Patel",
    'website': 'https://www.satvix.com',
    'license': 'AGPL-3',
    'depends': ['web'],
    'data': [],
    'js': ['static/lib/jQuery_calendars/jquery.plugin.js',
            'static/lib/jQuery_calendars/jquery.calendars.js',
            'static/lib/jQuery_calendars/jquery.calendars.plus.js',
            'static/lib/jQuery_calendars/jquery.calendars.picker.js',
            #'static/lib/jQuery_calendars/jquery.calendars.picker-ne.js',
            'static/lib/jQuery_calendars/jquery.calendars.nepali.js',
            'static/lib/jQuery_calendars/jquery.calendars.nepali-ne.js',
            'static/src/js/web_nepali_datepicker.js',
    ],
    'css': ['static/src/css/web_nepali_datepicker.css',
            'static/lib/jQuery_calendars/jquery.calendars.picker.css',
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'installable': True,    
    'auto_install': False,
}
