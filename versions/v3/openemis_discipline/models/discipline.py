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


class OpDiscipline(models.Model):
    _name = "op.discipline"
    _description = "Student Discipline Record"
    _rec_name = "student_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_faculty(self):
        return self.env['op.faculty'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1) or False

    student_id = fields.Many2one(
        'op.student', 'Student', required=True, tracking=True)
    date = fields.Date(
        'Date', required=True, default=fields.Date.today(), tracking=True)
    misbehaviour_category_id = fields.Many2one(
        'op.misbehaviour.category', 'Misbehaviour Category', required=True,
        tracking=True)
    discipline_action_id = fields.Many2one(
        'op.discipline.action', 'Discipline Action', tracking=True)
    faculty_id = fields.Many2one(
        'op.faculty', string='Reporting Faculty',
        default=lambda self: self._default_faculty(), tracking=True)
    description = fields.Text('Description')
    state = fields.Selection([
        ('reported', 'Reported'),
        ('under_review', 'Under Review'),
        ('action_taken', 'Action Taken'),
        ('resolved', 'Resolved'),
    ], string='Status', default='reported', tracking=True)
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    def action_review(self):
        self.write({'state': 'under_review'})

    def action_taken(self):
        self.write({'state': 'action_taken'})

    def action_resolve(self):
        self.write({'state': 'resolved'})
