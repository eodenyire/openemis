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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OpEvent(models.Model):
    _name = "op.event"
    _description = "School Event"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Event Name', required=True, tracking=True)
    event_type_id = fields.Many2one(
        'op.event.type', 'Event Type', required=True)
    start_date = fields.Datetime('Start Date', required=True, tracking=True)
    end_date = fields.Datetime('End Date', required=True, tracking=True)
    venue = fields.Char('Venue')
    organizer_id = fields.Many2one('op.faculty', 'Organizer')
    target_audience = fields.Selection(
        [('all', 'All'), ('students', 'Students'),
         ('faculty', 'Faculty'), ('parents', 'Parents'),
         ('external', 'External')],
        string='Target Audience', default='all')
    max_attendees = fields.Integer(
        'Max Attendees', default=0,
        help='Set to 0 for unlimited attendees.')
    registration_ids = fields.One2many(
        'op.event.registration', 'event_id', 'Registrations')
    registered_count = fields.Integer(
        'Registered', compute='_compute_registered_count', store=True)
    description = fields.Html('Description')
    state = fields.Selection(
        [('draft', 'Draft'), ('published', 'Published'),
         ('ongoing', 'Ongoing'), ('completed', 'Completed'),
         ('cancelled', 'Cancelled')],
        string='State', default='draft', tracking=True)
    active = fields.Boolean(default=True)

    @api.depends('registration_ids')
    def _compute_registered_count(self):
        for rec in self:
            rec.registered_count = len(rec.registration_ids)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    _('End Date must be greater than or equal to Start Date.'))

    def action_publish(self):
        self.state = 'published'

    def action_start(self):
        self.state = 'ongoing'

    def action_complete(self):
        self.state = 'completed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_draft(self):
        self.state = 'draft'

    def action_open_registrations(self):
        self.ensure_one()
        return {
            'name': _('Registrations'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.event.registration',
            'view_mode': 'list,form',
            'domain': [('event_id', '=', self.id)],
            'context': {'default_event_id': self.id},
        }
