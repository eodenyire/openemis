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


class OpTransportVehicle(models.Model):
    _name = "op.transport.vehicle"
    _description = "Transport Vehicle"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Vehicle Name', required=True)
    registration_number = fields.Char('Registration Number', required=True)
    vehicle_type = fields.Selection(
        [('bus', 'Bus'), ('van', 'Van'), ('minibus', 'Minibus'), ('car', 'Car')],
        string='Vehicle Type', default='bus', required=True)
    capacity = fields.Integer('Seating Capacity')
    driver_name = fields.Char('Driver Name')
    driver_phone = fields.Char('Driver Phone')
    driver_license = fields.Char('Driver License')
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('registration_number_unique', 'UNIQUE(registration_number)',
         'Registration number must be unique!'),
    ]
