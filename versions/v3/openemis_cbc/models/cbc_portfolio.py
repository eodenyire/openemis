###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
###############################################################################

from odoo import fields, models

CBC_GRADE_LEVELS = [
    ('pp1', 'Pre-Primary 1'), ('pp2', 'Pre-Primary 2'),
    ('g1', 'Grade 1'), ('g2', 'Grade 2'), ('g3', 'Grade 3'),
    ('g4', 'Grade 4'), ('g5', 'Grade 5'), ('g6', 'Grade 6'),
    ('g7', 'Grade 7'), ('g8', 'Grade 8'), ('g9', 'Grade 9'),
    ('g10', 'Grade 10'), ('g11', 'Grade 11'), ('g12', 'Grade 12'),
]


class CbcPortfolio(models.Model):
    _name = 'cbc.portfolio'
    _description = 'CBC Student Portfolio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'student_id, academic_year_id, name'

    name = fields.Char('Portfolio Title', required=True)
    student_id = fields.Many2one(
        'op.student', string='Student', required=True, ondelete='cascade')
    grade_level = fields.Selection(
        CBC_GRADE_LEVELS, string='Grade Level', required=True)
    academic_year_id = fields.Many2one(
        'op.academic.year', string='Academic Year')
    term = fields.Selection([
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('annual', 'Annual'),
    ], string='Term', default='annual')
    description = fields.Text('Description / Reflection')
    teacher_comment = fields.Text('Teacher Comment')
    parent_comment = fields.Text('Parent / Guardian Comment')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ], string='Status', default='draft', tracking=True)
    assessment_ids = fields.One2many(
        'cbc.formative.assessment', 'portfolio_id',
        string='Formative Assessments')
    assessment_count = fields.Integer(
        compute='_compute_assessment_count', string='Assessments')
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Evidence Files')

    def _compute_assessment_count(self):
        for rec in self:
            rec.assessment_count = len(rec.assessment_ids)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_review(self):
        self.write({'state': 'reviewed'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
