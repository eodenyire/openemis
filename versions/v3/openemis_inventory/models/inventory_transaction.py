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
from odoo.exceptions import ValidationError


class OpInventoryTransaction(models.Model):
    _name = "op.inventory.transaction"
    _description = "Inventory Transaction"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    item_id = fields.Many2one(
        'op.inventory.item', string='Item', required=True, tracking=True)
    transaction_type = fields.Selection(
        [('in', 'Stock In'), ('out', 'Stock Out')],
        string='Transaction Type', required=True, tracking=True)
    quantity = fields.Float('Quantity', required=True, tracking=True)
    date = fields.Date(
        'Date', required=True, default=fields.Date.today, tracking=True)
    department_id = fields.Many2one(
        'hr.department', string='Department')
    reference = fields.Char('Reference')
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Quantity must be greater than zero.')
