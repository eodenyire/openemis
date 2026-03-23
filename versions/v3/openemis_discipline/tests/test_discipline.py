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


class TestDiscipline(TransactionCase):
    """Regression tests for the Discipline module."""

    def setUp(self):
        super(TestDiscipline, self).setUp()
        partner = self.env['res.partner'].create({'name': 'Discipline Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'Discipline',
            'last_name': 'Student',
            'gender': 'm',
            'partner_id': partner.id,
        })
        self.misbehaviour_category = self.env[
            'op.misbehaviour.category'].create({
            'name': 'Tardiness',
            'description': 'Frequent late arrival',
        })
        self.discipline_action = self.env['op.discipline.action'].create({
            'name': 'Verbal Warning',
            'description': 'A formal verbal warning',
        })

    def test_misbehaviour_category_create(self):
        """Test creating a misbehaviour category."""
        self.assertEqual(self.misbehaviour_category.name, 'Tardiness')
        self.assertTrue(self.misbehaviour_category.active)

    def test_misbehaviour_category_unique(self):
        """Test that misbehaviour category names must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.misbehaviour.category'].create({'name': 'Tardiness'})

    def test_discipline_action_create(self):
        """Test creating a discipline action."""
        self.assertEqual(self.discipline_action.name, 'Verbal Warning')
        self.assertTrue(self.discipline_action.active)

    def test_discipline_action_unique(self):
        """Test that discipline action names must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.discipline.action'].create({
                'name': 'Verbal Warning'
            })

    def test_discipline_record_create(self):
        """Test creating a discipline record."""
        record = self.env['op.discipline'].create({
            'student_id': self.student.id,
            'date': '2024-04-10',
            'misbehaviour_category_id': self.misbehaviour_category.id,
            'discipline_action_id': self.discipline_action.id,
        })
        self.assertEqual(record.state, 'reported')
        self.assertEqual(record.student_id, self.student)

    def test_discipline_workflow(self):
        """Test the full discipline workflow state transitions."""
        record = self.env['op.discipline'].create({
            'student_id': self.student.id,
            'date': '2024-04-15',
            'misbehaviour_category_id': self.misbehaviour_category.id,
        })
        self.assertEqual(record.state, 'reported')
        record.action_review()
        self.assertEqual(record.state, 'under_review')
        record.action_taken()
        self.assertEqual(record.state, 'action_taken')
        record.action_resolve()
        self.assertEqual(record.state, 'resolved')

    def test_discipline_search(self):
        """Test searching discipline records."""
        self.env['op.discipline'].create({
            'student_id': self.student.id,
            'date': '2024-05-01',
            'misbehaviour_category_id': self.misbehaviour_category.id,
        })
        records = self.env['op.discipline'].search([
            ('student_id', '=', self.student.id)
        ])
        self.assertTrue(len(records) >= 1)
