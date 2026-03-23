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


class OpTransportRouteStop(models.Model):
    _name = "op.transport.route.stop"
    _description = "Transport Route Stop"
    _order = "sequence, id"

    name = fields.Char('Stop Name', required=True)
    route_id = fields.Many2one(
        'op.transport.route', string='Route', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    arrival_time = fields.Float('Minutes After Departure')
    landmark = fields.Char('Landmark')
    active = fields.Boolean(default=True)
