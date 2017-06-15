from __future__ import print_function

from rest_framework.test import APITransactionTestCase
from rest_framework import status
import os
from time import sleep

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.files import File
from data_wizard.models import Run, Identifier
from django.conf import settings


class WizardTestCase(APITransactionTestCase):
    serializer_name = None
    with_wqdb = True

    file_url = None
    file_model = None
    file_content_type = None

    def _fixture_teardown(self):
        # _fixture_teardown truncates related tables including contenttypes
        # (even though that table is populated before the test runs)
        content_types = list(ContentType.objects.all())
        super(WizardTestCase, self)._fixture_teardown()
        ContentType.objects.bulk_create(content_types)

    def setUp(self):
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.client.force_authenticate(user=self.user)

    def mkurl(self, run, action):
        if self.with_wqdb:
            template = "/datawizard/%s/%s.json"
        else:
            template = "/datawizard/%s/%s/?format=json"
        return template % (run.pk, action)

    def get_url(self, run, action, params={}):
        return self.client.get(self.mkurl(run, action), params)

    def post_url(self, run, action, post):
        return self.client.post(self.mkurl(run, action), post)

    def wait(self, run, action):
        print()
        response = self.post_url(run, action, None)
        self.assertIn("task_id", response.data)
        status_params = {'task': response.data['task_id']}
        done = False
        while not done:
            sleep(1)
            response = self.get_url(run, 'status', status_params)
            res = response.data
            if res.get('status', None) in ("PENDING", "PROGRESS"):
                print(res)
            else:
                done = True
        return res

    def create_identifier(self, name, field, value=None, attr_id=None):
        """
        0. Preregister any necessary identifiers
        """
        Identifier.objects.create(
            serializer=self.serializer_name,
            name=name,
            field=field,
            value=value,
            attr_id=attr_id,
            resolved=True,
        )

    def upload_file(self, filename, skip_serializer=False):
        """
        1. Upload spreadsheet file
        """
        filename = os.path.join(settings.MEDIA_ROOT, filename)
        with open(filename) as f:
            if self.with_wqdb:
                response = self.client.post(self.file_url, {'file': f})
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                file_id = response.data['id']
            else:
                file_id = self.file_model.objects.create(file=File(f)).pk

        post = {
            'content_type_id': self.file_content_type,
            'object_id': file_id,
        }
        if not skip_serializer:
            post['serializer'] = self.serializer_name

        response = self.client.post('/datawizard/?format=json', post)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, response.data
        )
        run = Run.objects.get(pk=response.data['id'])
        return run

    def set_serializer(self, run):
        """
        1b. Set serializer class
        """
        response = self.get_url(run, 'serializers')
        found = False
        for choice in response.data.get('serializer_choices'):
            if choice['name'] == self.serializer_name:
                found = True
        self.assertTrue(found)
        response = self.post_url(run, 'updateserializer', {
            'serializer': self.serializer_name,
        })
        self.assertEqual(response.data.get('serializer'), self.serializer_name)

    def check_columns(self, run, expect_columns, expect_unknown):
        """
        2. Start import process by verifying columns
        """
        response = self.get_url(run, 'columns')
        self.assertIn('result', response.data)
        self.assertIn('columns', response.data['result'])
        self.assertEqual(
            len(response.data['result']['columns']), expect_columns
        )
        self.assertEqual(
            response.data['result'].get('unknown_count', 0), expect_unknown
        )

    def update_columns(self, run, mappings):
        """
        3. Inspect unmatched columns and select choices
        """
        response = self.get_url(run, 'columns')
        post = {}
        for col in response.data['result']['columns']:
            if not col.get('unknown', False):
                continue
            self.assertIn('types', col)
            type_choices = {
                tc['name']: tc['choices'] for tc in col['types']
            }
            for type_name, mapping in mappings.items():
                self.assertIn(type_name, type_choices)

                # "Choose" options from dropdown menu choices
                col_id = mapping.get(col['name'])
                if col_id is None:
                    continue
                found = False
                for choice in type_choices[type_name]:
                    if choice['id'] == col_id:
                        found = True

                self.assertTrue(
                    found,
                    col_id + " not found in choices: %s" %
                    type_choices[type_name]
                )
                post["rel_%s" % col['rel_id']] = col_id

        response = self.post_url(run, 'updatecolumns', post)
        unknown = response.data['result']['unknown_count']
        self.assertFalse(unknown, "%s unknown columns remain" % unknown)

    def check_row_identifiers(self, run, expect_identifiers, expect_unknown):
        """
        4. Verify identifier (foreign key) values
        """
        response = self.get_url(run, 'ids')
        self.assertIn('result', response.data)
        self.assertIn('types', response.data['result'])
        all_ids = sum([
            len(group['ids'])
            for group in response.data['result']['types']
        ])
        self.assertEqual(expect_identifiers, all_ids)
        self.assertEqual(
            expect_unknown, response.data['result'].get('unknown_count', 0)
        )

    def update_row_identifiers(self, run, mappings):
        """
        5. Inspect unmatched identifiers and select choices
        """
        response = self.get_url(run, 'ids')
        type_ids = {
            t['type_id']: t['ids']
            for t in response.data['result']['types']
        }

        post = {}
        for typeid, mapping in mappings.items():
            self.assertIn(typeid, type_ids)
            for idinfo in type_ids[typeid]:
                if idinfo['value'] in mapping:
                    post[
                        'ident_%s_id' % idinfo['ident_id']
                    ] = mapping[idinfo['value']]

        # 7. Post selected options, verify that all identifiers are now known
        response = self.post_url(run, 'updateids', post)
        unknown = response.data['result']['unknown_count']
        self.assertFalse(unknown, "%s unknown identifiers remain" % unknown)

    def start_import(self, run, expect_skipped):
        """
        6. Start data import process, wait for completion
        """
        res = self.wait(run, 'data')
        for key in ('status', 'total', 'current', 'skipped'):
            self.assertIn(key, res)
        self.assertEqual('SUCCESS', res['status'])
        self.assertEqual(expect_skipped, res['skipped'])

    def auto_import(self, run, expect_input_required=False):
        """
        Test the auto import (steps 2-6)
        """
        res = self.wait(run, 'auto')
        self.assertEqual(res['status'], "SUCCESS")

        if expect_input_required:
            self.assertIn('message', res)
            return res

        self.assertNotIn('message', res, res.get('message'))
        for key in ('status', 'total', 'current', 'skipped'):
            self.assertIn(key, res)
        return res

    def assert_status(self, run, expect_count):
        """
        7. Verify record count, loader and serializer
        """
        run = Run.objects.get(pk=run.pk)
        self.assertEqual(expect_count, run.record_count)
        self.assertEqual('data_wizard.loaders.FileLoader', run.loader)
        self.assertEqual(self.serializer_name, run.serializer)

    def assert_ranges(self, run, expect_ranges):
        """
        8. Verify column and identifier ranges
        """
        ranges = [
            str(rng).replace("%s contains " % run, "")
            for rng in run.range_set.all()
        ]
        self.assertEqual(expect_ranges, ranges)

    def assert_records(self, run, expect_records):
        """
        9. Verify column and identifier ranges
        """
        records = [
            str(record).replace("%s " % run, "").replace('[u"', '["')
            for record in run.record_set.all()
        ]
        self.assertEqual(expect_records, records)

    def assert_log(self, run, expect_log):
        """
        10. Verify expected process was followed
        """
        steps = [log.event for log in run.log.all()]
        self.assertEqual(expect_log, steps)

    def assert_urls(self, run, urltemplate):
        if not self.with_wqdb:
            return
        records = self.get_url(run, 'records').data['records']
        for row, record in zip(records, run.record_set.all()):
            if record.success:
                self.assertEqual(
                    urltemplate % record.object_id,
                    row.get('object_url'),
                )
