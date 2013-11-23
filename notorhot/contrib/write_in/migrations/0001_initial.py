# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DefaultWriteIn'
        db.create_table(u'write_in_defaultwritein', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('candidate_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, blank=True)),
            ('date_submitted', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_processed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submitter_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('submitter_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal(u'write_in', ['DefaultWriteIn'])


    def backwards(self, orm):
        # Deleting model 'DefaultWriteIn'
        db.delete_table(u'write_in_defaultwritein')


    models = {
        u'write_in.defaultwritein': {
            'Meta': {'object_name': 'DefaultWriteIn'},
            'candidate_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_processed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'blank': 'True'}),
            'submitter_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['write_in']