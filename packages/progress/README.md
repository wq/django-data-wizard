# @wq/progress

**@wq/progress** provides a simple API client for auto-updating [progress] elements. @wq/progress is meant to be used with a JSON web service that provides updates as to the current status of a long-running task, such as the data import tasks in the [Django Data Wizard] package.

> Note: The jQuery and HTML `<progress>` integration has moved to a separate package, [@wq/progress-element]. wq framework / React UI integration is provided by [@wq/wizard].

## Installation

```bash
npm install @wq/progress
```

#### API

@wq/progress should be configured with a url and polling interval, as well as up to three custom callback functions (`onComplete`, `onFail`, and `onProgress`). The callback functions will be passed the most recent JSON data from the web service.

```javascript
// src/index.js
import { Progress } from '@wq/progress';

const progress = new Progress({
    url: 'http://some-web-service/',
    interval: 0.5,
    onProgress(data) {
        console.log(data);
    },
});

progress.start();
```

@wq/progress assumes a specific structure for the data from the web service. The following attributes should be specified on the returned JSON object:

-   `total`: the total number of items being processed
-   `current`: the rank of the currently processing item. (`current / total` will be used to determine the % complete)
-   `status`: A text status indicating task state. A status of `"SUCCESS"` or `"FAILURE"` will cause polling to cease and the `onComplete` or `onFailure` callbacks to be called. The status names were originally based on [Celery's state names][celery-states], though Celery is no longer required for [Django Data Wizard].
-   `error` or `message`: Will be displayed with the `data-wq-status` option.

[django data wizard]: https://github.com/wq/django-data-wizard
[@wq/progress-element]: https://github.com/wq/django-data-wizard/tree/main/packages/progress-element
[@wq/wizard]: https://github.com/wq/django-data-wizard/tree/main/packages/wizard
[celery-states]: http://docs.celeryproject.org/en/latest/userguide/tasks.html#states
