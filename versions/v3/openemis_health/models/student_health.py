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


class OpStudentHealth(models.Model):
    _name = "op.student.health"
    _description = "Student Health Record"
    _rec_name = "student_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    student_id = fields.Many2one('op.student', 'Student', required=True,
                                 tracking=True)
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve'),
    ], string='Blood Group', tracking=True)
    height = fields.Float('Height (cm)', tracking=True)
    weight = fields.Float('Weight (kg)', tracking=True)
    bmi = fields.Float('BMI', compute='_compute_bmi', store=True)
    medical_condition_ids = fields.Many2many(
        'op.medical.condition', string='Medical Conditions')
    vaccination_ids = fields.Many2many(
        'op.vaccination', string='Vaccinations')
    allergies = fields.Text('Allergies')
    emergency_contact_name = fields.Char('Emergency Contact Name')
    emergency_contact_phone = fields.Char('Emergency Contact Phone')
    emergency_contact_relation = fields.Char('Emergency Contact Relation')
    doctor_name = fields.Char('Doctor Name')
    doctor_phone = fields.Char('Doctor Phone')
    notes = fields.Text('Notes')
    last_checkup_date = fields.Date('Last Checkup Date')
    active = fields.Boolean(default=True)

    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight:
                height_m = record.height / 100.0
                record.bmi = round(record.weight / (height_m ** 2), 2)
            else:
                record.bmi = 0.0
