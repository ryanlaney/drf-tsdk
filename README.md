# django-typomatic

_A package to generate a TypeScript API client for [Django Rest Framework](https://www.django-rest-framework.org/) views and viewsets._

### Usage:

Install the package.
`pip install git+https://github.com/ryanlaney/drf-typescript-api-client.git`

Add the `@ts_api_client()` decorator above any view that should be included in your TypeScript API client.

To generate the API client, call `generate_ts_api_client`. Put this in a place where it will be evaluated once, such as at the bottom of your project-level _urls.py_.

_urls.py_

```python
from drf_typescript_api_client import generate_ts

urlpatterns = (
    ...
)

generate_ts_api_client('/path/to/apiclient.ts')
```

_/path/to/apiclient.ts_

```typescript
export default class API {
    foo = {
        list: () => {
            fetch(...)
        },
        create: () => {
            fetch(...)
        },
        get: () => {
            fetch(...)
        },
        update: () => {
            fetch(...)
        },
        delete: () => {
            fetch(...)
        }
    }

    bar = {
        list: () => {
            fetch(...)
        },
        create: () => {
            fetch(...)
        },
        get: () => {
            fetch(...)
        },
        update: () => {
            fetch(...)
        },
        delete: () => {
            fetch(...)
        }
    }
}
```
