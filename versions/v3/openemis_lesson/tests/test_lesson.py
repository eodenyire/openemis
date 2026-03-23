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


class TestLesson(TransactionCase):
    """Regression tests for the Lesson module."""

    def setUp(self):
        super(TestLesson, self).setUp()
        partner = self.env['res.partner'].create({'name': 'Lesson Faculty'})
        self.faculty = self.env['op.faculty'].create({
            'partner_id': partner.id,
            'first_name': 'Lesson',
            'last_name': 'Faculty',
            'gender': 'male',
        })
        self.course = self.env['op.course'].create({
            'name': 'Mathematics',
            'code': 'MATH-101',
        })
        self.subject = self.env['op.subject'].create({
            'name': 'Algebra',
            'code': 'MATH-ALG',
        })

    def test_lesson_create(self):
        """Test creating a lesson plan."""
        lesson = self.env['op.lesson'].create({
            'name': 'Introduction to Algebra',
            'faculty_id': self.faculty.id,
            'course_id': self.course.id,
            'subject_id': self.subject.id,
            'lesson_date': '2024-09-10',
            'topic': 'Variables and Expressions',
            'duration': 1.5,
            'teaching_method': 'lecture',
        })
        self.assertEqual(lesson.state, 'draft')
        self.assertEqual(lesson.name, 'Introduction to Algebra')

    def test_lesson_workflow(self):
        """Test lesson state transitions: draft -> planned -> completed."""
        lesson = self.env['op.lesson'].create({
            'name': 'Quadratic Equations',
            'faculty_id': self.faculty.id,
            'course_id': self.course.id,
            'subject_id': self.subject.id,
            'lesson_date': '2024-09-15',
            'topic': 'Solving Quadratics',
        })
        lesson.action_plan()
        self.assertEqual(lesson.state, 'planned')
        lesson.action_complete()
        self.assertEqual(lesson.state, 'completed')

    def test_lesson_reset_draft(self):
        """Test resetting a lesson to draft state."""
        lesson = self.env['op.lesson'].create({
            'name': 'Geometry Basics',
            'faculty_id': self.faculty.id,
            'course_id': self.course.id,
            'subject_id': self.subject.id,
            'lesson_date': '2024-09-20',
            'topic': 'Shapes and Angles',
        })
        lesson.action_plan()
        lesson.action_reset_draft()
        self.assertEqual(lesson.state, 'draft')

    def test_lesson_cannot_complete_from_draft(self):
        """Test that a lesson cannot be marked completed directly from draft."""
        lesson = self.env['op.lesson'].create({
            'name': 'Trigonometry',
            'faculty_id': self.faculty.id,
            'course_id': self.course.id,
            'subject_id': self.subject.id,
            'lesson_date': '2024-10-01',
            'topic': 'Sine, Cosine, Tangent',
        })
        with self.assertRaises(ValidationError):
            lesson.action_complete()

    def test_lesson_cannot_plan_from_completed(self):
        """Test that a completed lesson cannot be moved to planned state directly."""
        lesson = self.env['op.lesson'].create({
            'name': 'Calculus',
            'faculty_id': self.faculty.id,
            'course_id': self.course.id,
            'subject_id': self.subject.id,
            'lesson_date': '2024-10-05',
            'topic': 'Derivatives',
        })
        lesson.action_plan()
        lesson.action_complete()
        with self.assertRaises(ValidationError):
            lesson.action_plan()

    def test_lesson_negative_duration_rejected(self):
        """Test that a negative duration is rejected."""
        with self.assertRaises(ValidationError):
            self.env['op.lesson'].create({
                'name': 'Invalid Duration',
                'faculty_id': self.faculty.id,
                'course_id': self.course.id,
                'subject_id': self.subject.id,
                'lesson_date': '2024-10-10',
                'topic': 'Test Topic',
                'duration': -1.0,
            })
