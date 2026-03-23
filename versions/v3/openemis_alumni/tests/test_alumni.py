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


class TestAlumni(TransactionCase):
    """Regression tests for the Alumni module."""

    def setUp(self):
        super(TestAlumni, self).setUp()
        partner = self.env['res.partner'].create({'name': 'Alumni Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'Alumni',
            'last_name': 'Student',
            'gender': 'f',
            'partner_id': partner.id,
        })

    def test_alumni_create(self):
        """Test creating an alumni record."""
        alumni = self.env['op.alumni'].create({
            'student_id': self.student.id,
            'graduation_year': 2022,
            'employment_status': 'employed',
            'employer_name': 'Tech Company',
            'job_title': 'Software Engineer',
        })
        self.assertEqual(alumni.graduation_year, 2022)
        self.assertEqual(alumni.employment_status, 'employed')
        self.assertEqual(alumni.employer_name, 'Tech Company')

    def test_alumni_unique_per_year(self):
        """Test that duplicate alumni records for same student and year are rejected."""
        from odoo.exceptions import ValidationError
        self.env['op.alumni'].create({
            'student_id': self.student.id,
            'graduation_year': 2021,
        })
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.alumni'].create({
                'student_id': self.student.id,
                'graduation_year': 2021,
            })

    def test_alumni_employment_statuses(self):
        """Test different employment status values."""
        for i, status in enumerate(
                ['employed', 'self_employed', 'unemployed',
                 'further_studies', 'other']):
            partner = self.env['res.partner'].create(
                {'name': 'Student %d' % i})
            student = self.env['op.student'].create({
                'first_name': 'Student',
                'last_name': str(i),
                'gender': 'm',
                'partner_id': partner.id,
            })
            alumni = self.env['op.alumni'].create({
                'student_id': student.id,
                'graduation_year': 2020 + i,
                'employment_status': status,
            })
            self.assertEqual(alumni.employment_status, status)

    def test_alumni_search(self):
        """Test searching alumni records."""
        self.env['op.alumni'].create({
            'student_id': self.student.id,
            'graduation_year': 2023,
        })
        alumni = self.env['op.alumni'].search([
            ('student_id', '=', self.student.id)
        ])
        self.assertTrue(len(alumni) >= 1)

    def test_alumni_archive(self):
        """Test archiving an alumni record."""
        alumni = self.env['op.alumni'].create({
            'student_id': self.student.id,
            'graduation_year': 2019,
        })
        alumni.write({'active': False})
        self.assertFalse(alumni.active)
