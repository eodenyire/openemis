##############################################################################
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
##############################################################################

{
    'name': 'openEMIS ERP',
    'version': '18.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'author': 'openEMIS',
    'website': 'https://www.openemis.org',
    'depends': [
        'openemis_achievement',
        'openemis_admission',
        'openemis_activity',
        'openemis_alumni',
        'openemis_assignment',
        'openemis_attendance',
        'openemis_blog',
        'openemis_cafeteria',
        'openemis_cbc',
        'openemis_classroom',
        'openemis_digiguide',
        'openemis_discipline',
        'openemis_event',
        'openemis_facility',
        'openemis_fees',
        'openemis_grading',
        'openemis_health',
        'openemis_hostel',
        'openemis_inventory',
        'openemis_lesson',
        'openemis_library',
        'openemis_lms',
        'openemis_mentorship',
        'openemis_notice_board',
        'openemis_parent',
        'openemis_exam',
        'openemis_scholarship',
        'openemis_timetable',
        'openemis_transportation',
    ],
    'images': [
        'static/description/openemis-erp_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
