"""
Create or customize your page models here.
"""

from coderedcms.blocks import HTML_STREAMBLOCKS
from coderedcms.blocks import LAYOUT_STREAMBLOCKS
from coderedcms.blocks import BaseBlock
from coderedcms.blocks import BaseLinkBlock
from coderedcms.blocks import LinkStructValue
from coderedcms.forms import CoderedFormField
from coderedcms.models import CoderedArticleIndexPage
from coderedcms.models import CoderedArticlePage
from coderedcms.models import CoderedEmail
from coderedcms.models import CoderedEventIndexPage
from coderedcms.models import CoderedEventOccurrence
from coderedcms.models import CoderedEventPage
from coderedcms.models import CoderedFormPage
from coderedcms.models import CoderedLocationIndexPage
from coderedcms.models import CoderedLocationPage
from coderedcms.models import CoderedWebPage
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet


class ArticlePage(CoderedArticlePage):
    """
    Article, suitable for news or blog content.
    """

    class Meta:
        verbose_name = "Article"
        ordering = ["-first_published_at"]

    # Only allow this page to be created beneath an ArticleIndexPage.
    parent_page_types = ["website.ArticleIndexPage"]

    template = "coderedcms/pages/article_page.html"
    search_template = "coderedcms/pages/article_page.search.html"


class ArticleIndexPage(CoderedArticleIndexPage):
    """
    Shows a list of article sub-pages.
    """

    class Meta:
        verbose_name = "Article Landing Page"

    # Override to specify custom index ordering choice/default.
    index_query_pagemodel = "website.ArticlePage"

    # Only allow ArticlePages beneath this page.
    subpage_types = ["website.ArticlePage"]

    template = "coderedcms/pages/article_index_page.html"


class EventPage(CoderedEventPage):
    class Meta:
        verbose_name = "Event Page"

    parent_page_types = ["website.EventIndexPage"]
    template = "coderedcms/pages/event_page.html"


class EventIndexPage(CoderedEventIndexPage):
    """
    Shows a list of event sub-pages.
    """

    class Meta:
        verbose_name = "Events Landing Page"

    index_query_pagemodel = "website.EventPage"

    # Only allow EventPages beneath this page.
    subpage_types = ["website.EventPage"]

    template = "coderedcms/pages/event_index_page.html"


class EventOccurrence(CoderedEventOccurrence):
    event = ParentalKey(EventPage, related_name="occurrences")


class FormPage(CoderedFormPage):
    """
    A page with an html <form>.
    """

    class Meta:
        verbose_name = "Form"

    template = "coderedcms/pages/form_page.html"


class FormPageField(CoderedFormField):
    """
    A field that links to a FormPage.
    """

    class Meta:
        ordering = ["sort_order"]

    page = ParentalKey("FormPage", related_name="form_fields")


class FormConfirmEmail(CoderedEmail):
    """
    Sends a confirmation email after submitting a FormPage.
    """

    page = ParentalKey("FormPage", related_name="confirmation_emails")


class LocationPage(CoderedLocationPage):
    """
    A page that holds a location.  This could be a store, a restaurant, etc.
    """

    class Meta:
        verbose_name = "Location Page"

    template = "coderedcms/pages/location_page.html"

    # Only allow LocationIndexPages above this page.
    parent_page_types = ["website.LocationIndexPage"]


class LocationIndexPage(CoderedLocationIndexPage):
    """
    A page that holds a list of locations and displays them with a Google Map.
    This does require a Google Maps API Key in Settings > CRX Settings
    """

    class Meta:
        verbose_name = "Location Landing Page"

    # Override to specify custom index ordering choice/default.
    index_query_pagemodel = "website.LocationPage"

    # Only allow LocationPages beneath this page.
    subpage_types = ["website.LocationPage"]

    template = "coderedcms/pages/location_index_page.html"


class WebPage(CoderedWebPage):
    """
    General use page with featureful streamfield and SEO attributes.
    """

    class Meta:
        verbose_name = "Web Page"

    template = "coderedcms/pages/web_page.html"


