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

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpLesson(models.Model):
    _name = "op.lesson"
    _description = "Lesson Plan"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_faculty(self):
        return self.env['op.faculty'].search([
            ('user_id', '=', self._uid)
        ], limit=1) or False

    name = fields.Char(
        'Lesson Title', required=True)
    faculty_id = fields.Many2one(
        'op.faculty', string='Faculty', required=True,
        default=lambda self: self._default_faculty())
    course_id = fields.Many2one(
        'op.course', string='Course', required=True)
    batch_id = fields.Many2one(
        'op.batch', string='Batch')
    subject_id = fields.Many2one(
        'op.subject', string='Subject', required=True)
    academic_term_id = fields.Many2one(
        'op.academic.term', string='Academic Term')
    lesson_date = fields.Date(
        'Lesson Date', required=True, default=fields.Date.today)
    duration = fields.Float(
        'Duration (Hours)', help='Duration of the lesson in hours, e.g. 1.5')
    lesson_number = fields.Integer(
        'Lesson Number', help='Lesson number in the course sequence')
    topic = fields.Char(
        'Topic', required=True,
        help='Topic or unit being covered in this lesson')
    learning_objectives = fields.Text(
        'Learning Objectives',
        help='What students will learn by the end of this lesson')
    teaching_materials = fields.Text(
        'Teaching Materials',
        help='Materials, resources and equipment needed for this lesson')
    teaching_method = fields.Selection(
        [
            ('lecture', 'Lecture'),
            ('discussion', 'Discussion'),
            ('demonstration', 'Demonstration'),
            ('group_work', 'Group Work'),
            ('practical', 'Practical/Lab'),
            ('field_trip', 'Field Trip'),
            ('other', 'Other'),
        ],
        string='Teaching Method', default='lecture')
    content = fields.Html(
        'Lesson Content',
        help='Detailed lesson content, notes and delivery plan')
    homework = fields.Text(
        'Homework / Assignment',
        help='Assignment or homework given to students after this lesson')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('planned', 'Planned'),
            ('completed', 'Completed'),
        ],
        string='Status', default='draft', tracking=True)
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration < 0:
                raise ValidationError(_('Duration cannot be negative.'))

    def action_plan(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'planned'
            else:
                raise ValidationError(
                    _("Lesson can only be set to 'Planned' from 'Draft' state."))

    def action_complete(self):
        for record in self:
            if record.state == 'planned':
                record.state = 'completed'
            else:
                raise ValidationError(
                    _("Lesson can only be marked 'Completed' from 'Planned' state."))

    def action_reset_draft(self):
        for record in self:
            record.state = 'draft'
