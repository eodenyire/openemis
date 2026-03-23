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

from odoo.tests.common import TransactionCase


class TestTransportation(TransactionCase):
    """Regression tests for the Transportation module."""

    def setUp(self):
        super(TestTransportation, self).setUp()
        self.vehicle = self.env['op.transport.vehicle'].create({
            'name': 'School Bus 01',
            'registration_number': 'KAA 123A',
            'vehicle_type': 'bus',
            'capacity': 40,
            'driver_name': 'John Driver',
        })
        self.route = self.env['op.transport.route'].create({
            'name': 'Route North',
            'code': 'RT-N001',
            'vehicle_id': self.vehicle.id,
            'departure_time': 7.0,
            'return_time': 17.0,
        })

    def test_vehicle_create(self):
        """Test creating a transport vehicle."""
        self.assertEqual(self.vehicle.name, 'School Bus 01')
        self.assertEqual(self.vehicle.vehicle_type, 'bus')
        self.assertEqual(self.vehicle.capacity, 40)

    def test_vehicle_registration_unique(self):
        """Test that vehicle registration numbers must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.transport.vehicle'].create({
                'name': 'Another Bus',
                'registration_number': 'KAA 123A',
                'vehicle_type': 'bus',
            })

    def test_route_create(self):
        """Test creating a transport route."""
        self.assertEqual(self.route.name, 'Route North')
        self.assertEqual(self.route.code, 'RT-N001')
        self.assertEqual(self.route.vehicle_id, self.vehicle)

    def test_route_code_unique(self):
        """Test that route codes must be unique."""
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env['op.transport.route'].create({
                'name': 'Duplicate Route',
                'code': 'RT-N001',
            })

    def test_route_stop_create(self):
        """Test creating a route stop."""
        stop = self.env['op.transport.route.stop'].create({
            'name': 'City Center',
            'route_id': self.route.id,
            'sequence': 10,
            'arrival_time': 15.0,
            'landmark': 'Near Post Office',
        })
        self.assertEqual(stop.name, 'City Center')
        self.assertIn(stop, self.route.stop_ids)

    def test_multiple_route_stops(self):
        """Test creating multiple ordered stops on a route."""
        stops_data = [
            ('School Gate', 1, 0.0),
            ('Market Square', 2, 10.0),
            ('Residential Area A', 3, 20.0),
            ('Terminal Stop', 4, 30.0),
        ]
        for name, seq, time in stops_data:
            self.env['op.transport.route.stop'].create({
                'name': name,
                'route_id': self.route.id,
                'sequence': seq,
                'arrival_time': time,
            })
        self.route.invalidate_recordset()
        self.assertEqual(len(self.route.stop_ids), 4)

    def test_student_transport_assignment(self):
        """Test assigning a student to a transport route."""
        partner = self.env['res.partner'].create({'name': 'Transport Student'})
        student = self.env['op.student'].create({
            'first_name': 'Transport',
            'last_name': 'Student',
            'gender': 'm',
            'partner_id': partner.id,
        })
        stop = self.env['op.transport.route.stop'].create({
            'name': 'Bus Stop 1',
            'route_id': self.route.id,
            'sequence': 1,
        })
        transport = self.env['op.student.transport'].create({
            'student_id': student.id,
            'route_id': self.route.id,
            'stop_id': stop.id,
            'transport_type': 'both',
        })
        self.assertEqual(transport.transport_type, 'both')
        self.assertEqual(transport.route_id, self.route)

    def test_student_transport_types(self):
        """Test each transport type value."""
        partner = self.env['res.partner'].create(
            {'name': 'Transport Student 2'})
        student = self.env['op.student'].create({
            'first_name': 'Transport',
            'last_name': 'Student2',
            'gender': 'f',
            'partner_id': partner.id,
        })
        for transport_type in ['both', 'to_school', 'from_school']:
            transport = self.env['op.student.transport'].create({
                'student_id': student.id,
                'route_id': self.route.id,
                'transport_type': transport_type,
            })
            self.assertEqual(transport.transport_type, transport_type)
            transport.unlink()
