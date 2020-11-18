"""Home Views."""
# Third-Party Libraries
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Main HomePage View."""

    template_name = "home.html"
