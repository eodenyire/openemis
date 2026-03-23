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

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestHostel(TransactionCase):
    """Regression tests for the Hostel module."""

    def setUp(self):
        super(TestHostel, self).setUp()
        self.block = self.env['op.hostel.block'].create({
            'name': 'Block A',
            'code': 'BLK-A',
            'capacity': 50,
        })
        self.room_type = self.env['op.hostel.room.type'].create({
            'name': 'Double Room',
            'capacity': 2,
            'monthly_fee': 100.0,
        })
        self.room = self.env['op.hostel.room'].create({
            'name': '101',
            'block_id': self.block.id,
            'room_type_id': self.room_type.id,
        })
        partner = self.env['res.partner'].create({'name': 'Hostel Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'Hostel',
            'last_name': 'Student',
            'gender': 'm',
            'partner_id': partner.id,
        })

    def test_hostel_block_create(self):
        """Test creating a hostel block."""
        self.assertEqual(self.block.name, 'Block A')
        self.assertEqual(self.block.code, 'BLK-A')

    def test_hostel_block_unique(self):
        """Test that block names and codes must be unique."""
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.hostel.block'].create({
                'name': 'Block A',
                'code': 'BLK-B',
            })

    def test_hostel_room_type_create(self):
        """Test creating a hostel room type."""
        self.assertEqual(self.room_type.name, 'Double Room')
        self.assertEqual(self.room_type.capacity, 2)

    def test_hostel_room_create(self):
        """Test creating a hostel room."""
        self.assertEqual(self.room.name, '101')
        self.assertEqual(self.room.capacity, 2)
        self.assertEqual(self.room.available, 2)
        self.assertEqual(self.room.occupied, 0)

    def test_hostel_allocation_create(self):
        """Test creating a hostel allocation."""
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        self.assertEqual(allocation.state, 'draft')
        self.assertEqual(allocation.monthly_fee, 100.0)

    def test_hostel_allocation_confirm(self):
        """Test confirming a hostel allocation."""
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        allocation.action_confirm()
        self.assertEqual(allocation.state, 'confirmed')

    def test_hostel_allocation_checkout(self):
        """Test checking out from a hostel room."""
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        allocation.action_confirm()
        allocation.action_checkout()
        self.assertEqual(allocation.state, 'checked_out')

    def test_hostel_allocation_cancel(self):
        """Test cancelling a hostel allocation."""
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        allocation.action_cancel()
        self.assertEqual(allocation.state, 'cancelled')

    def test_hostel_allocation_reset_draft(self):
        """Test resetting a hostel allocation to draft."""
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        allocation.action_cancel()
        allocation.action_draft()
        self.assertEqual(allocation.state, 'draft')

    def test_hostel_allocation_date_validation(self):
        """Test that check-out date must not precede check-in date."""
        with self.assertRaises(ValidationError):
            self.env['op.hostel.allocation'].create({
                'student_id': self.student.id,
                'room_id': self.room.id,
                'check_in_date': '2024-08-15',
                'check_out_date': '2024-08-01',
            })

    def test_room_occupied_count_updates(self):
        """Test that room occupied count is updated when allocation is confirmed."""
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        allocation.action_confirm()
        self.room.invalidate_recordset()
        self.assertEqual(self.room.occupied, 1)
        self.assertEqual(self.room.available, 1)

    def test_maintenance_room_cannot_be_allocated(self):
        """Test that a room under maintenance cannot be allocated."""
        self.room.write({'state': 'maintenance'})
        allocation = self.env['op.hostel.allocation'].create({
            'student_id': self.student.id,
            'room_id': self.room.id,
            'check_in_date': '2024-08-01',
        })
        with self.assertRaises(UserError):
            allocation.action_confirm()
