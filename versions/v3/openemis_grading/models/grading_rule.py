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

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpGradingRule(models.Model):
    _name = "op.grading.rule"
    _description = "Grading Rule"

    name = fields.Char('Grade', required=True)
    min_marks = fields.Float('Minimum Marks (%)', required=True)
    max_marks = fields.Float('Maximum Marks (%)', required=True)
    gpa_point = fields.Float('GPA Points')
    grading_config_id = fields.Many2one(
        'op.grading.config', string='Grade Scale')
    active = fields.Boolean(default=True)
    description = fields.Char('Description')

    @api.constrains('min_marks', 'max_marks')
    def _check_marks(self):
        for rec in self:
            if (rec.min_marks < 0 or rec.min_marks > 100
                    or rec.max_marks < 0 or rec.max_marks > 100):
                raise ValidationError(
                    _('Marks must be between 0 and 100.'))
            if rec.min_marks >= rec.max_marks:
                raise ValidationError(
                    _('Minimum marks must be less than maximum marks.'))
