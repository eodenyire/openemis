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


class OpHostelBlock(models.Model):
    _name = "op.hostel.block"
    _description = "Hostel Block"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Block Name', required=True)
    code = fields.Char('Code', size=16, required=True)
    capacity = fields.Integer('Total Capacity')
    description = fields.Text('Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_block_name', 'unique(name)', 'Block name must be unique!'),
        ('unique_block_code', 'unique(code)', 'Block code must be unique!'),
    ]
