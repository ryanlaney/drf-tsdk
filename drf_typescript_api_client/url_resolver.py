import json

from django.urls import URLPattern, URLResolver

from .exceptions import DRFTypeScriptAPIClientException

class URLPattern_:
    def __init__(self, pattern, base_url=""):
        self.url_pattern = pattern
        self.base_url = base_url

def resolve_urls(urlpatterns):
    def list_urls(urlpatterns_, all_patterns=[], base_url=""):
        for urlpattern in urlpatterns_:
            if isinstance(urlpattern, URLPattern):
                all_patterns += [URLPattern_(urlpattern, base_url)]
            elif isinstance(urlpattern, URLResolver):
                all_patterns += list_urls(urlpattern.url_patterns, all_patterns, base_url=urlpattern.pattern)
            else:
                raise DRFTypeScriptAPIClientException(f"Unrecognized pattern {str(urlpattern)}")
        return all_patterns

    return list_urls(urlpatterns)
    # for p in patterns:
    #     print({
    #         'pattern': {
    #             'route': p.pattern._route,
    #             'regex_dict': p.pattern._regex_dict,
    #             'is_endpoint': p.pattern._is_endpoint,
    #             'name': p.pattern.name,
    #             'converters': p.pattern.converters
    #         },
    #         'callback': p.callback,
    #         'default_args': p.default_args,
    #         'name': p.name
    #     })
