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


class OpScholarshipType(models.Model):
    _name = "op.scholarship.type"
    _description = "Scholarship Type"
    _order = "name"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    criteria = fields.Text('Eligibility Criteria')
    amount = fields.Float('Default Amount')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_scholarship_type_name',
         'unique(name)', 'Scholarship type name must be unique!'),
    ]
