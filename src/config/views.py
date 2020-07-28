# Third-Party Libraries
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    "Homepage"
    template_name = "home.html"
