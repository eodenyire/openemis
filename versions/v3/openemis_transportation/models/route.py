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


class OpTransportRoute(models.Model):
    _name = "op.transport.route"
    _description = "Transport Route"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Route Name', required=True)
    code = fields.Char('Route Code', size=16, required=True)
    vehicle_id = fields.Many2one('op.transport.vehicle', string='Vehicle')
    departure_time = fields.Float('Departure Time (Hour)')
    return_time = fields.Float('Return Time (Hour)')
    stop_ids = fields.One2many(
        'op.transport.route.stop', 'route_id', string='Stops')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Route code must be unique!'),
    ]