# -- Navbar & Footer ----------------------------------------------------------


class NavbarLinkBlock(BaseLinkBlock):
    """
    Simple link in the navbar.
    """

    class Meta:
        icon = "link"
        label = "Link"
        template = "website/blocks/navbar_link.html"
        value_class = LinkStructValue


class NavbarDropdownBlock(BaseBlock):
    """
    Custom dropdown menu with heading, links, and rich content.
    """

    class Meta:
        icon = "arrow-down"
        label = "Dropdown"
        template = "website/blocks/navbar_dropdown.html"

    title = blocks.CharBlock(
        max_length=255,
        required=True,
        label="Title",
    )
    links = blocks.StreamBlock(
        [("link", NavbarLinkBlock())],
        required=True,
        label="Links",
    )
    description = blocks.StreamBlock(
        HTML_STREAMBLOCKS,
        required=False,
        label="Description",
    )


@register_snippet
class Navbar(models.Model):
    """
    Custom navigation bar / menu.
    """

    class Meta:
        verbose_name = "Navigation Bar"

    name = models.CharField(
        max_length=255,
    )
    content = StreamField(
        [
            ("link", NavbarLinkBlock()),
            ("dropdown", NavbarDropdownBlock()),
        ],
        use_json_field=True,
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("content"),
    ]

    def __str__(self) -> str:
        return self.name


@register_snippet
class Footer(models.Model):
    """
    Custom footer for bottom of pages on the site.
    """

    class Meta:
        verbose_name = "Footer"

    name = models.CharField(
        max_length=255,
    )
    content = StreamField(
        LAYOUT_STREAMBLOCKS,
        verbose_name="Content",
        blank=True,
        use_json_field=True,
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("content"),
    ]

    def __str__(self) -> str:
        return self.name


import uuid
from coderedcms.models.page_models import CoderedWebPage
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail.models import TranslatableMixin



class ProposalPage(CoderedWebPage):
    """A model for managing proposals with specific metadata and content."""

    caption = RichTextField(
        blank=True,
        verbose_name="Caption",
        help_text="A rich-text field for the proposal's caption."
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Author"),
        help_text="The owner of the proposal."
    )

    display_author_as = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Display Author As",
        help_text="Overrides how the author’s name displays on this proposal."
    )

    source = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Source",
        help_text="The source of the proposal, indicating its origin."
    )

    publication_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Publication Date",
        help_text="Date when the proposal is published or made available."
    )


    content_panels = CoderedWebPage.content_panels + [
        FieldPanel('caption'),
        MultiFieldPanel(
            [
                FieldPanel('author'),
                FieldPanel('display_author_as'),
                FieldPanel('source'),
                FieldPanel('publication_date'),
            ],
            heading="Proposal Metadata",
        ),
    ]

    class Meta:
        verbose_name = "Proposal Page"
        ordering = ['-publication_date']  # Order by most recent first

    parent_page_types = ["website.ProposalIndexPage"]


class ProposalIndexPage(CoderedWebPage):
    """
    Index page for listing all proposals. Automatically retrieves and displays
    child ProposalPage instances.
    """

    show_only_published = models.BooleanField(
        default=True,
        verbose_name=_("Show Only Published"),
        help_text=_("Show only proposals with a publication date in the past."),
    )

    content_panels = CoderedWebPage.content_panels + [
        FieldPanel('show_only_published'),
    ]

    def get_child_pages(self):
        """
        Retrieves child ProposalPage instances, optionally filtering by
        publication status.
        """
        queryset = ProposalPage.objects.child_of(self).live()
        if self.show_only_published:
            queryset = queryset.filter(publication_date__lte=models.F('go_live_at') or models.functions.Now())
        return queryset


    class Meta:
        verbose_name = "Proposal Index Page"
        ordering = ['-go_live_at']

    index_query_pagemodel = "website.ProposalPage"

    # Only allow ArticlePages beneath this page.
    subpage_types = ["website.ProposalPage"]


