import unittest
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
import datetime
from wq.db.contrib.vera.models import (
    Event, Report, ReportStatus, Site, Parameter, EventResult
)
from django.conf import settings


def value_by_type(attachments):
    return {
        a['type_id']: a['value'] for a in attachments
    }


class VeraTestCase(APITestCase):
    def setUp(self):
        if settings.SWAP:
            return
        self.site = Site.objects.find(45, -95)
        self.user = User.objects.create(username='testuser')
        self.valid = ReportStatus.objects.create(is_valid=True, slug='valid')
        self.invalid = ReportStatus.objects.create(slug='invalid')

        # Numeric parameters
        param1 = Parameter.objects.find('Temperature')
        param1.is_numeric = True
        param1.units = 'C'
        param1.save()

        param2 = Parameter.objects.find('Wind Speed')
        param2.is_numeric = True
        param2.units = 'm/s'
        param2.save()

        # Text parameters
        Parameter.objects.find('Notes')
        Parameter.objects.find('Rain')

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_simple(self):
        # Single report
        event_key = [45, -95, '2014-01-01']
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 5,
                'Notes': 'Test Observation'
            },
            user=self.user,
            status=self.valid,
        )
        # Test that event exists and has correct values
        instance = Event.objects.get_by_natural_key(*event_key)
        self.assertEqual(instance.date, datetime.date(2014, 1, 1))
        self.assertEqual(instance.site.pk, self.site.pk)
        self.assertEqual(instance.vals['temperature'], 5)
        self.assertEqual(instance.vals['notes'], 'Test Observation')

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_report_merge(self):
        event_key = [45, -95, '2014-01-02']

        # Three reports for the same event

        # Initial valid report
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 5,
                'Notes': 'Test Observation'
            },
            user=self.user,
            status=self.valid,
        )

        # Subsequent valid report, should override above
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 5.3,
                'Wind Speed': 10,
            },
            user=self.user,
            status=self.valid,
        )

        # Subsequent invalid report, should not override above (or appear
        #  in event at all)
        Report.objects.create_report(
            event_key,
            {
                'Wind Speed': 15,
                'Rain': 'N'
            },
            user=self.user,
            status=self.invalid,
        )

        # Test that each parameter has the latest valid value
        instance = Event.objects.get_by_natural_key(*event_key)
        self.assertEqual(instance.vals['temperature'], 5.3)
        self.assertEqual(instance.vals['notes'], 'Test Observation')
        self.assertEqual(instance.vals['wind-speed'], 10)
        self.assertNotIn('rain', instance.vals)

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_invalid_param(self):
        event_key = [45, -95, '2014-01-01']
        values = {
            'Invalid Parameter': 5,
            'Notes': 'Test Observation'
        }
        with self.assertRaises(TypeError):
            Report.objects.create_report(
                event_key,
                values,
                user=self.user
            )

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_merge_eventresult(self):
        event_key = [45, -95, '2014-01-10']

        # Two reports for the same event, EventResult should contain
        # two rows for the event (which should correspond to event.results)
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 6,
                'Notes': 'Test Observation 3'
            },
            user=self.user,
            status=self.valid,
        )

        # Subsequent valid report, should override above
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 5.3,
            },
            user=self.user,
            status=self.valid
        )
        event = Event.objects.get_by_natural_key(*event_key)
        ers = EventResult.objects.filter(event=event)
        self.assertEqual(ers.count(), 2)
        self.assertEqual(
            ers.get(result_type__name='Temperature').result_value_numeric,
            5.3
        )
        self.assertEqual(
            ers.get(result_type__name='Notes').result_value_text,
            'Test Observation 3'
        )

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_reset_eventresult(self):
        event_key = [45, -95, '2014-01-11']

        # Two reports for the same event, EventResult should contain
        # two rows for the event (which should correspond to event.results)
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 10,
                'Notes': 'Test Observation 4'
            },
            user=self.user,
            status=self.valid,
        )

        # Subsequent valid report, should override above
        Report.objects.create_report(
            event_key,
            {
                'Temperature': 11.3,
                'Notes': None,
            },
            user=self.user,
            status=self.valid
        )
        event = Event.objects.get_by_natural_key(*event_key)

        # Wipe out autogenerated eventresults and create them again
        EventResult.objects.all().delete()
        EventResult.objects.set_for_events(date='2014-01-11')

        ers = EventResult.objects.filter(event=event)
        self.assertEqual(ers.count(), 2)
        self.assertEqual(
            ers.get(result_type__name='Temperature').result_value_numeric,
            11.3
        )
        self.assertEqual(
            ers.get(result_type__name='Notes').result_value_text,
            'Test Observation 4'
        )


class VeraRestTestCase(APITestCase):
    def setUp(self):
        if settings.SWAP:
            return
        self.site = Site.objects.find(45, -95)
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.client.force_authenticate(user=self.user)
        self.valid = ReportStatus.objects.create(is_valid=True, slug='valid')

        param1 = Parameter.objects.find('Temperature')
        param1.is_numeric = True
        param1.units = 'C'
        param1.save()

        Parameter.objects.find('Notes')

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_post(self):
        form = {
            'site__latitude': 45,
            'site__longitude': -95.5,
            'date': '2014-01-03',
            'result-temperature-value': 6,
            'result-notes-value': 'Test Observation',
        }
        response = self.client.post('/reports.json', form)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['event_label'],
            "45.0, -95.5 on 2014-01-03"
        )
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)
        values = value_by_type(response.data['results'])
        self.assertEqual(values['temperature'], 6.0)
        self.assertEqual(values['notes'], 'Test Observation')

    @unittest.skipIf(settings.SWAP, "requires non-swapped models")
    def test_vera_post_merge(self):
        # Submit first report (but don't validate it)
        # Event should exist but have no result values
        form1 = {
            'site__latitude': 45,
            'site__longitude': -95.5,
            'date': '2014-01-04',
            'result-temperature-value': 6,
            'result-notes-value': 'Test Observation 2',
        }
        response1 = self.client.post('/reports.json', form1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        event_id = response1.data['event_id']
        event = self.client.get('/events/%s.json' % event_id).data
        self.assertEqual(len(event['results']), 0)

        # Submit second report and validate it
        # Event should contain a single result value
        form2 = {
            'site__latitude': 45,
            'site__longitude': -95.5,
            'date': '2014-01-04',
            'result-temperature-value': 7,
            'status': 'valid'
        }
        response2 = self.client.post('/reports.json', form2)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['event_id'], event_id)
        event = self.client.get('/events/%s.json' % event_id).data
        self.assertEqual(len(event['results']), 1)

        # Validate original report
        # Event should now have the temperature value from the second report
        # and the notes from the first.
        self.client.patch(
            '/reports/%s.json' % response1.data['id'],
            {'status': 'valid'}
        )
        event = self.client.get('/events/%s.json' % event_id).data
        self.assertEqual(len(event['results']), 2)
        values = value_by_type(event['results'])
        self.assertEqual(values['temperature'], 7)
        self.assertEqual(values['notes'], 'Test Observation 2')
