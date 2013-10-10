# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'POS Extension',
    'version': '0.0.9',
    'category': 'Point Of Sale',
    'sequence': 6,
    'summary': 'To provide more function to POS',
    'description': """
Providing the more function or tools to POS
===========================

This module is to enhance the function of the POS Sales.

Main Features
-------------
* Search Invoice using session 
* Search Invoice using POS Order Ref
* Summary Report for the order lines
    """,
    'author': 'Markus Bala',
    'images': [],
    'depends': ['sale_stock'],
    'data': [
        'pos_extension_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
