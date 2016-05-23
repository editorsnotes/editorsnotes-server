# -*- coding: utf-8 -*-


from django.db import models, migrations
import editorsnotes.djotero.fields
import editorsnotes.auth.models
import editorsnotes.main.models.base
from django.conf import settings
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reversion', '0001_initial'),
        ('auth', '0001_initial'),
        ('licensing', '__first__'),
        ('djotero', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternateName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=200)),
                ('creator', models.ForeignKey(related_name='created_alternatename_set', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('ordering', models.IntegerField(null=True, blank=True)),
                ('notes', editorsnotes.main.fields.XHTMLField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('creator', models.ForeignKey(related_name='created_citation_set', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['ordering'],
            },
            bases=(models.Model, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('zotero_data', editorsnotes.djotero.fields.ZoteroField(null=True, blank=True)),
                ('import_id', models.CharField(null=True, editable=False, max_length=64, blank=True, unique=True, db_index=True)),
                ('description', editorsnotes.main.fields.XHTMLField()),
                ('description_digest', models.CharField(max_length=32, editable=False)),
                ('ordering', models.CharField(max_length=32, editable=False)),
                ('language', models.CharField(default='English', max_length=32)),
                ('edtf_date', models.TextField(null=True, blank=True)),
                ('collection', models.ForeignKey(related_name='parts', blank=True, to='main.Document', null=True)),
                ('creator', models.ForeignKey(related_name='created_document_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('last_updater', models.ForeignKey(related_name='last_to_update_document_set', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['ordering', 'import_id'],
            },
            bases=(editorsnotes.main.models.base.Administered, editorsnotes.main.models.base.URLAccessible, editorsnotes.auth.models.ProjectPermissionsMixin, editorsnotes.auth.models.UpdatersMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DocumentLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField()),
                ('description', models.TextField(blank=True)),
                ('creator', models.ForeignKey(related_name='created_documentlink_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(related_name='links', to='main.Document')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('key', models.CharField(max_length=32)),
                ('value', models.TextField()),
                ('creator', models.ForeignKey(related_name='created_documentmetadata_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(related_name='metadata', to='main.Document')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeaturedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('creator', models.ForeignKey(related_name='created_featureditem_set', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='Footnote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('content', editorsnotes.main.fields.XHTMLField()),
                ('creator', models.ForeignKey(related_name='created_footnote_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('last_updater', models.ForeignKey(related_name='last_to_update_footnote_set', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.main.models.base.Administered, editorsnotes.main.models.base.URLAccessible, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='LegacyTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('preferred_name', models.CharField(unique=True, max_length='80')),
                ('slug', models.CharField(unique=True, max_length='80', editable=False, db_index=True)),
            ],
            options={
                'ordering': ['slug'],
            },
            bases=(models.Model, editorsnotes.main.models.base.URLAccessible),
        ),
        migrations.CreateModel(
            name='LogActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('display_title', models.CharField(max_length=300)),
                ('action', models.IntegerField()),
                ('message', models.TextField(null=True, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-time',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(unique=True, max_length='80')),
                ('content', editorsnotes.main.fields.XHTMLField()),
                ('status', models.CharField(default='1', max_length=1, choices=[('0', 'closed'), ('1', 'open'), ('2', 'hibernating')])),
                ('is_private', models.BooleanField(default=False)),
                ('sections_counter', models.PositiveIntegerField(default=0)),
                ('assigned_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
                ('creator', models.ForeignKey(related_name='created_note_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('last_updater', models.ForeignKey(related_name='last_to_update_note_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('license', models.ForeignKey(blank=True, to='licensing.License', null=True)),
            ],
            options={
                'ordering': ['-last_updated'],
                'permissions': (('view_private_note', 'Can view notes private to a project.'),),
            },
            bases=(models.Model, editorsnotes.main.models.base.Administered, editorsnotes.main.models.base.URLAccessible, editorsnotes.auth.models.ProjectPermissionsMixin, editorsnotes.auth.models.UpdatersMixin),
        ),
        migrations.CreateModel(
            name='NoteSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('_section_type', models.CharField(max_length=100)),
                ('note_section_id', models.PositiveIntegerField(null=True, blank=True)),
                ('ordering', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['ordering', '-note_section_id'],
            },
            bases=(models.Model, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='NoteReferenceNS',
            fields=[
                ('notesection_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='main.NoteSection')),
                ('content', editorsnotes.main.fields.XHTMLField(null=True, blank=True)),
                ('note_reference', models.ForeignKey(to='main.Note')),
            ],
            options={
            },
            bases=('main.notesection',),
        ),
        migrations.CreateModel(
            name='CitationNS',
            fields=[
                ('notesection_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='main.NoteSection')),
                ('content', editorsnotes.main.fields.XHTMLField(null=True, blank=True)),
            ],
            options={
            },
            bases=('main.notesection',),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length='80')),
                ('slug', models.SlugField(help_text='Used for project-specific URLs and groups', unique=True)),
                ('image', models.ImageField(null=True, upload_to='project_images', blank=True)),
                ('description', editorsnotes.main.fields.XHTMLField(null=True, blank=True)),
                ('default_license', models.ForeignKey(default=1, to='licensing.License')),
            ],
            options={
                'permissions': (('view_project_roster', 'Can view project roster.'), ('change_project_roster', 'Can edit project roster.')),
            },
            bases=(models.Model, editorsnotes.main.models.base.URLAccessible, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='ProjectInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('email', models.EmailField(max_length=75)),
                ('creator', models.ForeignKey(related_name='created_projectinvitation_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(to='main.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_super_role', models.BooleanField(default=False)),
                ('role', models.CharField(max_length=40)),
                ('group', models.OneToOneField(to='auth.Group')),
                ('project', models.ForeignKey(related_name='roles', to='main.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RevisionLogActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_activity', models.OneToOneField(related_name='revision_metadata', to='main.LogActivity')),
                ('revision', models.ForeignKey(related_name='logactivity_metadata', to='reversion.Revision')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RevisionProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='main.Project')),
                ('revision', models.OneToOneField(related_name='project_metadata', to='reversion.Revision')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(upload_to='scans/%Y/%m')),
                ('image_thumbnail', models.ImageField(null=True, upload_to='scans/%Y/%m', blank=True)),
                ('ordering', models.IntegerField(null=True, blank=True)),
                ('creator', models.ForeignKey(related_name='created_scan_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(related_name='scans', to='main.Document')),
            ],
            options={
                'ordering': ['ordering', '-created'],
            },
            bases=(models.Model, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='TextNS',
            fields=[
                ('notesection_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='main.NoteSection')),
                ('content', editorsnotes.main.fields.XHTMLField()),
            ],
            options={
            },
            bases=('main.notesection',),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('preferred_name', models.CharField(max_length=200)),
                ('summary', editorsnotes.main.fields.XHTMLField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('creator', models.ForeignKey(related_name='created_topic_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('last_updater', models.ForeignKey(related_name='last_to_update_topic_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('merged_into', models.ForeignKey(blank=True, editable=False, to='main.Topic', null=True)),
                ('project', models.ForeignKey(related_name='topics', to='main.Project')),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.main.models.base.URLAccessible, editorsnotes.auth.models.ProjectPermissionsMixin, editorsnotes.main.models.base.Administered),
        ),
        migrations.CreateModel(
            name='TopicAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('creator', models.ForeignKey(related_name='created_topicassignment_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(related_name='assignments', blank=True, to='main.Topic', null=True)),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='TopicNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('_preferred_name', models.CharField(max_length='200')),
                ('type', models.CharField(blank=True, max_length=3, null=True, choices=[('EVT', 'Event'), ('ORG', 'Organization'), ('PER', 'Person'), ('PUB', 'Publication')])),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('creator', models.ForeignKey(related_name='created_topicnode_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('last_updater', models.ForeignKey(related_name='last_to_update_topicnode_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('merged_into', models.ForeignKey(blank=True, editable=False, to='main.TopicNode', null=True)),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.main.models.base.URLAccessible),
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('content', editorsnotes.main.fields.XHTMLField()),
                ('creator', models.ForeignKey(related_name='created_transcript_set', editable=False, to=settings.AUTH_USER_MODEL)),
                ('document', models.OneToOneField(related_name='_transcript', to='main.Document')),
                ('last_updater', models.ForeignKey(related_name='last_to_update_transcript_set', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, editorsnotes.main.models.base.Administered, editorsnotes.main.models.base.URLAccessible, editorsnotes.auth.models.ProjectPermissionsMixin),
        ),
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('purpose', models.IntegerField(choices=[(1, 'Feedback'), (2, 'Bug report'), (9, 'Other')])),
                ('message', models.TextField()),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='topicassignment',
            unique_together=set([('content_type', 'object_id', 'topic')]),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_node',
            field=models.ForeignKey(related_name='project_topics', to='main.TopicNode'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together=set([('project', 'preferred_name'), ('project', 'topic_node')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectrole',
            unique_together=set([('project', 'role')]),
        ),
        migrations.AddField(
            model_name='projectinvitation',
            name='project_role',
            field=models.ForeignKey(to='main.ProjectRole'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notesection',
            name='creator',
            field=models.ForeignKey(related_name='created_notesection_set', editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notesection',
            name='last_updater',
            field=models.ForeignKey(related_name='last_to_update_notesection_set', editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notesection',
            name='note',
            field=models.ForeignKey(related_name='sections', to='main.Note'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='notesection',
            unique_together=set([('note', 'note_section_id')]),
        ),
        migrations.AddField(
            model_name='note',
            name='project',
            field=models.ForeignKey(related_name='notes', to='main.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logactivity',
            name='project',
            field=models.ForeignKey(to='main.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logactivity',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='legacytopic',
            name='merged_into',
            field=models.ForeignKey(blank=True, editable=False, to='main.TopicNode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='footnote',
            name='transcript',
            field=models.ForeignKey(related_name='footnotes', to='main.Transcript'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='featureditem',
            name='project',
            field=models.ForeignKey(to='main.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='documentmetadata',
            unique_together=set([('document', 'key')]),
        ),
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(related_name='documents', to='main.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='zotero_link',
            field=models.OneToOneField(related_name='zotero_item', null=True, blank=True, to='djotero.ZoteroLink'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('project', 'description_digest')]),
        ),
        migrations.AddField(
            model_name='citationns',
            name='document',
            field=models.ForeignKey(to='main.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='citation',
            name='document',
            field=models.ForeignKey(related_name='citations', to='main.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='citation',
            name='last_updater',
            field=models.ForeignKey(related_name='last_to_update_citation_set', editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alternatename',
            name='topic',
            field=models.ForeignKey(related_name='alternate_names', to='main.Topic'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='alternatename',
            unique_together=set([('topic', 'name')]),
        ),
    ]
