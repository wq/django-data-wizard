from .models import MetaColumn
from wq.db.patterns import admin

admin.site.register(MetaColumn, admin.IdentifiedModelAdmin)
