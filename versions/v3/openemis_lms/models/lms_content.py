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


class OpLmsContent(models.Model):
    _name = "op.lms.content"
    _description = "LMS Section Content"
    _order = "sequence, id"

    name = fields.Char('Content Title', required=True)
    lms_section_id = fields.Many2one(
        'op.lms.section', string='Section', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    content_type = fields.Selection(
        [('document', 'Document'), ('video', 'Video'),
         ('link', 'External Link'), ('quiz', 'Quiz'),
         ('assignment', 'Assignment')],
        string='Content Type', required=True, default='document')
    description = fields.Text('Description')
    document = fields.Binary('File Attachment')
    document_name = fields.Char('File Name')
    url = fields.Char('URL')
    duration = fields.Float('Duration (minutes)')
    active = fields.Boolean(default=True)
