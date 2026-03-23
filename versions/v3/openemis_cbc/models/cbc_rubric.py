###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
###############################################################################

from odoo import fields, models


class CbcRubric(models.Model):
    _name = 'cbc.rubric'
    _description = 'CBC Rubric Level'
    _order = 'outcome_id, level'

    outcome_id = fields.Many2one(
        'cbc.learning.outcome', string='Learning Outcome',
        required=True, ondelete='cascade')
    level = fields.Selection([
        ('em', 'EM – Exceeds Most Expectations'),
        ('me', 'ME – Meets Expectations'),
        ('ap', 'AP – Approaching Proficiency'),
        ('be', 'BE – Below Expectations'),
    ], string='Performance Level', required=True)
    level_code = fields.Char(
        compute='_compute_level_code', store=True, string='Code')
    descriptor = fields.Text('Descriptor', required=True)
    score = fields.Float('Score', default=0.0)

    def _compute_level_code(self):
        mapping = {'em': 'EM', 'me': 'ME', 'ap': 'AP', 'be': 'BE'}
        for rec in self:
            rec.level_code = mapping.get(rec.level, '')
