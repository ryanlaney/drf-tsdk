# drf-typescript-api-client

_A package to generate a TypeScript API client for [Django Rest Framework](https://www.django-rest-framework.org/) views and viewsets._

### Usage:

Install the package.
`pip install git+https://github.com/ryanlaney/drf-typescript-api-client.git`

Add the `@ts_api_client()` decorator above any view that should be included in your TypeScript API client.

```python
from rest_framework import serializers
from rest_framework.decorators import api_view

from drf_typescript_api_client import ts_api_client

class SomeSerializer(serializers.Serializer):
    foo = serializers.CharField()
    bar = serializers.IntegerField(allow_null=True)
    baz = serializers.DateTimeField(required=False)

@api_view(['GET'])
@ts_api_client(path=["endpointName"], url="/api/v1/my_endpoint_name", query_serializer=None, request_serializer=None, response_serializer=SomeSerializer(many=True))
def my_view(request):
    pass
```

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
const API {
    endpointName: (
        params: {
            options ? : any,
            onSuccess ? ({
                foo: string,
                bar: number | null,
                baz ? : string
            }) : void,
            onError ? (error: any) : void
        },
    ):
        Promise < Response > => {
            return fetch("/api/v1/myy_endpoint_name", {
                method: "GET",
                ...params.options,
            })
            .then((response) => response.json())
            .then((result: {
                foo: string,
                bar: number | null,
                baz ? : string
            }) => params.onSuccess & params.onSuccess(result))
            .catch((error) => params.onError & params.onError(error));
    }
}

export default API;
```
