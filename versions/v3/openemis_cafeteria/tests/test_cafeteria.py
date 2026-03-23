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

from odoo.tests.common import TransactionCase


class TestCafeteria(TransactionCase):
    """Regression tests for the Cafeteria module."""

    def setUp(self):
        super(TestCafeteria, self).setUp()
        self.food_category = self.env['op.food.category'].create({
            'name': 'Main Course',
        })

    def test_food_category_create(self):
        """Test creating a food category."""
        self.assertEqual(self.food_category.name, 'Main Course')
        self.assertTrue(self.food_category.active)

    def test_food_category_unique(self):
        """Test that food category names must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.food.category'].create({'name': 'Main Course'})

    def test_menu_item_create(self):
        """Test creating a menu item."""
        item = self.env['op.menu.item'].create({
            'name': 'Grilled Chicken',
            'food_category_id': self.food_category.id,
            'price': 5.50,
            'calories': 350,
            'is_vegetarian': False,
        })
        self.assertEqual(item.name, 'Grilled Chicken')
        self.assertEqual(item.price, 5.50)
        self.assertFalse(item.is_vegetarian)

    def test_vegetarian_menu_item(self):
        """Test creating a vegetarian menu item."""
        item = self.env['op.menu.item'].create({
            'name': 'Garden Salad',
            'food_category_id': self.food_category.id,
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
        })
        self.assertTrue(item.is_vegetarian)
        self.assertTrue(item.is_vegan)
        self.assertTrue(item.is_gluten_free)

    def test_daily_menu_create(self):
        """Test creating a daily menu."""
        item = self.env['op.menu.item'].create({
            'name': 'Rice and Beans',
            'food_category_id': self.food_category.id,
        })
        daily_menu = self.env['op.daily.menu'].create({
            'name': 'Monday Lunch',
            'date': '2024-09-02',
            'meal_type': 'lunch',
            'menu_item_ids': [(4, item.id)],
        })
        self.assertEqual(daily_menu.meal_type, 'lunch')
        self.assertIn(item, daily_menu.menu_item_ids)

    def test_daily_menu_unique_date_meal(self):
        """Test that only one menu per meal type per day is allowed."""
        from odoo.exceptions import ValidationError
        self.env['op.daily.menu'].create({
            'name': 'Thursday Breakfast',
            'date': '2024-09-05',
            'meal_type': 'breakfast',
        })
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.daily.menu'].create({
                'name': 'Thursday Breakfast Duplicate',
                'date': '2024-09-05',
                'meal_type': 'breakfast',
            })

    def test_daily_menu_different_meal_types(self):
        """Test creating menus for different meal types on the same day."""
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            menu = self.env['op.daily.menu'].create({
                'name': 'Friday %s' % meal_type,
                'date': '2024-09-06',
                'meal_type': meal_type,
            })
            self.assertEqual(menu.meal_type, meal_type)
