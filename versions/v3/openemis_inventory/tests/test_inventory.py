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

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestInventory(TransactionCase):
    """Regression tests for the Inventory module."""

    def setUp(self):
        super(TestInventory, self).setUp()
        self.category = self.env['op.inventory.category'].create({
            'name': 'Laboratory Equipment',
            'description': 'Equipment used in science lab',
        })
        self.item = self.env['op.inventory.item'].create({
            'name': 'Microscope',
            'code': 'INV-001',
            'category_id': self.category.id,
            'unit_of_measure': 'pieces',
            'min_stock_level': 2.0,
        })

    def test_inventory_category_create(self):
        """Test creating an inventory category."""
        self.assertEqual(self.category.name, 'Laboratory Equipment')
        self.assertTrue(self.category.active)

    def test_inventory_category_unique(self):
        """Test that inventory category names must be unique."""
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.inventory.category'].create({
                'name': 'Laboratory Equipment'
            })

    def test_inventory_item_create(self):
        """Test creating an inventory item."""
        self.assertEqual(self.item.name, 'Microscope')
        self.assertEqual(self.item.code, 'INV-001')
        self.assertEqual(self.item.current_stock, 0.0)

    def test_inventory_item_code_unique(self):
        """Test that inventory item codes must be unique."""
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.inventory.item'].create({
                'name': 'Another Item',
                'code': 'INV-001',
                'category_id': self.category.id,
            })

    def test_stock_in_transaction(self):
        """Test that a stock-in transaction increases current stock."""
        self.env['op.inventory.transaction'].create({
            'item_id': self.item.id,
            'transaction_type': 'in',
            'quantity': 10.0,
            'date': '2024-09-01',
        })
        self.item.invalidate_recordset()
        self.assertEqual(self.item.current_stock, 10.0)

    def test_stock_out_transaction(self):
        """Test that a stock-out transaction decreases current stock."""
        self.env['op.inventory.transaction'].create({
            'item_id': self.item.id,
            'transaction_type': 'in',
            'quantity': 10.0,
            'date': '2024-09-01',
        })
        self.env['op.inventory.transaction'].create({
            'item_id': self.item.id,
            'transaction_type': 'out',
            'quantity': 3.0,
            'date': '2024-09-05',
        })
        self.item.invalidate_recordset()
        self.assertEqual(self.item.current_stock, 7.0)

    def test_transaction_quantity_must_be_positive(self):
        """Test that transaction quantity must be greater than zero."""
        with self.assertRaises(ValidationError):
            self.env['op.inventory.transaction'].create({
                'item_id': self.item.id,
                'transaction_type': 'in',
                'quantity': 0.0,
                'date': '2024-09-01',
            })

    def test_low_stock_flag(self):
        """Test that low_stock flag is set when stock is at or below minimum."""
        self.env['op.inventory.transaction'].create({
            'item_id': self.item.id,
            'transaction_type': 'in',
            'quantity': 2.0,
            'date': '2024-09-01',
        })
        self.item.invalidate_recordset()
        self.assertTrue(self.item.low_stock)

    def test_not_low_stock(self):
        """Test that low_stock flag is not set when stock is above minimum."""
        self.env['op.inventory.transaction'].create({
            'item_id': self.item.id,
            'transaction_type': 'in',
            'quantity': 10.0,
            'date': '2024-09-01',
        })
        self.item.invalidate_recordset()
        self.assertFalse(self.item.low_stock)
