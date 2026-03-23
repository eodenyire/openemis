###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
###############################################################################

from odoo import api, fields, models

CBC_GRADE_LEVELS = [
    ('pp1', 'Pre-Primary 1'), ('pp2', 'Pre-Primary 2'),
    ('g1', 'Grade 1'), ('g2', 'Grade 2'), ('g3', 'Grade 3'),
    ('g4', 'Grade 4'), ('g5', 'Grade 5'), ('g6', 'Grade 6'),
    ('g7', 'Grade 7'), ('g8', 'Grade 8'), ('g9', 'Grade 9'),
    ('g10', 'Grade 10'), ('g11', 'Grade 11'), ('g12', 'Grade 12'),
]


class CbcReportCard(models.Model):
    _name = 'cbc.report.card'
    _description = 'CBC Competency Report Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'student_id, academic_year_id, term'

    name = fields.Char(
        'Report Card', compute='_compute_name', store=True)
    student_id = fields.Many2one(
        'op.student', string='Student', required=True, ondelete='cascade')
    grade_level = fields.Selection(
        CBC_GRADE_LEVELS, string='Grade Level', required=True)
    academic_year_id = fields.Many2one(
        'op.academic.year', string='Academic Year', required=True)
    term = fields.Selection([
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
    ], string='Term', required=True, default='term1')
    teacher_id = fields.Many2one(
        'op.faculty', string='Class Teacher', ondelete='set null')
    class_teacher_comment = fields.Text('Class Teacher Comment')
    principal_comment = fields.Text("Principal's Comment")
    parent_comment = fields.Text('Parent / Guardian Comment')
    line_ids = fields.One2many(
        'cbc.report.card.line', 'report_card_id', string='Competency Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('acknowledged', 'Acknowledged'),
    ], string='Status', default='draft', tracking=True)
    total_score = fields.Float(
        compute='_compute_total_score', store=True, string='Total Score')
    average_score = fields.Float(
        compute='_compute_total_score', store=True, string='Average Score')

    @api.depends('student_id', 'academic_year_id', 'term')
    def _compute_name(self):
        for rec in self:
            student = rec.student_id.name or ''
            year = rec.academic_year_id.name or ''
            term = dict(rec._fields['term'].selection).get(rec.term, '')
            rec.name = f'{student} – {year} {term}'

    @api.depends('line_ids.score')
    def _compute_total_score(self):
        for rec in self:
            scores = rec.line_ids.mapped('score')
            rec.total_score = sum(scores)
            rec.average_score = sum(scores) / len(scores) if scores else 0.0

    def action_publish(self):
        self.write({'state': 'published'})

    def action_acknowledge(self):
        self.write({'state': 'acknowledged'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class CbcReportCardLine(models.Model):
    _name = 'cbc.report.card.line'
    _description = 'CBC Report Card Competency Line'
    _order = 'report_card_id, strand_id, outcome_id'

    report_card_id = fields.Many2one(
        'cbc.report.card', string='Report Card',
        required=True, ondelete='cascade')
    strand_id = fields.Many2one(
        'cbc.strand', string='Strand', required=True, ondelete='cascade')
    outcome_id = fields.Many2one(
        'cbc.learning.outcome', string='Learning Outcome',
        ondelete='set null')
    performance_level = fields.Selection([
        ('em', 'EM – Exceeds Most Expectations'),
        ('me', 'ME – Meets Expectations'),
        ('ap', 'AP – Approaching Proficiency'),
        ('be', 'BE – Below Expectations'),
    ], string='Performance Level')
    score = fields.Float('Score', default=0.0)
    teacher_remark = fields.Text('Remark')
