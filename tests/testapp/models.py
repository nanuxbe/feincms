from __future__ import absolute_import, unicode_literals

from django import forms
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from feincms.models import Base, create_base_model
from feincms.module.blog.models import Entry, EntryAdmin
from feincms.module.page.models import Page
from feincms.content.raw.models import RawContent
from feincms.content.image.models import ImageContent
from feincms.content.medialibrary.models import MediaFileContent
from feincms.content.application.models import ApplicationContent
from feincms.content.contactform.models import ContactFormContent, ContactForm
from feincms.content.file.models import FileContent
from feincms.module.page.extensions.navigation import (
    NavigationExtension, PagePretender)
from feincms.module.page import processors
from feincms.content.application.models import reverse

from mptt.models import MPTTModel

from .content import CustomContentType

Page.register_templates({
    'key': 'base',
    'title': 'Base Template',
    'path': 'base.html',
    'regions': (
        ('main', 'Main region'),
        ('sidebar', 'Sidebar', 'inherited'),
    ),
})
Page.create_content_type(RawContent)
Page.create_content_type(
    MediaFileContent,
    TYPE_CHOICES=(
        ('default', 'Default position'),
    )
)
Page.create_content_type(
    ImageContent,
    POSITION_CHOICES=(
        ('default', 'Default position'),
    )
)
Page.create_content_type(ContactFormContent, form=ContactForm)
Page.create_content_type(FileContent)
Page.register_request_processor(processors.etag_request_processor)
Page.register_response_processor(processors.etag_response_processor)
Page.register_response_processor(
    processors.debug_sql_queries_response_processor())


def get_admin_fields(form, *args, **kwargs):
    return {
        'exclusive_subpages': forms.BooleanField(
            label=capfirst(_('exclusive subpages')),
            required=False,
            initial=form.instance.parameters.get('exclusive_subpages', False),
            help_text=_(
                'Exclude everything other than the application\'s content'
                ' when rendering subpages.'),
        ),
        'custom_field': forms.CharField(),
    }

Page.create_content_type(
    ApplicationContent,
    APPLICATIONS=(
        ('testapp.blog_urls', 'Blog', {'admin_fields': get_admin_fields}),
        ('whatever', 'Test Urls', {'urls': 'testapp.applicationcontent_urls'}),
    )
)

Entry.register_extensions(
    'feincms.module.extensions.seo',
    'feincms.module.extensions.translations',
    'feincms.module.extensions.seo',
    'feincms.module.extensions.ct_tracker',
)
Entry.register_regions(
    ('main', 'Main region'),
)
Entry.create_content_type(RawContent)
Entry.create_content_type(
    ImageContent, POSITION_CHOICES=(
        ('default', 'Default position'),
    )
)


class BlogEntriesNavigationExtension(NavigationExtension):
    """
    Extended navigation for blog entries.

    It would be added to 'Blog' page properties in admin.
    """
    name = _('all blog entries')

    def children(self, page, **kwargs):
        for entry in Entry.objects.all():
            yield PagePretender(
                title=entry.title,
                url=reverse(
                    'testapp.blog_urls/blog_entry_detail',
                    kwargs={'object_id': entry.id}
                ),
            )

Page.register_extensions(
    'feincms.module.page.extensions.navigation',
    'feincms.module.page.extensions.sites',
    'feincms.module.extensions.translations',
    'feincms.module.extensions.datepublisher',
    'feincms.module.extensions.translations',
    'feincms.module.extensions.ct_tracker',
    'feincms.module.extensions.seo',
    'feincms.module.extensions.changedate',
    'feincms.module.extensions.seo',  # duplicate
    'feincms.module.page.extensions.navigation',
    'feincms.module.page.extensions.symlinks',
    'feincms.module.page.extensions.titles',
    'feincms.module.page.extensions.navigationgroups',
)


@python_2_unicode_compatible
class Category(MPTTModel):
    name = models.CharField(max_length=20)
    slug = models.SlugField()
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children')

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


# add m2m field to entry so it shows up in entry admin
Entry.add_to_class(
    str('categories'),
    models.ManyToManyField(Category, blank=True, null=True))
EntryAdmin.list_filter += ('categories',)


class ExampleCMSBase(Base):
    pass

ExampleCMSBase.register_regions(
    ('region', 'region title'),
    ('region2', 'region2 title'))


class ExampleCMSBase2(Base):
        pass

ExampleCMSBase2.register_regions(
    ('region', 'region title'),
    ('region2', 'region2 title'))


class MyModel(create_base_model()):
    pass


MyModel.register_regions(('main', 'Main region'))


unchanged = CustomContentType
MyModel.create_content_type(CustomContentType)
assert CustomContentType is unchanged
