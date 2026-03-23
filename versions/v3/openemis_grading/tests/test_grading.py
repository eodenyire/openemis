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


class TestGrading(TransactionCase):
    """Regression tests for the Grading module."""

    def setUp(self):
        super(TestGrading, self).setUp()
        self.grading_config = self.env['op.grading.config'].create({
            'name': 'Standard Grading Scale',
        })

    def test_grading_config_create(self):
        """Test creating a grading configuration."""
        self.assertEqual(self.grading_config.name, 'Standard Grading Scale')
        self.assertTrue(self.grading_config.active)

    def test_grading_rule_create(self):
        """Test creating a grading rule."""
        rule = self.env['op.grading.rule'].create({
            'name': 'A+',
            'min_marks': 90.0,
            'max_marks': 100.0,
            'gpa_point': 4.0,
            'grading_config_id': self.grading_config.id,
        })
        self.assertEqual(rule.name, 'A+')
        self.assertEqual(rule.min_marks, 90.0)
        self.assertEqual(rule.max_marks, 100.0)

    def test_grading_rule_marks_validation(self):
        """Test that marks must be between 0 and 100."""
        with self.assertRaises(ValidationError):
            self.env['op.grading.rule'].create({
                'name': 'Invalid',
                'min_marks': -5.0,
                'max_marks': 50.0,
                'grading_config_id': self.grading_config.id,
            })

    def test_grading_rule_min_less_than_max(self):
        """Test that minimum marks must be less than maximum marks."""
        with self.assertRaises(ValidationError):
            self.env['op.grading.rule'].create({
                'name': 'Bad Rule',
                'min_marks': 80.0,
                'max_marks': 60.0,
                'grading_config_id': self.grading_config.id,
            })

    def test_grading_rule_equal_min_max(self):
        """Test that equal min and max marks are rejected."""
        with self.assertRaises(ValidationError):
            self.env['op.grading.rule'].create({
                'name': 'Equal Rule',
                'min_marks': 50.0,
                'max_marks': 50.0,
                'grading_config_id': self.grading_config.id,
            })

    def test_full_grading_scale(self):
        """Test creating a complete set of grading rules for a config."""
        grade_data = [
            ('A+', 90.0, 100.0, 4.0),
            ('A', 80.0, 90.0, 3.7),
            ('B', 70.0, 80.0, 3.0),
            ('C', 60.0, 70.0, 2.0),
            ('D', 50.0, 60.0, 1.0),
            ('F', 0.0, 50.0, 0.0),
        ]
        for name, min_m, max_m, gpa in grade_data:
            rule = self.env['op.grading.rule'].create({
                'name': name,
                'min_marks': min_m,
                'max_marks': max_m,
                'gpa_point': gpa,
                'grading_config_id': self.grading_config.id,
            })
            self.assertEqual(rule.grading_config_id, self.grading_config)
        self.assertEqual(len(self.grading_config.grading_rule_ids), 6)
