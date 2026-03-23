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
"""
openEMIS ERP – End-to-End Integration Tests
============================================
Validates that all openEMIS modules referenced by openemis_erp are present
and that cross-module workflows (student → exam → result → grading) operate
correctly end-to-end.
"""

from datetime import date

from odoo.tests.common import TransactionCase


class TestERPModulePresence(TransactionCase):
    """Verify that every module declared as a dependency of openemis_erp is
    installed and accessible."""

    ERP_DEPS = [
        "openemis_achievement",
        "openemis_admission",
        "openemis_activity",
        "openemis_alumni",
        "openemis_assignment",
        "openemis_attendance",
        "openemis_blog",
        "openemis_cafeteria",
        "openemis_classroom",
        "openemis_digiguide",
        "openemis_discipline",
        "openemis_event",
        "openemis_facility",
        "openemis_fees",
        "openemis_grading",
        "openemis_health",
        "openemis_hostel",
        "openemis_inventory",
        "openemis_lesson",
        "openemis_library",
        "openemis_lms",
        "openemis_mentorship",
        "openemis_notice_board",
        "openemis_parent",
        "openemis_exam",
        "openemis_scholarship",
        "openemis_timetable",
        "openemis_transportation",
    ]

    def test_all_dependency_modules_installed(self):
        """All modules that openemis_erp depends on must be installed."""
        installed = set(
            self.env["ir.module.module"]
            .search([["name", "in", self.ERP_DEPS], ["state", "=", "installed"]])
            .mapped("name")
        )
        missing = set(self.ERP_DEPS) - installed
        self.assertFalse(
            missing,
            f"The following openemis_erp dependency modules are NOT installed: "
            f"{sorted(missing)}",
        )


class TestERPStudentWorkflow(TransactionCase):
    """End-to-end student data integrity tests across core EMIS modules."""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({
            "name": "ERP Integration Student",
            "email": "erp_integration@openemis.example.com",
        })
        self.student = self.env["op.student"].create({
            "first_name": "ERPIntegration",
            "last_name": "TestStudent",
            "gender": "m",
            "birth_date": "2004-06-15",
            "partner_id": self.partner.id,
        })

    def test_student_created_with_partner(self):
        """Student record must be linked to a res.partner."""
        self.assertTrue(self.student.partner_id)
        self.assertEqual(self.student.partner_id.id, self.partner.id)

    def test_student_active_by_default(self):
        """Newly created students should be active."""
        self.assertTrue(self.student.active)

    def test_student_archive_and_restore(self):
        """Students can be archived (active=False) and restored."""
        self.student.active = False
        self.assertFalse(self.student.active)
        self.student.active = True
        self.assertTrue(self.student.active)

    def test_student_name_fields(self):
        """First name and last name are stored correctly."""
        self.assertEqual(self.student.first_name, "ERPIntegration")
        self.assertEqual(self.student.last_name, "TestStudent")


class TestERPExamToResultWorkflow(TransactionCase):
    """Tests the full exam → marksheet → result pipeline."""

    def setUp(self):
        super().setUp()
        # Create prerequisite partner + student
        partner = self.env["res.partner"].create({"name": "Result Test Student"})
        self.student = self.env["op.student"].create({
            "first_name": "Result",
            "last_name": "TestStudent",
            "gender": "f",
            "partner_id": partner.id,
        })
        # Course and batch
        self.course = self.env["op.course"].create({
            "name": "ERP Test Course",
            "code": "ERP-TEST-001",
        })
        self.batch = self.env["op.batch"].create({
            "name": "ERP Test Batch",
            "code": "ERP-BATCH-001",
            "course_id": self.course.id,
            "start_date": "2024-08-01",
            "end_date": "2025-07-31",
        })
        # Subject
        self.subject = self.env["op.subject"].create({
            "name": "ERP Test Subject",
            "code": "ERP-SUBJ-001",
        })
        # Exam type and session
        self.exam_type = self.env["op.exam.type"].create({
            "name": "ERP Test Exam Type",
            "code": "ERP-EXT-001",
        })
        self.exam_session = self.env["op.exam.session"].create({
            "name": "ERP Test Exam Session",
            "start_date": "2024-11-01",
            "end_date": "2024-11-15",
            "exam_type": self.exam_type.id,
            "course_id": self.course.id,
            "batch_id": self.batch.id,
        })

    def test_exam_session_created(self):
        """Exam session should be created with correct fields."""
        self.assertEqual(self.exam_session.name, "ERP Test Exam Session")
        self.assertEqual(self.exam_session.course_id.id, self.course.id)

    def test_exam_created_under_session(self):
        """An exam can be created and linked to the session."""
        exam = self.env["op.exam"].create({
            "name": "ERP Mid-Term Exam",
            "session_id": self.exam_session.id,
            "course_id": self.course.id,
            "batch_id": self.batch.id,
            "subject_id": self.subject.id,
            "start_time": "2024-11-05 09:00:00",
            "end_time": "2024-11-05 12:00:00",
            "total_marks": 100,
            "min_marks": 50,
        })
        self.assertEqual(exam.session_id.id, self.exam_session.id)
        self.assertEqual(exam.total_marks, 100)

    def test_marksheet_register_created(self):
        """A marksheet register can be created for an exam session."""
        register = self.env["op.marksheet.register"].create({
            "name": "ERP Test Marksheet",
            "exam_session_id": self.exam_session.id,
        })
        self.assertEqual(register.exam_session_id.id, self.exam_session.id)

    def test_marksheet_line_and_result(self):
        """Marksheet line and result line can be created for a student."""
        register = self.env["op.marksheet.register"].create({
            "name": "ERP Result Register",
            "exam_session_id": self.exam_session.id,
        })
        exam = self.env["op.exam"].create({
            "name": "ERP Final Exam",
            "session_id": self.exam_session.id,
            "course_id": self.course.id,
            "batch_id": self.batch.id,
            "subject_id": self.subject.id,
            "start_time": "2024-11-10 09:00:00",
            "end_time": "2024-11-10 12:00:00",
            "total_marks": 100,
            "min_marks": 50,
        })
        ml = self.env["op.marksheet.line"].create({
            "marksheet_reg_id": register.id,
            "student_id": self.student.id,
        })
        result = self.env["op.result.line"].create({
            "marksheet_line_id": ml.id,
            "exam_id": exam.id,
            "student_id": self.student.id,
            "marks": 78,
            "status": "pass",
        })
        self.assertEqual(result.marks, 78)
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.student_id.id, self.student.id)


