###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'openEMIS Transportation',
    'version': '18.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 3,
    'summary': 'Manage School Transportation, Routes and Vehicle Assignment',
    'complexity': 'easy',
    'author': 'openEMIS',
    'website': 'https://www.openemis.org',
    'depends': ['openemis_core'],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/vehicle_view.xml',
        'views/route_view.xml',
        'views/route_stop_view.xml',
        'views/student_transport_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': ['demo/transportation_demo.xml'],
    'installable': True,
    'auto_install': True,
    'application': True,
}
