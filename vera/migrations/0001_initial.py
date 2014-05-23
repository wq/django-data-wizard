# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
import swapper


class Migration(SchemaMigration):

    def forwards(self, orm):
        if not swapper.is_swapped('vera', 'Site'):
            # Adding model 'Site'
            db.create_table('wq_site', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
                ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ))
            db.send_create_signal(u'vera', ['Site'])

            # Adding unique constraint on 'Site', fields ['latitude', 'longitude']
            db.create_unique('wq_site', ['latitude', 'longitude'])

        if not swapper.is_swapped('vera', 'Event'):
            Site = swapper.load_model('vera', 'Site', orm)

            # Adding model 'Event'
            db.create_table('wq_event', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=Site)),
                ('date', self.gf('django.db.models.fields.DateField')()),
            ))
            db.send_create_signal(u'vera', ['Event'])

            # Adding unique constraint on 'Event', fields ['site', 'date']
            db.create_unique('wq_event', ['site_id', 'date'])

        if not swapper.is_swapped('vera', 'Report'):
            Event = swapper.load_model('vera', 'Event', orm)
            User = swapper.load_model('auth', 'User', orm)
            ReportStatus = swapper.load_model('vera', 'ReportStatus', orm)

            # Adding model 'Report'
            db.create_table('wq_report', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=Event)),
                ('entered', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
                ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'vera_report', null=True, to=User)),
                ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=ReportStatus, null=True, blank=True)),
            ))
            db.send_create_signal(u'vera', ['Report'])

        if not swapper.is_swapped('vera', 'ReportStatus'):
            # Adding model 'ReportStatus'
            db.create_table('wq_reportstatus', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
                ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ))
            db.send_create_signal(u'vera', ['ReportStatus'])

            # Adding unique constraint on 'ReportStatus', fields ['slug']
            db.create_unique('wq_reportstatus', ['slug'])

        if not swapper.is_swapped('vera', 'Parameter'):
            # Adding model 'Parameter'
            db.create_table('wq_parameter', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
                ('is_numeric', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('units', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ))
            db.send_create_signal(u'vera', ['Parameter'])

        if not swapper.is_swapped('vera', 'Result'):
            Parameter = swapper.load_model('vera', 'Parameter', orm)
            Report = swapper.load_model('vera', 'Report', orm)
            # Adding model 'Result'
            db.create_table('wq_result', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=Parameter)),
                ('report', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=Report)),
                ('value_numeric', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
                ('value_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
                ('empty', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ))
            db.send_create_signal(u'vera', ['Result'])

            # Adding index on 'Result', fields ['type', 'report_id', 'empty']
            db.create_index('wq_result', ['type_id', 'report_id', 'empty'])

        if not swapper.is_swapped('vera', 'EventResult'):
            Event = swapper.load_model('vera', 'Event', orm)
            Result = swapper.load_model('vera', 'Result', orm)
            Site = swapper.load_model('vera', 'Site', orm)
            Parameter = swapper.load_model('vera', 'Parameter', orm)
            Report = swapper.load_model('vera', 'Report', orm)

            # Adding model 'EventResult'
            db.create_table('wq_eventresult', (
                ('id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
                ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=Event)),
                ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=Result)),
                ('event_site', self.gf('django.db.models.fields.related.ForeignKey')(to=Site, null=True, blank=True)),
                ('event_date', self.gf('django.db.models.fields.DateField')()),
                ('result_type', self.gf('django.db.models.fields.related.ForeignKey')(to=Parameter)),
                ('result_report', self.gf('django.db.models.fields.related.ForeignKey')(to=Report)),
                ('result_value_numeric', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
                ('result_value_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
                ('result_empty', self.gf('django.db.models.fields.BooleanField')()),
            ))
            db.send_create_signal('vera', ['EventResult'])

            # Adding unique constraint on 'EventResult', fields ['event', 'result_type']
            db.create_unique('wq_eventresult', ['event_id', 'result_type_id'])


    def backwards(self, orm):
        if not swapper.is_swapped('vera', 'EventResult'):
            # Removing unique constraint on 'EventResult', fields ['event', 'result_type']
            db.delete_unique('wq_eventresult', ['event_id', 'result_type_id'])

        if not swapper.is_swapped('vera', 'Result'):
            # Removing index on 'Result', fields ['type', 'report', 'empty']
            db.delete_index('wq_result', ['type_id', 'report_id', 'empty'])

        if not swapper.is_swapped('vera', 'ReportStatus'):
            # Removing unique constraint on 'ReportStatus', fields ['slug']
            db.delete_unique('wq_reportstatus', ['slug'])

        if not swapper.is_swapped('vera', 'Event'):
            # Removing unique constraint on 'Event', fields ['site', 'date']
            db.delete_unique('wq_event', ['site_id', 'date'])

        if not swapper.is_swapped('vera', 'Site'):
            # Removing unique constraint on 'Site', fields ['latitude', 'longitude']
            db.delete_unique('wq_site', ['latitude', 'longitude'])

        if not swapper.is_swapped('vera', 'Site'):
            # Deleting model 'Site'
            db.delete_table('wq_site')

        if not swapper.is_swapped('vera', 'Event'):
            # Deleting model 'Event'
            db.delete_table('wq_event')

        if not swapper.is_swapped('vera', 'Report'):
            # Deleting model 'Report'
            db.delete_table('wq_report')

        if not swapper.is_swapped('vera', 'ReportStatus'):
            # Deleting model 'ReportStatus'
            db.delete_table('wq_reportstatus')

        if not swapper.is_swapped('vera', 'Parameter'):
            # Deleting model 'Parameter'
            db.delete_table('wq_parameter')

        if not swapper.is_swapped('vera', 'Result'):
            # Deleting model 'Result'
            db.delete_table('wq_result')

        if not swapper.is_swapped('vera', 'EventResult'):
            # Deleting model 'EventResult'
            db.delete_table('wq_eventresult')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'identify.authority': {
            'Meta': {'object_name': 'Authority', 'db_table': "'wq_identifiertype'"},
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'identify.identifier': {
            'Meta': {'object_name': 'Identifier', 'db_table': "'wq_identifier'"},
            'authority': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['identify.Authority']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'vera.event': {
            'Meta': {'ordering': "('-date',)", 'unique_together': "(('site', 'date'),)", 'object_name': 'Event', 'db_table': "'wq_event'"},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Site']", 'null': 'True', 'blank': 'True'})
        },
        'vera.eventresult': {
            'Meta': {'unique_together': "(('event', 'result_type'),)", 'object_name': 'EventResult', 'db_table': "'wq_eventresult'"},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Event']"}),
            'event_date': ('django.db.models.fields.DateField', [], {}),
            'event_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Site']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Result']"}),
            'result_empty': ('django.db.models.fields.BooleanField', [], {}),
            'result_report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Report']"}),
            'result_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Parameter']"}),
            'result_value_numeric': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'result_value_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'vera.parameter': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Parameter', 'db_table': "'wq_parameter'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_numeric': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'vera.report': {
            'Meta': {'ordering': "('-entered',)", 'object_name': 'Report', 'db_table': "'wq_report'"},
            'entered': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.ReportStatus']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'vera_report'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'vera.reportstatus': {
            'Meta': {'unique_together': "[['slug']]", 'object_name': 'ReportStatus', 'db_table': "'wq_reportstatus'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'vera.result': {
            'Meta': {'ordering': "('type',)", 'object_name': 'Result', 'db_table': "'wq_result'", 'index_together': "[('type', 'report', 'empty')]"},
            'empty': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': u"orm['vera.Report']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vera.Parameter']"}),
            'value_numeric': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'vera.site': {
            'Meta': {'unique_together': "(('latitude', 'longitude'),)", 'object_name': 'Site', 'db_table': "'wq_site'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'relate.relationship': {
            'Meta': {'object_name': 'Relationship', 'db_table': "'wq_relationship'"},
            'computed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'from_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['contenttypes.ContentType']"}),
            'from_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['contenttypes.ContentType']"}),
            'to_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['relate.RelationshipType']"})
        },
        u'relate.relationshiptype': {
            'Meta': {'object_name': 'RelationshipType', 'db_table': "'wq_relationshiptype'"},
            'computed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'from_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inverse_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['contenttypes.ContentType']"})
        }
    }

    complete_apps = ['vera']
