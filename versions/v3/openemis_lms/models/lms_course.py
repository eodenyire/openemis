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

from odoo import api, fields, models


class OpLmsCourse(models.Model):
    _name = "op.lms.course"
    _description = "LMS Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_faculty(self):
        return self.env['op.faculty'].search([
            ('user_id', '=', self._uid)
        ], limit=1) or False

    name = fields.Char('Course Name', required=True)
    code = fields.Char('Course Code', size=16, required=True)
    description = fields.Html('Description')
    faculty_id = fields.Many2one(
        'op.faculty', string='Faculty', required=True,
        default=lambda self: self._default_faculty())
    course_id = fields.Many2one('op.course', string='Course')
    subject_id = fields.Many2one('op.subject', string='Subject')
    image = fields.Binary('Thumbnail')
    state = fields.Selection(
        [('draft', 'Draft'), ('published', 'Published'),
         ('archived', 'Archived')],
        string='State', default='draft', tracking=True)
    section_ids = fields.One2many(
        'op.lms.section', 'lms_course_id', string='Sections')
    enrollment_ids = fields.One2many(
        'op.lms.enrollment', 'lms_course_id', string='Enrollments')
    section_count = fields.Integer(
        string='Section Count', compute='_compute_counts')
    enrollment_count = fields.Integer(
        string='Enrollment Count', compute='_compute_counts')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_lms_course_code',
         'unique(code)', 'LMS Course Code must be unique!')]

    @api.depends('section_ids', 'enrollment_ids')
    def _compute_counts(self):
        for record in self:
            record.section_count = len(record.section_ids)
            record.enrollment_count = len(record.enrollment_ids)

    def action_publish(self):
        for record in self:
            record.state = 'published'

    def action_archive_course(self):
        for record in self:
            record.state = 'archived'

    def action_reset_draft(self):
        for record in self:
            record.state = 'draft'

    def open_lms_sections(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'op.lms.section',
            'domain': [('lms_course_id', '=', self.id)],
            'name': 'Sections',
            'view_mode': 'list,form',
            'context': {'default_lms_course_id': self.id},
            'target': 'current',
        }

    def open_lms_enrollments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'op.lms.enrollment',
            'domain': [('lms_course_id', '=', self.id)],
            'name': 'Enrollments',
            'view_mode': 'list,form',
            'context': {'default_lms_course_id': self.id},
            'target': 'current',
        }
