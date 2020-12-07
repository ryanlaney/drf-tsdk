from django.urls import reverse


class URLFinder:
    def __init__(self, view, urlpatterns_module):
        self.view = view
        self.urlpatterns = urlpatterns_module.urlpatterns

    def find_url(self):
        try:
            return reverse(self.view, urlconf=self.urlpatterns)
        except:
            return "/api/v1/test"
