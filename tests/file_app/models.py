from wq.db.contrib.files.models import BaseFile
from dbio.models import IoFile


class File(IoFile, BaseFile):
    pass
