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


class OpScholarship(models.Model):
    _name = "op.scholarship"
    _description = "Student Scholarship"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Scholarship Title', required=True)
    student_id = fields.Many2one('op.student', 'Student', required=True,
                                 tracking=True)
    scholarship_type_id = fields.Many2one('op.scholarship.type',
                                          'Scholarship Type', required=True,
                                          tracking=True)
    academic_year_id = fields.Many2one('op.academic.year', 'Academic Year')
    course_id = fields.Many2one('op.course', 'Course')
    amount = fields.Float('Amount', tracking=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('applied', 'Applied'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected'),
         ('expired', 'Expired')],
        'State', default='draft', tracking=True)
    description = fields.Text('Description')
    rejection_reason = fields.Text('Rejection Reason')
    active = fields.Boolean(default=True)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date:
                if record.end_date < record.start_date:
                    raise ValidationError(
                        _('End Date cannot be set before Start Date.'))

    def action_apply(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'applied'
            else:
                raise ValidationError(
                    _("Scholarship can only be applied from 'Draft' state."))

    def action_approve(self):
        for record in self:
            if record.state == 'applied':
                record.state = 'approved'
            else:
                raise ValidationError(
                    _("Scholarship can only be approved from 'Applied' state."))

    def action_reject(self):
        for record in self:
            if record.state in ('applied', 'approved'):
                record.state = 'rejected'
            else:
                raise ValidationError(
                    _("Scholarship can only be rejected from "
                      "'Applied' or 'Approved' state."))

    def action_expire(self):
        for record in self:
            if record.state == 'approved':
                record.state = 'expired'
            else:
                raise ValidationError(
                    _("Scholarship can only be expired from 'Approved' state."))

    def action_reset_draft(self):
        for record in self:
            if record.state == 'rejected':
                record.state = 'draft'
            else:
                raise ValidationError(
                    _("Scholarship can only be reset to draft from "
                      "'Rejected' state."))
