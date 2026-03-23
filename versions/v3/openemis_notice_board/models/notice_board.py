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

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpNoticeBoard(models.Model):
    _name = "op.notice.board"
    _description = "Notice Board"
    _rec_name = "title"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc, id desc"

    title = fields.Char(string="Title", required=True, tracking=True)
    notice_type = fields.Selection(
        selection=[
            ('general', 'General'),
            ('academic', 'Academic'),
            ('sports', 'Sports'),
            ('event', 'Event'),
            ('holiday', 'Holiday'),
            ('exam', 'Examination'),
            ('urgent', 'Urgent'),
        ],
        string="Notice Type",
        required=True,
        default='general',
        tracking=True,
    )
    target_audience = fields.Selection(
        selection=[
            ('all', 'All'),
            ('students', 'Students'),
            ('faculty', 'Faculty'),
            ('parents', 'Parents'),
        ],
        string="Target Audience",
        required=True,
        default='all',
        tracking=True,
    )
    course_ids = fields.Many2many(
        'op.course',
        string="Specific Courses",
    )
    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.today,
    )
    end_date = fields.Date(string="End Date")
    description = fields.Html(string="Description")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments",
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string="State",
        default='draft',
        tracking=True,
    )
    published_by = fields.Many2one(
        'res.users',
        string="Published By",
        default=lambda self: self.env.user,
    )
    published_date = fields.Datetime(string="Published Date", readonly=True)
    active = fields.Boolean(default=True)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.end_date < record.start_date:
                raise ValidationError(
                    "End Date must be greater than or equal to Start Date."
                )

    def action_publish(self):
        for record in self:
            record.write({
                'state': 'published',
                'published_date': fields.Datetime.now(),
                'published_by': self.env.user.id,
            })

    def action_expire(self):
        for record in self:
            record.write({'state': 'expired'})

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancelled'})

    def action_reset_draft(self):
        for record in self:
            record.write({'state': 'draft'})
