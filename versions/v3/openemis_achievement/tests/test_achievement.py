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


class TestAchievement(TransactionCase):
    """Regression tests for the Achievement module."""

    def setUp(self):
        super(TestAchievement, self).setUp()
        partner = self.env['res.partner'].create({'name': 'Test Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'Test',
            'last_name': 'Student',
            'gender': 'm',
            'partner_id': partner.id,
        })
        self.achievement_type = self.env['op.achievement.type'].create({
            'name': 'Academic Excellence',
            'description': 'For outstanding academic performance',
        })

    def test_achievement_type_create(self):
        """Test that an achievement type can be created."""
        self.assertEqual(self.achievement_type.name, 'Academic Excellence')
        self.assertTrue(self.achievement_type.active)

    def test_achievement_type_unique(self):
        """Test that achievement type names must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.achievement.type'].create({
                'name': 'Academic Excellence',
            })

    def test_achievement_create(self):
        """Test that a student achievement record can be created."""
        achievement = self.env['op.achievement'].create({
            'name': 'First Place in Science Fair',
            'student_id': self.student.id,
            'achievement_type_id': self.achievement_type.id,
            'date': '2024-03-01',
            'award_by': 'Principal',
        })
        self.assertEqual(achievement.name, 'First Place in Science Fair')
        self.assertEqual(achievement.student_id, self.student)
        self.assertEqual(achievement.achievement_type_id, self.achievement_type)

    def test_achievement_search(self):
        """Test searching achievement records."""
        self.env['op.achievement'].create({
            'name': 'Best Athlete Award',
            'student_id': self.student.id,
            'achievement_type_id': self.achievement_type.id,
            'date': '2024-05-15',
        })
        achievements = self.env['op.achievement'].search([
            ('student_id', '=', self.student.id)
        ])
        self.assertTrue(len(achievements) >= 1)

    def test_achievement_archive(self):
        """Test archiving an achievement record."""
        achievement = self.env['op.achievement'].create({
            'name': 'Leadership Award',
            'student_id': self.student.id,
            'achievement_type_id': self.achievement_type.id,
            'date': '2024-06-01',
        })
        achievement.write({'active': False})
        self.assertFalse(achievement.active)
