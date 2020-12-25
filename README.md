# drf-typescript-api-client

_A package to generate a TypeScript API client for [Django Rest Framework](https://www.django-rest-framework.org/) views and viewsets._

### Usage:

Install the package.
`pip install git+https://github.com/ryanlaney/drf-typescript-api-client.git`

Add the `@ts_api_endpoint()` decorator above any View that should be included as an endpoint your TypeScript API client.

Add the `@ts_api_interface()` decorator above any Serializer that should be included as an Interface.

```python
from rest_framework import serializers
from rest_framework.decorators import api_view

from drf_typescript_api_client import ts_api_endpoint

@ts_api_interface(name="ISomeSerializer")
class SomeSerializer(serializers.Serializer):
    foo = serializers.CharField()
    bar = serializers.IntegerField(allow_null=True)
    baz = serializers.DateTimeField(required=False)

@api_view(['GET'])
@ts_api_endpoint(path=["endpointName"], url="/api/v1/my_endpoint_name", query_serializer=None, body_serializer=None, response_serializer=SomeSerializer(many=True))
def my_view(request):
    pass
```

Note that using the `@ts_api_interface` decorator isn't necessary; this package supports inline object literals, but for complex APIs, you'll probably end up with a cleaner output (as well as useful, reusable Interfaces) if you use the decorator.

To generate the API client, call `generate_api_client`. Put this in a place where it will be evaluated once, such as at the bottom of your project-level _urls.py_.

_urls.py_

```python
from drf_typescript_api_client import generate_api_client

urlpatterns = [
    ...
]

generate_api_client('/path/to/apiclient.ts')
```

_/path/to/apiclient.ts_

```typescript
export interface ISomeSerializer {
    foo: string,
    bar: number | null,
    baz ? : string
}

const API {
    endpointName: (
        params: {
            options ? : any,
            onSuccess ? (result: ISomeSerializer[]) : void,
            onError ? (error: any) : void
        },
    ): Promise < Response > => {
            return fetch("/api/v1/myy_endpoint_name", {
                method: "GET",
                ...params.options,
            })
            .then((response) => response.json())
            .then((result: ISomeSerializer[]) => params.onSuccess & params.onSuccess(result))
            .catch((error) => params.onError & params.onError(error));
    }
}

export default API;
```

# TODO

- [ ] Add support for FilterInspectors and Paginators
- [ ] Throw an error if two Interfaces are generated with the same name
- [ ] Throw an error if two endpoints have the same path
- [ ] Automatically resolve endpoint URL if possible (i.e. using Django `reverse`)
- [ ] Automatically resolve endpoint type (_GET_, _POST_, etc) if possible (i.e. also using Django `reverse` and inspecting the view decorators)
- [ ] Add support for `serializer_class` in ViewSets, overridable by `response_serializer`. Investigate how this is handled by DRF e.g. when generating Swagger docs and mimic this behavior.

# Current Limitations

- Only works if the request body and response types are JSON. I.e. no `formData`, `blob`, etc.
