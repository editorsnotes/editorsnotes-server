# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20151019_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='document',
            name='creator',
            field=models.ForeignKey(related_name='created_document_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='document',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='The last time this item was edited.'),
        ),
        migrations.AlterField(
            model_name='document',
            name='last_updater',
            field=models.ForeignKey(related_name='last_to_update_document_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The last user to update this item.'),
        ),
        migrations.AlterField(
            model_name='featureditem',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='featureditem',
            name='creator',
            field=models.ForeignKey(related_name='created_featureditem_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='note',
            name='assigned_users',
            field=models.ManyToManyField(help_text='Users who have been assigned to this note.', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='note',
            name='creator',
            field=models.ForeignKey(related_name='created_note_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='note',
            name='is_private',
            field=models.BooleanField(default=False, help_text=b"If true, will only be be viewable to users who belong to the note's project."),
        ),
        migrations.AlterField(
            model_name='note',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='The last time this item was edited.'),
        ),
        migrations.AlterField(
            model_name='note',
            name='last_updater',
            field=models.ForeignKey(related_name='last_to_update_note_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The last user to update this item.'),
        ),
        migrations.AlterField(
            model_name='note',
            name='license',
            field=models.ForeignKey(blank=True, to='licensing.License', help_text='The license under which this note is available.', null=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='markup',
            field=models.TextField(help_text='Text for this item that uses CommonMark syntax, with Working Notes-specific additions for notes, topics, and documents.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(help_text='The markup text for this item rendered into HTML.', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='project',
            field=models.ForeignKey(related_name='notes', to='main.Project', help_text='The project to which this note belongs.'),
        ),
        migrations.AlterField(
            model_name='note',
            name='status',
            field=models.CharField(default='1', help_text='The status of the note. "Open" for outstanding, "Closed" for finished, or "Hibernating" for somewhere in between.', max_length=1, choices=[('0', 'closed'), ('1', 'open'), ('2', 'hibernating')]),
        ),
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(help_text='The title of the note.', max_length='80'),
        ),
        migrations.AlterField(
            model_name='project',
            name='image',
            field=models.ImageField(upload_to='project_images', null=True, verbose_name='An image representing this project.', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='markup',
            field=models.TextField(help_text='Text for this item that uses CommonMark syntax, with Working Notes-specific additions for notes, topics, and documents.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(help_text='The markup text for this item rendered into HTML.', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(help_text='The name of the project.', max_length='80'),
        ),
        migrations.AlterField(
            model_name='projectinvitation',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='projectinvitation',
            name='creator',
            field=models.ForeignKey(related_name='created_projectinvitation_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='scan',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='scan',
            name='creator',
            field=models.ForeignKey(related_name='created_scan_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='creator',
            field=models.ForeignKey(related_name='created_topic_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='The last time this item was edited.'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='last_updater',
            field=models.ForeignKey(related_name='last_to_update_topic_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The last user to update this item.'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='markup',
            field=models.TextField(help_text='Text for this item that uses CommonMark syntax, with Working Notes-specific additions for notes, topics, and documents.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(help_text='The markup text for this item rendered into HTML.', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='topicassignment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='topicassignment',
            name='creator',
            field=models.ForeignKey(related_name='created_topicassignment_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='The time this item was created.'),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='creator',
            field=models.ForeignKey(related_name='created_transcript_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The user who created this item.'),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='The last time this item was edited.'),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='last_updater',
            field=models.ForeignKey(related_name='last_to_update_transcript_set', editable=False, to=settings.AUTH_USER_MODEL, help_text='The last user to update this item.'),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='markup',
            field=models.TextField(help_text='Text for this item that uses CommonMark syntax, with Working Notes-specific additions for notes, topics, and documents.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(help_text='The markup text for this item rendered into HTML.', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.CharField(help_text='Profile text for a user.', max_length=1000, null=True, blank=True),
        ),
    ]
