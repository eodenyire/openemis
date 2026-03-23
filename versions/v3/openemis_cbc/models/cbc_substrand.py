###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
###############################################################################

from odoo import fields, models


class CbcSubstrand(models.Model):
    _name = 'cbc.substrand'
    _description = 'CBC Sub-strand'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'strand_id, sequence, name'

    name = fields.Char('Sub-strand Name', required=True)
    code = fields.Char('Code', size=20)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True)
    strand_id = fields.Many2one(
        'cbc.strand', string='Strand', required=True, ondelete='cascade')
    description = fields.Text('Description')
    outcome_ids = fields.One2many(
        'cbc.learning.outcome', 'substrand_id', string='Learning Outcomes')
    outcome_count = fields.Integer(
        compute='_compute_outcome_count', string='Outcomes')

    def _compute_outcome_count(self):
        for rec in self:
            rec.outcome_count = len(rec.outcome_ids)
