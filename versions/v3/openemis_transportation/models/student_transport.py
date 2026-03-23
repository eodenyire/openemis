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


class OpStudentTransport(models.Model):
    _name = "op.student.transport"
    _description = "Student Transport Assignment"
    _rec_name = "student_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    student_id = fields.Many2one('op.student', string='Student', required=True)
    route_id = fields.Many2one(
        'op.transport.route', string='Route', required=True)
    stop_id = fields.Many2one(
        'op.transport.route.stop', string='Stop',
        domain="[('route_id', '=', route_id)]")
    transport_type = fields.Selection(
        [('both', 'To & From School'),
         ('to_school', 'To School Only'),
         ('from_school', 'From School Only')],
        string='Transport Type', default='both', required=True)
    academic_year_id = fields.Many2one(
        'op.academic.year', string='Academic Year')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('student_academic_year_unique',
         'UNIQUE(student_id, academic_year_id)',
         'A student can only have one transport assignment per academic year!'),
    ]
