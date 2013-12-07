# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MetaColumn'
        db.create_table('wq_metacolumn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('vera', ['MetaColumn'])

        # Adding model 'UnknownItem'
        db.create_table('wq_unknownitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('vera', ['UnknownItem'])

        # Adding model 'SkippedRecord'
        db.create_table('wq_skippedrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reason', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('vera', ['SkippedRecord'])

        # Adding model 'Range'
        db.create_table('wq_range', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('relationship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['relate.Relationship'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('start_row', self.gf('django.db.models.fields.IntegerField')()),
            ('end_row', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_column', self.gf('django.db.models.fields.IntegerField')()),
            ('end_column', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('vera', ['Range'])

    def backwards(self, orm):
        # Deleting model 'MetaColumn'
        db.delete_table('wq_metacolumn')

        # Deleting model 'UnknownItem'
        db.delete_table('wq_unknownitem')

        # Deleting model 'SkippedRecord'
        db.delete_table('wq_skippedrecord')

        # Deleting model 'Range'
        db.delete_table('wq_range')

    models = {
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
        u'vera.metacolumn': {
            'Meta': {'object_name': 'MetaColumn', 'db_table': "'wq_metacolumn'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'vera.range': {
            'Meta': {'object_name': 'Range', 'db_table': "'wq_range'"},
            'end_column': ('django.db.models.fields.IntegerField', [], {}),
            'end_row': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['relate.Relationship']"}),
            'start_column': ('django.db.models.fields.IntegerField', [], {}),
            'start_row': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'vera.skippedrecord': {
            'Meta': {'object_name': 'SkippedRecord', 'db_table': "'wq_skippedrecord'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {})
        },
        u'vera.unknownitem': {
            'Meta': {'object_name': 'UnknownItem', 'db_table': "'wq_unknownitem'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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

    complete_apps = []
