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


class OpDailyMenu(models.Model):
    _name = "op.daily.menu"
    _description = "Daily Menu"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Name', required=True, tracking=True)
    date = fields.Date(
        'Date', required=True, default=fields.Date.today, tracking=True)
    meal_type = fields.Selection(
        [('breakfast', 'Breakfast'), ('lunch', 'Lunch'),
         ('dinner', 'Dinner'), ('snack', 'Snack')],
        string='Meal Type', required=True, tracking=True)
    menu_item_ids = fields.Many2many(
        'op.menu.item', string='Menu Items')
    special_note = fields.Text('Special Note')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_date_meal_type',
         'UNIQUE(date, meal_type)',
         'Only one menu per meal type per day is allowed.'),
    ]
