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


class TestNoticeBoard(TransactionCase):
    """Regression tests for the Notice Board module."""

    def test_notice_create(self):
        """Test creating a notice board entry."""
        notice = self.env['op.notice.board'].create({
            'title': 'School Closed Tomorrow',
            'notice_type': 'general',
            'target_audience': 'all',
            'start_date': '2024-09-10',
        })
        self.assertEqual(notice.state, 'draft')
        self.assertEqual(notice.notice_type, 'general')

    def test_notice_publish(self):
        """Test publishing a notice."""
        notice = self.env['op.notice.board'].create({
            'title': 'Exam Schedule Released',
            'notice_type': 'exam',
            'target_audience': 'students',
            'start_date': '2024-10-01',
        })
        notice.action_publish()
        self.assertEqual(notice.state, 'published')
        self.assertTrue(notice.published_date)

    def test_notice_expire(self):
        """Test expiring a notice."""
        notice = self.env['op.notice.board'].create({
            'title': 'Holiday Notice',
            'notice_type': 'holiday',
            'target_audience': 'all',
            'start_date': '2024-08-01',
        })
        notice.action_publish()
        notice.action_expire()
        self.assertEqual(notice.state, 'expired')

    def test_notice_cancel(self):
        """Test cancelling a notice."""
        notice = self.env['op.notice.board'].create({
            'title': 'Event Cancelled',
            'notice_type': 'event',
            'target_audience': 'all',
            'start_date': '2024-11-01',
        })
        notice.action_cancel()
        self.assertEqual(notice.state, 'cancelled')

    def test_notice_reset_draft(self):
        """Test resetting a notice to draft state."""
        notice = self.env['op.notice.board'].create({
            'title': 'Sports Day Notice',
            'notice_type': 'sports',
            'target_audience': 'students',
            'start_date': '2024-11-15',
        })
        notice.action_publish()
        notice.action_reset_draft()
        self.assertEqual(notice.state, 'draft')

    def test_notice_date_validation(self):
        """Test that end date must not be before start date."""
        with self.assertRaises(ValidationError):
            self.env['op.notice.board'].create({
                'title': 'Invalid Notice',
                'notice_type': 'general',
                'target_audience': 'all',
                'start_date': '2024-10-15',
                'end_date': '2024-10-01',
            })

    def test_notice_different_types(self):
        """Test creating notices of each type."""
        types = ['general', 'academic', 'sports', 'event',
                 'holiday', 'exam', 'urgent']
        for notice_type in types:
            notice = self.env['op.notice.board'].create({
                'title': 'Notice: %s' % notice_type,
                'notice_type': notice_type,
                'target_audience': 'all',
                'start_date': '2024-09-01',
            })
            self.assertEqual(notice.notice_type, notice_type)

    def test_notice_different_audiences(self):
        """Test creating notices for each target audience."""
        audiences = ['all', 'students', 'faculty', 'parents']
        for i, audience in enumerate(audiences):
            notice = self.env['op.notice.board'].create({
                'title': 'Notice for %s' % audience,
                'notice_type': 'general',
                'target_audience': audience,
                'start_date': '2024-09-0%d' % (i + 1),
            })
            self.assertEqual(notice.target_audience, audience)
