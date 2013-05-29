# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from wq.db.patterns.base import swapper

class Migration(SchemaMigration):

    def forwards(self, orm):
        if not swapper.is_swapped('qual', 'Site'):
            # Adding model 'Site'
            db.create_table('wq_site', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
                ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ))
            db.send_create_signal(u'qual', ['Site'])

            # Adding unique constraint on 'Site', fields ['latitude', 'longitude']
            db.create_unique('wq_site', ['latitude', 'longitude'])

        if not swapper.is_swapped('qual', 'Event'):
            Site = swapper.load_model('qual', 'Site', orm)
            
            # Adding model 'Event'
            db.create_table('wq_event', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('date', self.gf('django.db.models.fields.DateField')()),
                ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=Site)),
            ))
            db.send_create_signal(u'qual', ['Event'])

            # Adding unique constraint on 'Event', fields ['site', 'date']
            db.create_unique('wq_event', ['site_id', 'date'])

        if not swapper.is_swapped('qual', 'Report'):
            Event        = swapper.load_model('qual', 'Event', orm)
            User         = swapper.load_model('auth', 'User', orm)
            ReportStatus = swapper.load_model('qual', 'ReportStatus', orm)

            # Adding model 'Report'
            db.create_table('wq_report', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=Event)),
                ('entered', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
                ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=User)),
                ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=ReportStatus, null=True, blank=True)),
            ))
            db.send_create_signal(u'qual', ['Report'])

        if not swapper.is_swapped('qual', 'ReportStatus'):
            # Adding model 'ReportStatus'
            db.create_table('wq_reportstatus', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
                ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ))
            db.send_create_signal(u'qual', ['ReportStatus'])

        if swapper.is_swapped('annotate', 'AnnotationType') == 'qual.Parameter':
            # Adding model 'Parameter'
            db.create_table('wq_parameter', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
                ('contenttype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
                ('is_numeric', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('units', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ))
            db.send_create_signal(u'qual', ['Parameter'])

        if swapper.is_swapped('annotate', 'Annotation') == 'qual.Result':
            AnnotationType = swapper.load_model('annotate', 'AnnotationType')
            # Adding model 'Result'
            db.create_table('wq_result', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=AnnotationType)),
                ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
                ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
                ('value_numeric', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
                ('value_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ))
            db.send_create_signal(u'qual', ['Result'])

    def backwards(self, orm):

        if not swapper.is_swapped('qual', 'Site'):
            # Removing unique constraint on 'Site', fields ['latitude', 'longitude']
            db.delete_unique('wq_site', ['latitude', 'longitude'])

            # Deleting model 'Site'
            db.delete_table('wq_site')

        if not swapper.is_swapped('qual', 'Event'):
            # Removing unique constraint on 'Event', fields ['site', 'date']
            db.delete_unique('wq_event', ['site_id', 'date'])

            # Deleting model 'Event'
            db.delete_table('wq_event')

        if not swapper.is_swapped('qual', 'Report'):
            # Deleting model 'Report'
            db.delete_table('wq_report')

        if not swapper.is_swapped('qual', 'ReportStatus'):
            # Deleting model 'ReportStatus'
            db.delete_table('wq_reportstatus')

        if swapper.is_swapped('qual', 'AnnotationType') == 'qual.Parameter':
            # Deleting model 'Parameter'
            db.delete_table('wq_parameter')

        if swapper.is_swapped('qual', 'Annotation') == 'qual.Result':
            # Deleting model 'Result'
            db.delete_table('wq_result')


    models = {
        u'annotate.annotation': {
            'Meta': {'object_name': 'Annotation', 'db_table': "'wq_annotation'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['annotate.AnnotationType']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'annotate.annotationtype': {
            'Meta': {'object_name': 'AnnotationType', 'db_table': "'wq_annotationtype'"},
            'contenttype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'valid_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'valid_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'qual.event': {
            'Meta': {'object_name': 'Event', 'db_table': "'wq_event'"},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qual.Site']"})
        },
        u'qual.parameter': {
            'Meta': {'object_name': 'Parameter', 'db_table': "'wq_parameter'"},
            'contenttype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_numeric': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'qual.report': {
            'Meta': {'object_name': 'Report', 'db_table': "'wq_report'"},
            'entered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': u"orm['qual.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qual.ReportStatus']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'qual.reportstatus': {
            'Meta': {'object_name': 'ReportStatus', 'db_table': "'wq_reportstatus'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'qual.result': {
            'Meta': {'object_name': 'Result', 'db_table': "'wq_result'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qual.Parameter']"}),
            'value_numeric': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'qual.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'wq_site'"},
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

    complete_apps = ['qual']
