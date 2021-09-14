# @wq/wizard

**@wq/wizard** is a [@wq/app plugin][plugins] providing a complete React UI for the [Django Data Wizard] package.

## Installation

### wq.app for PyPI

When using Django Data Wizard together with [wq.app]'s [wq.js] build, update app/js/{project_name}.js to import and register wizard.js, which is provided by data_wizard's static/app/js directory.

```bash
pip install wq.app data-wizard
```

```javascript
import wq from './wq.js';
import config from './data/config.js';
import wizard from './wizard.js';

wq.use([wizard]);

wq.init(config).then(...);
```

### @wq/app for npm

When using @wq/app for npm, install and import the @wq/wizard npm package.

```bash
npm install @wq/wizard
```

```javascript
import app from '@wq/app';
import material from '@wq/material';
import mapgl from '@wq/map-gl';
import wizard from '@wq/wizard';
import config from './config';

app.use([material, mapgl, wizard]);

app.init(config).then(...);
```

[plugins]: https://wq.io/plugins/
[django data wizard]: https://github.com/wq/django-data-wizard
[wq.app]: https://wq.io/wq.app/
[wq.js]: https://wq.io/wq
[@wq/app]: https://wq.io/@wq/app
