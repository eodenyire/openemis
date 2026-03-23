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


class TestLms(TransactionCase):
    """Regression tests for the LMS module."""

    def setUp(self):
        super(TestLms, self).setUp()
        partner = self.env['res.partner'].create({'name': 'LMS Faculty'})
        self.faculty = self.env['op.faculty'].create({
            'partner_id': partner.id,
            'first_name': 'LMS',
            'last_name': 'Faculty',
            'gender': 'male',
        })
        self.lms_course = self.env['op.lms.course'].create({
            'name': 'Python Programming',
            'code': 'LMS-PY-001',
            'faculty_id': self.faculty.id,
        })
        partner_s = self.env['res.partner'].create({'name': 'LMS Student'})
        self.student = self.env['op.student'].create({
            'first_name': 'LMS',
            'last_name': 'Student',
            'gender': 'f',
            'partner_id': partner_s.id,
        })

    def test_lms_course_create(self):
        """Test creating an LMS course."""
        self.assertEqual(self.lms_course.name, 'Python Programming')
        self.assertEqual(self.lms_course.state, 'draft')
        self.assertEqual(self.lms_course.section_count, 0)
        self.assertEqual(self.lms_course.enrollment_count, 0)

    def test_lms_course_code_unique(self):
        """Test that LMS course codes must be unique."""
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.lms.course'].create({
                'name': 'Another Python Course',
                'code': 'LMS-PY-001',
                'faculty_id': self.faculty.id,
            })

    def test_lms_course_workflow(self):
        """Test LMS course state transitions."""
        self.lms_course.action_publish()
        self.assertEqual(self.lms_course.state, 'published')
        self.lms_course.action_archive_course()
        self.assertEqual(self.lms_course.state, 'archived')
        self.lms_course.action_reset_draft()
        self.assertEqual(self.lms_course.state, 'draft')

    def test_lms_section_create(self):
        """Test creating an LMS section."""
        section = self.env['op.lms.section'].create({
            'name': 'Chapter 1: Introduction',
            'lms_course_id': self.lms_course.id,
            'sequence': 1,
        })
        self.assertEqual(section.name, 'Chapter 1: Introduction')
        self.lms_course.invalidate_recordset()
        self.assertEqual(self.lms_course.section_count, 1)

    def test_lms_enrollment_create(self):
        """Test enrolling a student in an LMS course."""
        enrollment = self.env['op.lms.enrollment'].create({
            'student_id': self.student.id,
            'lms_course_id': self.lms_course.id,
            'enrollment_date': '2024-09-01',
        })
        self.assertEqual(enrollment.status, 'enrolled')
        self.assertEqual(enrollment.completion_percentage, 0.0)
        self.lms_course.invalidate_recordset()
        self.assertEqual(self.lms_course.enrollment_count, 1)

    def test_lms_enrollment_unique(self):
        """Test that a student can only be enrolled once in the same LMS course."""
        self.env['op.lms.enrollment'].create({
            'student_id': self.student.id,
            'lms_course_id': self.lms_course.id,
            'enrollment_date': '2024-09-01',
        })
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.lms.enrollment'].create({
                'student_id': self.student.id,
                'lms_course_id': self.lms_course.id,
                'enrollment_date': '2024-09-02',
            })

    def test_open_lms_sections_action(self):
        """Test that open_lms_sections returns a window action."""
        action = self.lms_course.open_lms_sections()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'op.lms.section')

    def test_open_lms_enrollments_action(self):
        """Test that open_lms_enrollments returns a window action."""
        action = self.lms_course.open_lms_enrollments()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'op.lms.enrollment')
