# @wq/progress-element

**@wq/progress-element** provides a simple way to create fetch()-powered auto-updating HTML5 [progress] elements. @wq/progress-element is meant to be used with a JSON web service that provides updates as to the current status of a long-running task. @wq/progress-element is primarily intended for (and bundled with) the [Django Data Wizard] package.

## Installation

```bash
npm install @wq/progress-element
```

> Note: @wq/progress-element is designed for Django Data Wizard's Admin-style UI, and is enabled automatically by default. If you are using a wq framework / React UI, use [@wq/wizard] rather than @wq/progress-element.

#### API

@wq/progress-element scans the page for `<progress>` elements during initialization, and can be configured via `data-wq-*` attributes.

-   `data-wq-url` configures the URL to use for the AJAX request to update the progress status.
-   `data-wq-interval` defines the polling frequency in seconds (default 0.5).
-   `data-wq-status` can be used to specify an element which will be used to display `error` or `message` attributes from the JSON response.

```xml
<progress data-wq-url="/getstatus.json"
          data-wq-interval=0.25
          data-wq-status="status-info"></progress>
<div id="status-info"></div>
```

For older browsers, the `<progress>` bar will automatically fall back to text showing the current status.

@wq/progress-element automatically configures a [@wq/progress] client to start polling the web service. See [@wq/progress] for more details on the expected data structure.

[progress]: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress
[django data wizard]: https://github.com/wq/django-data-wizard
[@wq/wizard]: https://github.com/wq/django-data-wizard/tree/main/packages/wizard
[@wq/progress]: https://github.com/wq/django-data-progress/tree/main/packages/progress
