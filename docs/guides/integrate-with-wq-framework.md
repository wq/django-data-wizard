---
order: -1
icon: pin
---

# How To: Integrate with the wq Framework

The Django Data Wizard has built-in support for integration with the [wq framework].  On the server, configuration is mostly the same, except that you do not need to add `"data_wizard.urls"` to your urls.py as the wizard will register itself with [wq.db] instead.

Django Data Wizard provides a complete set of React views via a [wq.app plugin].  This plugin needs to be registered with your application before calling `app.init()` / `wq.init()`.

### wq.app for PyPI

When using Django Data Wizard together with [wq.app]'s [wq.js] build, update app/js/{project_name}.js to import and register wizard.js, which is provided by data_wizard's static/app/js directory for use with `./manage.py collectstatic`.

```bash
pip install wq.app data-wizard
```

```diff
  import wq from './wq.js';
+ import wizard from './wizard.js';
  import config from './data/config.js';

+ wq.use([wizard]);

  async function init() {
      await wq.init(config);
      // ...
```

### @wq/app for npm

When using with [@wq/app] for npm, install and import the [@wq/wizard] npm package.

```bash
npm install @wq/wizard
```

```diff
  import app from '@wq/app';
  import material from '@wq/material';
  import mapgl from '@wq/map-gl';
+ import wizard from '@wq/wizard';
  import config from './data/config';

- app.use([material, mapgl]);
+ app.use([material, mapgl, wizard]);

  async function init() {
      await app.init(config);
      // ...
```

[wq framework]: https://wq.io/
[wq.db]: https://wq.io/wq.db/
[plugins]: https://wq.io/plugins/
[django data wizard]: https://github.com/wq/django-data-wizard
[wq.app]: https://wq.io/wq.app/
[wq.js]: https://wq.io/wq
[@wq/app]: https://wq.io/@wq/app
[@wq/wizard]: ../@wq/wizard.md
