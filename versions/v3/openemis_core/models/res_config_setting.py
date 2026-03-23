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

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_openemis_activity = fields.Boolean(string="Activity")
    module_openemis_achievement = fields.Boolean(string="Achievement")
    module_openemis_alumni = fields.Boolean(string="Alumni")
    module_openemis_cafeteria = fields.Boolean(string="Cafeteria")
    module_openemis_event = fields.Boolean(string="Event Management")
    module_openemis_facility = fields.Boolean(string="Facility")
    module_openemis_hostel = fields.Boolean(string="Hostel")
    module_openemis_inventory = fields.Boolean(string="Inventory")
    module_openemis_parent = fields.Boolean(string="Parent")
    module_openemis_assignment = fields.Boolean(string="Assignment")
    module_openemis_classroom = fields.Boolean(string="Classroom")
    module_openemis_discipline = fields.Boolean(string="Discipline")
    module_openemis_fees = fields.Boolean(string="Fees")
    module_openemis_grading = fields.Boolean(string="Grading")
    module_openemis_health = fields.Boolean(string="Health")
    module_openemis_admission = fields.Boolean(string="Admission")
    module_openemis_lesson = fields.Boolean(string="Lesson Planning")
    module_openemis_lms = fields.Boolean(string="LMS")
    module_openemis_notice_board = fields.Boolean(string="Notice Board")
    module_openemis_scholarship = fields.Boolean(string="Scholarship")
    module_openemis_timetable = fields.Boolean(string="Timetable")
    module_openemis_transportation = fields.Boolean(string="Transportation")
    module_openemis_exam = fields.Boolean(string="Exam")
    module_openemis_library = fields.Boolean(string="Library")
    module_openemis_attendance = fields.Boolean(string="Attendance")
    module_openemis_blog = fields.Boolean(string="Blog")
    module_openemis_mentorship = fields.Boolean(string="Mentorship")
    module_openemis_digiguide = fields.Boolean(
        string="DigiGuide – Digital Career Guidance")
    attendance_subject_generic = fields.Selection(
        [('subject', 'Subject Wise'), ('generic', 'Generic')],
        help=(
            "Subject-specific attendance will be gathered during a "
            "particular session, whereas general attendance will be "
            "collected by one responsible faculty member for the "
            "entire day."
        ),
        config_parameter="attendance_subject_generic_parameter",
        default='subject'
    )
