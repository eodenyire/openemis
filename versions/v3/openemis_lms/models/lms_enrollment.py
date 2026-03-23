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


class OpLmsEnrollment(models.Model):
    _name = "op.lms.enrollment"
    _description = "LMS Course Enrollment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "student_id"

    student_id = fields.Many2one(
        'op.student', string='Student', required=True)
    lms_course_id = fields.Many2one(
        'op.lms.course', string='LMS Course', required=True)
    enrollment_date = fields.Date(
        'Enrollment Date', required=True, default=fields.Date.today)
    completion_percentage = fields.Float(
        'Completion (%)', default=0.0)
    status = fields.Selection(
        [('enrolled', 'Enrolled'), ('in_progress', 'In Progress'),
         ('completed', 'Completed'), ('dropped', 'Dropped')],
        string='Status', default='enrolled', tracking=True)
    completion_date = fields.Date('Completion Date')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_student_lms_course',
         'unique(student_id, lms_course_id)',
         'A student can only be enrolled once per LMS course!')]
