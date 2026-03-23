###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
###############################################################################

from odoo import fields, models

CBC_GRADE_LEVELS = [
    ('pp1', 'Pre-Primary 1'),
    ('pp2', 'Pre-Primary 2'),
    ('g1', 'Grade 1'), ('g2', 'Grade 2'), ('g3', 'Grade 3'),
    ('g4', 'Grade 4'), ('g5', 'Grade 5'), ('g6', 'Grade 6'),
    ('g7', 'Grade 7'), ('g8', 'Grade 8'), ('g9', 'Grade 9'),
    ('g10', 'Grade 10'), ('g11', 'Grade 11'), ('g12', 'Grade 12'),
]


class CbcLearningOutcome(models.Model):
    _name = 'cbc.learning.outcome'
    _description = 'CBC Learning Outcome'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'substrand_id, grade_level, sequence'

    name = fields.Char('Learning Outcome', required=True)
    code = fields.Char('Code', size=30)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True)
    substrand_id = fields.Many2one(
        'cbc.substrand', string='Sub-strand', required=True,
        ondelete='cascade')
    strand_id = fields.Many2one(
        related='substrand_id.strand_id', store=True, string='Strand')
    grade_level = fields.Selection(
        CBC_GRADE_LEVELS, string='Grade Level', required=True)
    description = fields.Text('Description')
    rubric_ids = fields.One2many(
        'cbc.rubric', 'outcome_id', string='Rubric Levels')
