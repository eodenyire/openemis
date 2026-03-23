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


class CbcFormativeAssessment(models.Model):
    _name = 'cbc.formative.assessment'
    _description = 'CBC Formative Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name'

    name = fields.Char('Assessment Title', required=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    assessment_type = fields.Selection([
        ('observation', 'Teacher Observation'),
        ('oral', 'Oral Assessment'),
        ('written', 'Written Task'),
        ('project', 'Project / PBL'),
        ('portfolio', 'Portfolio Evidence'),
        ('peer', 'Peer Assessment'),
    ], string='Type', required=True, default='observation')
    grade_level = fields.Selection(
        CBC_GRADE_LEVELS, string='Grade Level', required=True)
    student_id = fields.Many2one(
        'op.student', string='Student', required=True, ondelete='cascade')
    teacher_id = fields.Many2one(
        'op.faculty', string='Teacher', ondelete='set null')
    subject_id = fields.Many2one(
        'op.subject', string='Subject', ondelete='set null')
    outcome_id = fields.Many2one(
        'cbc.learning.outcome', string='Learning Outcome',
        ondelete='set null')
    strand_id = fields.Many2one(
        related='outcome_id.strand_id', store=True, string='Strand')
    performance_level = fields.Selection([
        ('em', 'EM – Exceeds Most Expectations'),
        ('me', 'ME – Meets Expectations'),
        ('ap', 'AP – Approaching Proficiency'),
        ('be', 'BE – Below Expectations'),
    ], string='Performance Level', required=True)
    score = fields.Float('Score', default=0.0)
    max_score = fields.Float('Max Score', default=4.0)
    observations = fields.Text('Teacher Observations / Remarks')
    term = fields.Selection([
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
    ], string='Term', required=True, default='term1')
    academic_year_id = fields.Many2one(
        'op.academic.year', string='Academic Year')
    portfolio_id = fields.Many2one(
        'cbc.portfolio', string='Portfolio', ondelete='set null')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', tracking=True)

    @api.onchange('performance_level')
    def _onchange_performance_level(self):
        level_score = {'em': 4.0, 'me': 3.0, 'ap': 2.0, 'be': 1.0}
        if self.performance_level:
            self.score = level_score.get(self.performance_level, 0.0)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
