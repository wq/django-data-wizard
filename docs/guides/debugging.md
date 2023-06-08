# Debugging

### General Tips

 1. Given the wide variety of use cases and failure points, Data Wizard traps most errors by default, to ensure the user can get a short, hopefully informative message rather than a generic 500 error.  The trapped errors are logged via python's `logging` module.

 2. The threading backend (enabled by default) adds another layer of indirection when trying to identify an exception.

 3. Thus, if you are writing a custom Iter or Serializer class, make sure each component works in isolation before trying to debug within the Data Wizard stack.  (See examples below)

 4. Once you have confirmed that itertable and the serializer are working individually, try running `data_wizard` without any web UI traffic via the CLI ([`./manage.py runwizard`](https://github.com/wq/django-data-wizard#command-line-interface)).

 5. Once that is working, try running through the web UI with `./manage.py runserver` and the `immediate` backend:
 
```python3
DATA_WIZARD = {
    "BACKEND": "data_wizard.backends.immediate"
}
```

### Debugging File Loading/Parsing (IterTable)

To debug issues loading and parsing spreadsheet files, try using `itertable` directly:

```python3
from itertable import load_file

for row in load_file('/path/to/file.xlsx'):
    print(row)
```

If `load_file()` throws an error or does not return any rows, there may be a bug in [IterTable](../itertable/index.md) or an issue with your file.  Try to resolve those before returning to the wizard.

If you are writing a custom Iter class, test the class with a similar loop:

```python3
from myapp import CustomIter

for row in CustomIter(filename='/path/to/file.xlsx'):
    print(row)
```

### Debugging the Serializer (DRF)
To investigate validation issues, try instantiating the DRF serializer class directly.

```python3
from data_wizard import registry
Serializer = registry.get_serializer("My Model")
serializer = Serializer(data={"test": "data"})
serializer.is_valid(raise_exception=True)
```

> Note that `data_wizard` traps any and all serializer errors for individual rows, saving only the error text to the `Record` table.  The full stack trace is still sent to the Python `logging` module.
