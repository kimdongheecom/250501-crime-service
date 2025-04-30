from dataclasses import dataclass

@dataclass
class DataSchema:
    context: str = ''
    fname: str = ''
    train: object = None
    test: object = None
    id: str = ''
    label: str = ''

    @property
    def context(self) -> str:
        return self._context

    @context.setter
    def context(self, context: str):
        self._context = context

    @property
    def fname(self) -> str:
        return self._fname

    @fname.setter
    def fname(self, fname: str):
        self._fname = fname

    @property
    def train(self) -> object:
        return self._train

    @train.setter
    def train(self, train: object):
        self._train = train

    @property
    def test(self) -> object:
        return self._test

    @test.setter
    def test(self, test: object):
        self._test = test

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id: str):
        self._id = id

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label
