###############################################################################
#
#    openEMIS
#    Copyright (C) 2009-TODAY openEMIS(<https://www.openemis.org>).
#
###############################################################################

from odoo import fields, models


class CbcStrand(models.Model):
    _name = 'cbc.strand'
    _description = 'CBC Competency Strand'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char('Strand Name', required=True)
    code = fields.Char('Code', size=10)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True)
    description = fields.Text('Description')
    grade_band = fields.Selection([
        ('lp', 'Lower Primary (Grades 1–3)'),
        ('up', 'Upper Primary (Grades 4–6)'),
        ('js', 'Junior Secondary (Grades 7–9)'),
        ('ss', 'Senior Secondary (Grades 10–12)'),
        ('all', 'All Levels'),
    ], string='Grade Band', default='all')
    subject_id = fields.Many2one(
        'op.subject', string='Subject', ondelete='set null')
    substrand_ids = fields.One2many(
        'cbc.substrand', 'strand_id', string='Sub-strands')
    substrand_count = fields.Integer(
        compute='_compute_substrand_count', string='Sub-strands')

    def _compute_substrand_count(self):
        for rec in self:
            rec.substrand_count = len(rec.substrand_ids)
