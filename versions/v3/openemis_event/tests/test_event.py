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

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEvent(TransactionCase):
    """Regression tests for the Event module."""

    def setUp(self):
        super(TestEvent, self).setUp()
        self.event_type = self.env['op.event.type'].create({
            'name': 'Annual Day',
            'description': 'Annual school celebration',
        })

    def test_event_type_create(self):
        """Test creating an event type."""
        self.assertEqual(self.event_type.name, 'Annual Day')
        self.assertTrue(self.event_type.active)

    def test_event_type_unique(self):
        """Test that event type names must be unique."""
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.event.type'].create({'name': 'Annual Day'})

    def test_event_create(self):
        """Test creating an event."""
        event = self.env['op.event'].create({
            'name': 'Annual Sports Day',
            'event_type_id': self.event_type.id,
            'start_date': '2024-11-15 09:00:00',
            'end_date': '2024-11-15 17:00:00',
            'venue': 'School Grounds',
            'target_audience': 'all',
        })
        self.assertEqual(event.state, 'draft')
        self.assertEqual(event.name, 'Annual Sports Day')

    def test_event_date_validation(self):
        """Test that end date must not be before start date."""
        with self.assertRaises(ValidationError):
            self.env['op.event'].create({
                'name': 'Invalid Event',
                'event_type_id': self.event_type.id,
                'start_date': '2024-11-15 17:00:00',
                'end_date': '2024-11-15 09:00:00',
            })

    def test_event_workflow(self):
        """Test event state transitions through its lifecycle."""
        event = self.env['op.event'].create({
            'name': 'Science Exhibition',
            'event_type_id': self.event_type.id,
            'start_date': '2024-12-01 08:00:00',
            'end_date': '2024-12-01 16:00:00',
        })
        self.assertEqual(event.state, 'draft')
        event.action_publish()
        self.assertEqual(event.state, 'published')
        event.action_start()
        self.assertEqual(event.state, 'ongoing')
        event.action_complete()
        self.assertEqual(event.state, 'completed')

    def test_event_cancel_and_reset(self):
        """Test event cancellation and reset to draft."""
        event = self.env['op.event'].create({
            'name': 'Art Fair',
            'event_type_id': self.event_type.id,
            'start_date': '2024-10-10 10:00:00',
            'end_date': '2024-10-10 15:00:00',
        })
        event.action_publish()
        event.action_cancel()
        self.assertEqual(event.state, 'cancelled')
        event.action_reset_draft()
        self.assertEqual(event.state, 'draft')

    def test_event_registration(self):
        """Test creating an event registration."""
        event = self.env['op.event'].create({
            'name': 'Drama Festival',
            'event_type_id': self.event_type.id,
            'start_date': '2024-10-20 09:00:00',
            'end_date': '2024-10-20 18:00:00',
        })
        partner = self.env['res.partner'].create({'name': 'Event Student'})
        student = self.env['op.student'].create({
            'first_name': 'Event',
            'last_name': 'Student',
            'gender': 'f',
            'partner_id': partner.id,
        })
        registration = self.env['op.event.registration'].create({
            'event_id': event.id,
            'student_id': student.id,
            'attendee_name': 'Event Student',
        })
        self.assertEqual(registration.state, 'registered')
        self.assertEqual(event.registered_count, 1)

    def test_event_registration_workflow(self):
        """Test event registration state transitions."""
        event = self.env['op.event'].create({
            'name': 'Tech Talk',
            'event_type_id': self.event_type.id,
            'start_date': '2024-11-01 14:00:00',
            'end_date': '2024-11-01 16:00:00',
        })
        registration = self.env['op.event.registration'].create({
            'event_id': event.id,
            'attendee_name': 'Guest Speaker',
        })
        registration.action_mark_attended()
        self.assertEqual(registration.state, 'attended')
        self.assertTrue(registration.attended)
        registration.action_reset_registered()
        self.assertEqual(registration.state, 'registered')
        self.assertFalse(registration.attended)
        registration.action_cancel()
        self.assertEqual(registration.state, 'cancelled')

    def test_event_open_registrations_action(self):
        """Test that open_registrations returns a window action."""
        event = self.env['op.event'].create({
            'name': 'Open Day',
            'event_type_id': self.event_type.id,
            'start_date': '2024-12-10 09:00:00',
            'end_date': '2024-12-10 14:00:00',
        })
        action = event.action_open_registrations()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'op.event.registration')
