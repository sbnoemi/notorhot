# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CandidateCategory'
        db.create_table(u'notorhot_candidatecategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from='name', unique_with=(), blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'notorhot', ['CandidateCategory'])

        # Adding model 'Candidate'
        db.create_table(u'notorhot_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from='name', unique_with=(), blank=True)),
            ('pic', self.gf('notorhot.fields.AutoDocumentableImageField')(max_length=100)),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='candidates', to=orm['notorhot.CandidateCategory'])),
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
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitions', to=orm['notorhot.CandidateCategory'])),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comparisons_won', null=True, to=orm['notorhot.Candidate'])),
            ('winning_side', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'notorhot', ['Competition'])


    def backwards(self, orm):
        # Deleting model 'CandidateCategory'
        db.delete_table(u'notorhot_candidatecategory')

        # Deleting model 'Candidate'
        db.delete_table(u'notorhot_candidate')

        # Deleting model 'Competition'
        db.delete_table(u'notorhot_competition')


    models = {
        u'notorhot.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'candidates'", 'to': u"orm['notorhot.CandidateCategory']"}),
            'challenges': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pic': ('notorhot.fields.AutoDocumentableImageField', [], {'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()', 'blank': 'True'}),
            'votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'wins': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'notorhot.candidatecategory': {
            'Meta': {'ordering': "('name',)", 'object_name': 'CandidateCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()', 'blank': 'True'})
        },
        u'notorhot.competition': {
            'Meta': {'object_name': 'Competition'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitions'", 'to': u"orm['notorhot.CandidateCategory']"}),
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