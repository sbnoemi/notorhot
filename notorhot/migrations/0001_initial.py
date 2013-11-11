# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Candidate'
        db.create_table(u'notorhot_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('pic', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('challenges', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('wins', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'notorhot', ['Candidate'])

        # Adding model 'Competition'
        db.create_table(u'notorhot_competition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_presented', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_voted', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('left', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comparisons_left', to=orm['notorhot.Candidate'])),
            ('right', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comparisons_right', to=orm['notorhot.Candidate'])),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comparisons_won', null=True, to=orm['notorhot.Candidate'])),
            ('winning_side', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'notorhot', ['Competition'])


    def backwards(self, orm):
        # Deleting model 'Candidate'
        db.delete_table(u'notorhot_candidate')

        # Deleting model 'Competition'
        db.delete_table(u'notorhot_competition')


    models = {
        u'notorhot.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'challenges': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pic': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'wins': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'notorhot.competition': {
            'Meta': {'object_name': 'Competition'},
            'date_presented': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_voted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comparisons_left'", 'to': u"orm['notorhot.Candidate']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comparisons_right'", 'to': u"orm['notorhot.Candidate']"}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comparisons_won'", 'null': 'True', 'to': u"orm['notorhot.Candidate']"}),
            'winning_side': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['notorhot']