class TestERPDisciplineWorkflow(TransactionCase):
    """Tests discipline record creation and state transitions."""

    def setUp(self):
        super().setUp()
        partner = self.env["res.partner"].create({"name": "Discipline Test Student"})
        self.student = self.env["op.student"].create({
            "first_name": "Discipline",
            "last_name": "TestStudent",
            "gender": "m",
            "partner_id": partner.id,
        })
        self.category = self.env["op.misbehaviour.category"].create({
            "name": "ERP Test Category",
            "description": "Test misbehaviour for ERP regression",
        })
        self.action = self.env["op.discipline.action"].create({
            "name": "ERP Test Action",
            "description": "Test disciplinary action for ERP regression",
        })

    def test_discipline_record_reported(self):
        """A discipline record can be created in 'reported' state."""
        disc = self.env["op.discipline"].create({
            "student_id": self.student.id,
            "misbehaviour_category_id": self.category.id,
            "discipline_action_id": self.action.id,
            "date": date.today().strftime("%Y-%m-%d"),
            "description": "ERP integration test – discipline event",
            "state": "reported",
        })
        self.assertEqual(disc.state, "reported")
        self.assertEqual(disc.student_id.id, self.student.id)

    def test_discipline_state_transition_to_review(self):
        """Discipline record state can be changed to 'under_review'."""
        disc = self.env["op.discipline"].create({
            "student_id": self.student.id,
            "misbehaviour_category_id": self.category.id,
            "discipline_action_id": self.action.id,
            "date": date.today().strftime("%Y-%m-%d"),
            "description": "ERP state-transition test",
            "state": "reported",
        })
        disc.state = "under_review"
        self.assertEqual(disc.state, "under_review")


class TestERPGradingWorkflow(TransactionCase):
    """Tests grading configuration and rule lookup."""

    def setUp(self):
        super().setUp()
        self.grading_config = self.env["op.grading.config"].create({
            "name": "ERP Test Grade Scale",
        })

    def test_grading_rules_created(self):
        """Multiple grading rules can be created for a config."""
        rules = [
            ("A+", 90.0, 100.0, 4.0, "Outstanding"),
            ("A",  80.0,  89.0, 3.7, "Distinction"),
            ("B",  70.0,  79.0, 3.0, "Merit"),
            ("C",  60.0,  69.0, 2.0, "Pass"),
            ("D",  50.0,  59.0, 1.0, "Marginal Pass"),
            ("F",   0.0,  49.0, 0.0, "Fail"),
        ]
        created = []
        for name, mn, mx, gpa, desc in rules:
            rule = self.env["op.grading.rule"].create({
                "name": name,
                "min_marks": mn,
                "max_marks": mx,
                "gpa_point": gpa,
                "description": desc,
                "grading_config_id": self.grading_config.id,
            })
            created.append(rule)

        self.assertEqual(len(created), 6)
        grade_names = [r.name for r in created]
        self.assertIn("A+", grade_names)
        self.assertIn("F", grade_names)

    def test_grading_config_unique(self):
        """Grading config must have a unique name."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env["op.grading.config"].create({"name": "ERP Test Grade Scale"})
