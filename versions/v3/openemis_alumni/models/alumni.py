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


class OpAlumni(models.Model):
    _name = "op.alumni"
    _description = "Alumni"
    _rec_name = "student_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    student_id = fields.Many2one(
        'op.student', string='Student', required=True, tracking=True)
    graduation_year = fields.Integer(
        string='Graduation Year', required=True, tracking=True)
    course_id = fields.Many2one(
        'op.course', string='Course', tracking=True)
    batch_id = fields.Many2one(
        'op.batch', string='Batch', tracking=True)
    employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('unemployed', 'Unemployed'),
        ('further_studies', 'Further Studies'),
        ('other', 'Other'),
    ], string='Employment Status', default='employed', tracking=True)
    employer_name = fields.Char(string='Employer Name')
    job_title = fields.Char(string='Job Title')
    industry = fields.Char(string='Industry')
    linkedin_url = fields.Char(string='LinkedIn URL')
    current_city = fields.Char(string='Current City')
    current_country_id = fields.Many2one(
        'res.country', string='Current Country')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_student_graduation_year',
         'unique(student_id, graduation_year)',
         'An alumni record already exists for this student and graduation year!'),
    ]
