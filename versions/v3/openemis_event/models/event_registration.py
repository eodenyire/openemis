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


class OpEventRegistration(models.Model):
    _name = "op.event.registration"
    _description = "Event Registration"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    event_id = fields.Many2one('op.event', 'Event', required=True)
    student_id = fields.Many2one('op.student', 'Student')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    attendee_name = fields.Char('Attendee Name')
    attendee_email = fields.Char('Attendee Email')
    registration_date = fields.Datetime(
        'Registration Date', default=fields.Datetime.now)
    attended = fields.Boolean('Attended', default=False)
    state = fields.Selection(
        [('registered', 'Registered'),
         ('attended', 'Attended'),
         ('cancelled', 'Cancelled')],
        string='State', default='registered', tracking=True)
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    def action_mark_attended(self):
        self.write({'state': 'attended', 'attended': True})

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_registered(self):
        self.write({'state': 'registered', 'attended': False})
