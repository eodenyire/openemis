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

{
    'name': 'openEMIS CBC – Competency Based Curriculum',
    'version': '18.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 4,
    'summary': (
        'Kenya CBC competency tracking, learning outcomes, formative '
        'assessments, portfolios and rubric-based grading for Grades 1–12'
    ),
    'description': """
CBC – Competency Based Curriculum
===================================
This module implements the full Kenya Competency Based Curriculum (CBC)
assessment framework for Grades 1–12, covering:

* **Competency Strands** – The seven core competency areas defined by KICD
  (Communication, Critical Thinking, Creativity, Citizenship, Learning to
  Learn, Digital Literacy, Self-Efficacy) plus subject-specific strands.
* **Sub-strands** – Fine-grained learning expectations nested under each
  strand.
* **Learning Outcomes** – Measurable outcomes aligned to CBC grade bands
  (Lower Primary 1-3, Upper Primary 4-6, Junior Secondary 7-9, Senior
  Secondary 10-12).
* **Formative Assessments** – Teacher observation records, class activities,
  project-based tasks and oral assessments.
* **Student Portfolios** – Collection of evidence artefacts (files, notes)
  demonstrating competency attainment.
* **Rubric-Based Scoring** – Four-level CBC performance rubrics
  (EM/AP/ME/EE) per competency / learning outcome.
* **CBC Report Cards** – Termly competency progress report for parents.
    """,
    'author': 'openEMIS',
    'website': 'https://www.openemis.org',
    'depends': [
        'openemis_exam',
        'openemis_grading',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'data/cbc_data.xml',
        'views/cbc_strand_view.xml',
        'views/cbc_substrand_view.xml',
        'views/cbc_learning_outcome_view.xml',
        'views/cbc_rubric_view.xml',
        'views/cbc_formative_assessment_view.xml',
        'views/cbc_portfolio_view.xml',
        'views/cbc_report_card_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/cbc_demo.xml',
    ],
    'images': [
        'static/description/openemis_cbc_banner.png',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
