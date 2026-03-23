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


class OpInventoryItem(models.Model):
    _name = "op.inventory.item"
    _description = "Inventory Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Name', required=True, tracking=True)
    code = fields.Char('Code', size=16, required=True, tracking=True)
    category_id = fields.Many2one(
        'op.inventory.category', string='Category', required=True)
    description = fields.Text('Description')
    unit_of_measure = fields.Char('Unit of Measure')
    current_stock = fields.Float(
        'Current Stock', compute='_compute_stock', store=True)
    min_stock_level = fields.Float('Min Stock Level')
    unit_price = fields.Float('Unit Price')
    active = fields.Boolean(default=True)
    low_stock = fields.Boolean(
        'Low Stock', compute='_compute_low_stock', store=True)
    transaction_ids = fields.One2many(
        'op.inventory.transaction', 'item_id', string='Transactions')

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Inventory item code must be unique.'),
    ]

    @api.depends('transaction_ids.quantity', 'transaction_ids.transaction_type',
                 'transaction_ids.active')
    def _compute_stock(self):
        for item in self:
            transactions = item.transaction_ids.filtered(lambda t: t.active)
            stock_in = sum(
                t.quantity for t in transactions if t.transaction_type == 'in')
            stock_out = sum(
                t.quantity for t in transactions if t.transaction_type == 'out')
            item.current_stock = stock_in - stock_out

    @api.depends('current_stock', 'min_stock_level')
    def _compute_low_stock(self):
        for item in self:
            item.low_stock = item.current_stock <= item.min_stock_level
