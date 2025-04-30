from dataclasses import dataclass


@dataclass
class MatZipdata:
    MatZip: object
    context: str
    fname: int
    id: str
    name: str

    @property
    def MatZip(self) -> object:
        return self._MatZip

    @MatZip.setter
    def MatZip(self, MatZip):
        self._MatZip = MatZip

    @property
    def context(self) -> str:
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    @property
    def fname(self) -> str:
        return self._fname

    @fname.setter
    def fname(self, fname):
        self._fname = fname

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name