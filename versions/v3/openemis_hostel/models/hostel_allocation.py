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
from odoo.exceptions import UserError, ValidationError


class OpHostelAllocation(models.Model):
    _name = "op.hostel.allocation"
    _description = "Student Hostel Allocation"
    _rec_name = "student_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id DESC"

    student_id = fields.Many2one(
        'op.student', 'Student', required=True, tracking=True)
    room_id = fields.Many2one(
        'op.hostel.room', 'Room', required=True, tracking=True)
    academic_year_id = fields.Many2one(
        'op.academic.year', 'Academic Year', tracking=True)
    check_in_date = fields.Date(
        'Check-In Date', required=True,
        default=fields.Date.today, tracking=True)
    check_out_date = fields.Date('Check-Out Date', tracking=True)
    monthly_fee = fields.Float(
        'Monthly Fee',
        related='room_id.room_type_id.monthly_fee',
        store=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('checked_out', 'Checked Out'),
         ('cancelled', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_student_room_year',
         'unique(student_id, room_id, academic_year_id)',
         'A student can only have one allocation per room per academic year!'),
    ]

    @api.constrains('check_in_date', 'check_out_date')
    def _check_dates(self):
        for rec in self:
            if rec.check_out_date and rec.check_in_date > rec.check_out_date:
                raise ValidationError(
                    _('Check-out date must be on or after the check-in date.'))

    def action_confirm(self):
        for rec in self:
            room = rec.room_id
            if room.state == 'maintenance':
                raise UserError(
                    _('Room "%s" is under maintenance and cannot be allocated.')
                    % room.name)
            if room.available <= 0:
                raise UserError(
                    _('Room "%s" has no available beds.') % room.name)
            rec.state = 'confirmed'

    def action_checkout(self):
        for rec in self:
            rec.state = 'checked_out'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
