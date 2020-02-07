# OpenERP custom modules for Billing

## Deployment Procedure
1. Enter /opt/bahmni-erp directory
	a. cd /opt/bahmni-erp;
	b. git clone https://github.com/padamdahal/erp-billing-addons.git

2. Open the file /opt/bahmni-erp/etc/openerp-server.conf with any text editor
3. Add the following line at the end of the file:
   addons_path=/opt/bahmni-erp/erp-billing-addons,/usr/lib/python2.6/site-packages/openerp-7.0_20130301_002301-py2.6.egg/openerp/addons

4. Restart the openerp server
   sudo service openerp restart

5. Go to OpenERP > Settings. Click on "Update Modules List"
