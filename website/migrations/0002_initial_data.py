from django.db import migrations
from wagtail.models import Locale


def initial_data(apps, schema_editor):
    ContentType = apps.get_model('contenttypes.ContentType')
    Page = apps.get_model('wagtailcore.Page')
    Site = apps.get_model('wagtailcore.Site')
    WebPage = apps.get_model('website.WebPage')

    # Create page content type
    webpage_content_type, created = ContentType.objects.get_or_create(
        model='webpage',
        app_label='website',
    )

    # Delete the default home page generated by wagtail,
    # and replace it with a more useful page type.
    curr_homepage = Page.objects.filter(slug='home').delete()

    homepage = WebPage.objects.create(
        title = "Home",
        slug='home',
        custom_template='coderedcms/pages/home_page.html',
        content_type=webpage_content_type,
        path='00010001',
        depth=2,
        numchild=0,
        url_path='/home/',
        locale_id=Locale.get_default().id,
    )

    # Create a new default site
    Site.objects.create(
        hostname='www.wisdar-emp.com',
        site_name='wisdar news',
        root_page_id=homepage.id,
        is_default_site=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('coderedcms', '0001_initial'),
        ('wagtailcore', '0057_page_locale_fields_notnull'),
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_data),
    ]
