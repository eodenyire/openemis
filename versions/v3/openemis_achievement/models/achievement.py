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

from odoo import fields, models


class OpAchievement(models.Model):
    _name = "op.achievement"
    _description = "Student Achievement"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_faculty(self):
        return self.env['op.faculty'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1) or False

    name = fields.Char('Achievement', required=True)
    student_id = fields.Many2one('op.student', 'Student', required=True,
                                 tracking=True)
    achievement_type_id = fields.Many2one('op.achievement.type',
                                          string='Achievement Type',
                                          required=True, tracking=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    faculty_id = fields.Many2one('op.faculty', string='Faculty',
                                 default=lambda self: self._default_faculty())
    description = fields.Text('Description')
    award_by = fields.Char('Awarded By', size=256)
    attachment = fields.Binary('Certificate/Attachment')
    attachment_name = fields.Char('Attachment Filename')
    active = fields.Boolean(default=True)
