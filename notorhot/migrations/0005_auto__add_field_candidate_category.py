# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Candidate.category'
        db.add_column(u'notorhot_candidate', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['notorhot.CandidateCategory'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Candidate.category'
        db.delete_column(u'notorhot_candidate', 'category_id')


    models = {
        u'notorhot.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['notorhot.CandidateCategory']", 'null': 'True', 'blank': 'True'}),
            'challenges': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pic': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()', 'blank': 'True'}),
            'votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'wins': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'notorhot.candidatecategory': {
            'Meta': {'object_name': 'CandidateCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()', 'blank': 'True'})
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