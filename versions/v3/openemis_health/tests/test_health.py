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


class TestHealth(TransactionCase):
    """Regression tests for the Health module."""

    def setUp(self):
        super(TestHealth, self).setUp()
        partner = self.env['res.partner'].create({'name': 'Health Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'Health',
            'last_name': 'Student',
            'gender': 'm',
            'partner_id': partner.id,
        })
        self.medical_condition = self.env['op.medical.condition'].create({
            'name': 'Asthma',
            'description': 'Chronic respiratory condition',
        })
        self.vaccination = self.env['op.vaccination'].create({
            'name': 'Influenza Vaccine',
            'description': 'Annual flu vaccine',
        })

    def test_medical_condition_create(self):
        """Test creating a medical condition."""
        self.assertEqual(self.medical_condition.name, 'Asthma')
        self.assertTrue(self.medical_condition.active)

    def test_medical_condition_unique(self):
        """Test that medical condition names must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.medical.condition'].create({'name': 'Asthma'})

    def test_vaccination_create(self):
        """Test creating a vaccination record."""
        self.assertEqual(self.vaccination.name, 'Influenza Vaccine')
        self.assertTrue(self.vaccination.active)

    def test_vaccination_unique(self):
        """Test that vaccination names must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.vaccination'].create({'name': 'Influenza Vaccine'})

    def test_student_health_create(self):
        """Test creating a student health record."""
        health = self.env['op.student.health'].create({
            'student_id': self.student.id,
            'blood_group': 'O+',
            'height': 170.0,
            'weight': 65.0,
            'emergency_contact_name': 'Parent Name',
            'emergency_contact_phone': '0700000000',
        })
        self.assertEqual(health.blood_group, 'O+')
        self.assertEqual(health.height, 170.0)

    def test_bmi_computation(self):
        """Test that BMI is correctly computed from height and weight."""
        health = self.env['op.student.health'].create({
            'student_id': self.student.id,
            'height': 175.0,
            'weight': 70.0,
        })
        expected_bmi = round(70.0 / (1.75 ** 2), 2)
        self.assertAlmostEqual(health.bmi, expected_bmi, places=1)

    def test_bmi_zero_without_measurements(self):
        """Test that BMI is zero when height or weight is not provided."""
        health = self.env['op.student.health'].create({
            'student_id': self.student.id,
        })
        self.assertEqual(health.bmi, 0.0)

    def test_health_with_conditions_and_vaccinations(self):
        """Test associating medical conditions and vaccinations with a student."""
        health = self.env['op.student.health'].create({
            'student_id': self.student.id,
            'medical_condition_ids': [(4, self.medical_condition.id)],
            'vaccination_ids': [(4, self.vaccination.id)],
        })
        self.assertIn(self.medical_condition, health.medical_condition_ids)
        self.assertIn(self.vaccination, health.vaccination_ids)
