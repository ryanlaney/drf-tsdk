**This package is now deprecated.**

There are a number of actively maintained and more full-featured packages capable of generating TypeScript clients from an OpenAPI spec, such as [orval](https://github.com/anymaniax/orval) or [openapi-typescript-codegen](https://github.com/ferdikoomen/openapi-typescript-codegen). You can use something like [drf-spectacular](https://github.com/tfranzel/drf-spectacular) to generate Swagger documentation, then one of these packages to build the TypeScript client.

# drf-tsdk

_A package to generate a TypeScript API client for [Django Rest Framework](https://www.django-rest-framework.org/) views and viewsets._

### Usage:

Install the package.
`pip install git+https://github.com/ryanlaney/drf-tsdk.git`

Add the `@ts_api_endpoint()` decorator above any View that should be included as an endpoint your TypeScript API client.

Add the `@ts_api_interface()` decorator above any Serializer that should be included as an Interface.

```python
from rest_framework import serializers
from rest_framework.decorators import api_view

from drf_tsdk import ts_api_endpoint

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

To generate the SDK, call `generate_typescript_bindings`. Put this in a place where it will be evaluated once, such as at the bottom of your project-level _urls.py_.

_urls.py_

```python
from drf_tsdk import generate_typescript_bindings

urlpatterns = [
    ...
]

generate_typescript_bindings('/path/to/apiclient.ts')
```

_/path/to/apiclient.ts_

```typescript
const cache = {};

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
            onError ? (error: any) : void,
            shouldUseCache ? : boolean = false,
            shouldUpdateCache ? : boolean = false
        },
    ): Promise < Response > ? => {
        if (params.shouldUseCache && cache["/api/v1/fields"]) {
            params.onSuccess && params.onSuccess(cache["/api/v1/fields"])
        } else {
            return fetch("/api/v1/myy_endpoint_name", {
                method: "GET",
                ...params.options,
            })
            .then((response) => response.json())
            .then((result: ISomeSerializer[]) => params.onSuccess & params.onSuccess(result))
            .catch((error) => params.onError & params.onError(error));
        }
    }
}

export default API;
```

# TODO

- [ ] Add support for DRF FilterInspectors and Paginators
- [ ] Throw an error if two Interfaces are generated with the same name
- [ ] Throw an error if two endpoints have the same path
- [ ] Refactor... especially *generate_typescript_bindings.py*

# Current Limitations

- Only works if the request body and response types are JSON. I.e. no `formData`, `blob`, etc.
