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


class TestScholarship(TransactionCase):
    """Regression tests for the Scholarship module."""

    def setUp(self):
        super(TestScholarship, self).setUp()
        self.scholarship_type = self.env['op.scholarship.type'].create({
            'name': 'Merit Scholarship',
            'description': 'Awarded based on academic performance',
            'amount': 5000.0,
        })
        partner = self.env['res.partner'].create(
            {'name': 'Scholarship Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'Scholarship',
            'last_name': 'Student',
            'gender': 'f',
            'partner_id': partner.id,
        })

    def test_scholarship_type_create(self):
        """Test creating a scholarship type."""
        self.assertEqual(self.scholarship_type.name, 'Merit Scholarship')
        self.assertEqual(self.scholarship_type.amount, 5000.0)

    def test_scholarship_type_unique(self):
        """Test that scholarship type names must be unique."""
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.scholarship.type'].create({
                'name': 'Merit Scholarship',
            })

    def test_scholarship_create(self):
        """Test creating a scholarship record."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Excellence Award 2024',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-01-01',
            'amount': 5000.0,
        })
        self.assertEqual(scholarship.state, 'draft')
        self.assertEqual(scholarship.name, 'Excellence Award 2024')

    def test_scholarship_workflow_apply(self):
        """Test applying for a scholarship."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Sports Scholarship',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-02-01',
        })
        scholarship.action_apply()
        self.assertEqual(scholarship.state, 'applied')

    def test_scholarship_workflow_approve(self):
        """Test approving a scholarship."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Arts Award',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-03-01',
        })
        scholarship.action_apply()
        scholarship.action_approve()
        self.assertEqual(scholarship.state, 'approved')

    def test_scholarship_workflow_reject(self):
        """Test rejecting a scholarship."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Science Grant',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-04-01',
        })
        scholarship.action_apply()
        scholarship.action_reject()
        self.assertEqual(scholarship.state, 'rejected')

    def test_scholarship_workflow_expire(self):
        """Test expiring a scholarship."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Leadership Award',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-05-01',
        })
        scholarship.action_apply()
        scholarship.action_approve()
        scholarship.action_expire()
        self.assertEqual(scholarship.state, 'expired')

    def test_scholarship_reset_draft_from_rejected(self):
        """Test resetting a scholarship to draft from rejected state."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Innovation Award',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-06-01',
        })
        scholarship.action_apply()
        scholarship.action_reject()
        scholarship.action_reset_draft()
        self.assertEqual(scholarship.state, 'draft')

    def test_scholarship_date_validation(self):
        """Test that end date must not be before start date."""
        with self.assertRaises(ValidationError):
            self.env['op.scholarship'].create({
                'name': 'Bad Dates Scholarship',
                'student_id': self.student.id,
                'scholarship_type_id': self.scholarship_type.id,
                'start_date': '2024-10-01',
                'end_date': '2024-09-01',
            })

    def test_scholarship_cannot_apply_from_non_draft(self):
        """Test that apply action can only be called from draft state."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Test Award',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-07-01',
        })
        scholarship.action_apply()
        with self.assertRaises(ValidationError):
            scholarship.action_apply()

    def test_scholarship_cannot_approve_from_draft(self):
        """Test that approve action requires applied state."""
        scholarship = self.env['op.scholarship'].create({
            'name': 'Another Award',
            'student_id': self.student.id,
            'scholarship_type_id': self.scholarship_type.id,
            'start_date': '2024-08-01',
        })
        with self.assertRaises(ValidationError):
            scholarship.action_approve()
