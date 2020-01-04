import abc
import enum
from datetime import datetime
from typing import Callable, Dict, Any

from marshmallow import fields, Schema, post_load
from marshmallow_enum import EnumField


class BaseMessage:

    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            if not hasattr(self.__class__, k):
                raise AttributeError("No class attribute {!r}".format(k))
            setattr(self, k, v)


class BaseSchema(Schema):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    @abc.abstractmethod
    def _model_class(self, **kwargs) -> Callable[..., BaseMessage]:
        pass

    @post_load
    def make_model(self, data, **kwargs):
        return self._model_class(**data)

