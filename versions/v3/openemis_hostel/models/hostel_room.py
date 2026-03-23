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


class OpHostelRoom(models.Model):
    _name = "op.hostel.room"
    _description = "Hostel Room"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Room Number', required=True)
    block_id = fields.Many2one('op.hostel.block', 'Block', required=True)
    room_type_id = fields.Many2one(
        'op.hostel.room.type', 'Room Type', required=True)
    capacity = fields.Integer(
        'Bed Capacity', related='room_type_id.capacity', store=True)
    occupied = fields.Integer(
        'Occupied Beds', compute='_compute_occupied', store=True)
    available = fields.Integer(
        'Available Beds', compute='_compute_available', store=True)
    state = fields.Selection(
        [('available', 'Available'),
         ('partially_occupied', 'Partially Occupied'),
         ('fully_occupied', 'Fully Occupied'),
         ('maintenance', 'Under Maintenance')],
        string='Status', compute='_compute_state', store=True,
        default='available')
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    allocation_ids = fields.One2many(
        'op.hostel.allocation', 'room_id', string='Allocations')

    @api.depends('allocation_ids', 'allocation_ids.state')
    def _compute_occupied(self):
        for room in self:
            room.occupied = len(
                room.allocation_ids.filtered(
                    lambda a: a.state == 'confirmed'))

    @api.depends('capacity', 'occupied')
    def _compute_available(self):
        for room in self:
            room.available = max(0, room.capacity - room.occupied)

    @api.depends('capacity', 'occupied')
    def _compute_state(self):
        for room in self:
            # Preserve maintenance state; it is set manually and not recomputed.
            if room.state == 'maintenance':
                continue
            if room.occupied == 0:
                room.state = 'available'
            elif room.occupied >= room.capacity:
                room.state = 'fully_occupied'
            else:
                room.state = 'partially_occupied'
