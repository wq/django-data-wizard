from __future__ import print_function

from rest_framework.test import APITestCase
from rest_framework import status
import os
from time import sleep

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from vera.models import ReportStatus, Parameter
from data_wizard.models import Identifier, Run
from tests.file_app.models import File

import unittest

from django.conf import settings
import swapper
Site = swapper.load_model("vera", "Site")
Event = swapper.load_model("vera", "Event")
Report = swapper.load_model("vera", "Report")
EventResult = swapper.load_model("vera", "EventResult")


class SwapTestCase(APITestCase):
    def setUp(self):
        if not settings.SWAP:
            return

        self.site = Site.objects.find("Site #1")
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.client.force_authenticate(user=self.user)
        self.valid = ReportStatus.objects.create(
            is_valid=True,
            slug='valid',
            pk=100,
        )

        param1 = Parameter.objects.find('Temperature')
        param1.is_numeric = True
        param1.units = 'C'
        param1.save()
        Identifier.objects.create(
            name='Temperature',
            content_object=param1,
        )

        Identifier.objects.create(
            name='Date',
            content_type=ContentType.objects.get_for_model(Event),
            field='date'
        )
        Identifier.objects.create(
            name='Site',
            content_type=ContentType.objects.get_for_model(Site),
            field='id',
        )

    @unittest.skipUnless(settings.SWAP, "requires swapped models")
    def test_manual(self):
        """
        Test the full data_wizard import process, from initial upload thru data
        import - using the non-auto API.
        """
        # 1. Upload file
        filename = os.path.join(os.path.dirname(__file__), 'testdata.csv')
        with open(filename, 'rb') as f:
            response = self.client.post('/files.json', {'file': f})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            fileid = response.data['id']

        run = Run.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(File),
            object_id=fileid,
        )

        def url(action):
            return '/datawizard/%s/%s.json' % (run.pk, action)

        # 2. Start import process
        response = self.client.get(url('start'))
        self.assertIn('result', response.data)
        self.assertIn('columns', response.data['result'])
        self.assertEqual(len(response.data['result']['columns']), 4)

        # 3. Inspect unmatched columns, noting that
        #    - "site id" is an alias for site
        #    - "notes" is a previously unknown parameter
        post = {}
        for col in response.data['result']['columns']:
            if not col.get('unknown', False):
                continue
            self.assertIn('types', col)
            type_choices = {
                tc['name']: tc['choices'] for tc in col['types']
            }
            self.assertIn("Metadata", type_choices)
            self.assertIn("Parameter", type_choices)

            # "Choose" options from dropdown menu choices
            self.assertIn(col['name'], ("notes", "site id"))
            if col['name'] == "notes":
                col_id = "parameters/new"
                type_name = "Parameter"
            elif col['name'] == "site id":
                col_id = "site.id"
                type_name = "Metadata"

            found = False
            for choice in type_choices[type_name]:
                if choice['id'] == col_id:
                    found = True

            self.assertTrue(
                found,
                col_id + " not found in choices: %s" % type_choices[type_name]
            )
            post["rel_%s" % col['rel_id']] = col_id

        # 4. Post selected options, verify that all columns are now known
        response = self.client.post(url('columns'), post)
        unknown = response.data['result']['unknown_count']
        self.assertFalse(unknown, "%s unknown columns remain" % unknown)

        # 5. Check site identifiers
        response = self.client.get(url('ids'))
        res = response.data['result']
        self.assertEqual(res['unknown_count'], 1)
        self.assertEqual(len(res['types']), 1)
        self.assertEqual(len(res['types'][0]['ids']), 1)
        idinfo = res['types'][0]['ids'][0]
        self.assertTrue(idinfo['unknown'])
        self.assertEqual(idinfo['count'], 3)
        self.assertEqual(len(idinfo['choices']), 2)
        for choice in idinfo['choices']:
            if choice['id'] != 'new':
                site_id = choice['id']

        # 6. Post selected options, verify that all identifiers are now known
        post = {
            'ident_%s_id' % idinfo['ident_id']: site_id
        }
        response = self.client.post(url('updateids'), post)
        self.assertFalse(response.data['result']['unknown_count'])

        # 7. Start data import process, wait for completion
        response = self.client.post(url('data'))
        self.assertIn("task_id", response.data)
        task = response.data['task_id']
        done = False
        print()
        while not done:
            sleep(1)
            response = self.client.get(url('status'), {'task': task})
            res = response.data
            if res.get('status', None) in ("PENDING", "PROGRESS"):
                print(res)
                continue
            for key in ('status', 'total', 'current', 'skipped'):
                self.assertIn(key, res)
            if res['status'] == "SUCCESS" or res['total'] == res['current']:
                done = True
                self.assertFalse(res['skipped'])

        # 8. Import complete -verify data exists in database
        for event in Event.objects.all():
            self.assertTrue(event.is_valid)
        self.assertEqual(EventResult.objects.count(), 6)
        param = Parameter.objects.find('temperature')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-07'
        )
        self.assertEqual(er.result_value_numeric, 1.0)

        param = Parameter.objects.find('notes')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-06'
        )
        self.assertEqual(er.result_value_text, "Test Note 2")

        # 9. Check logs
        steps = [log.event for log in run.log.all()]
        self.assertEqual(steps, [
            'created',
            'parse_columns',
            'update_columns',
            'parse_row_identifiers',
            'update_row_identifiers',
            'do_import',
            'import_complete',
        ])
        self.check_data(run)

    @unittest.skipUnless(settings.SWAP, "requires swapped models")
    def test_auto(self):
        """
        Test the full data_wizard import process, from initial upload thru data
        import - using the auto API.
        """
        # 0. Ensure all necessary identifiers are already matched
        Identifier.objects.create(
            name='notes',
            content_object=Parameter.objects.find('notes')
        )
        Identifier.objects.create(
            name='site id',
            content_type=ContentType.objects.get_for_model(Site),
            field='id'
        )
        Identifier.objects.create(
            name='Site 1',
            content_object=self.site,
        )

        # 1. Upload file
        filename = os.path.join(os.path.dirname(__file__), 'testdata.csv')
        with open(filename, 'rb') as f:
            response = self.client.post('/files.json', {'file': f})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            fileid = response.data['id']

        run = Run.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(File),
            object_id=fileid,
        )

        def url(action):
            return '/datawizard/%s/%s.json' % (run.pk, action)

        # 2. Trigger auto-import
        response = self.client.post(url('auto'))
        self.assertIn("task_id", response.data)
        task = response.data['task_id']

        print()
        done = False
        while not done:
            sleep(1)
            response = self.client.get(url('status'), {'task': task})
            res = response.data
            if res.get('status', None) in ("PENDING", "PROGRESS"):
                print(res)
                continue
            for key in ('status', 'total', 'current', 'skipped'):
                self.assertIn(key, res)
            if res['status'] == "SUCCESS" or res['total'] == res['current']:
                done = True
                self.assertFalse(res['skipped'])

        # 3. Import complete -verify data exists in database
        for event in Event.objects.all():
            self.assertTrue(event.is_valid)
        self.assertEqual(EventResult.objects.count(), 6)
        param = Parameter.objects.find('temperature')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-07'
        )
        self.assertEqual(er.result_value_numeric, 1.0)

        param = Parameter.objects.find('notes')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-06'
        )
        self.assertEqual(er.result_value_text, "Test Note 2")

        # 4. Check logs
        steps = [log.event for log in run.log.all()]
        self.assertEqual(steps, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])
        self.check_data(run)

    def check_data(self, run):
        run = Run.objects.get(pk=run.pk)
        self.assertEqual(run.record_count, 3)
        self.assertEqual(run.loader, 'data_wizard.loaders.FileLoader')

        ranges = [
            str(rng).replace("Run for File object contains ", "")
            for rng in run.range_set.all()
        ]
        self.assertEqual(ranges, [
            "Data Column 'Date -> Meta: event.date' at Rows 1-3, Column 0",
            "Data Column 'site id -> Meta: site.id' at Rows 1-3, Column 1",
            "Data Column 'Temperature -> parameter: Temperature (C)'"
            " at Rows 1-3, Column 2",
            "Data Column 'notes -> parameter: notes' at Rows 1-3, Column 3",
            "Cell value 'Site 1 -> site: Site #1' at Rows 1-3, Column 1",
        ])

        records = [
            str(record).replace("Run for File object imported ", "")
            for record in run.record_set.all()
        ]
        self.assertEqual(records, [
            "'Site 1 on 2014-01-05 according to testuser' at row 1",
            "'Site 1 on 2014-01-06 according to testuser' at row 2",
            "'Site 1 on 2014-01-07 according to testuser' at row 3",
        ])
