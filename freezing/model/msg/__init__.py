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
        if 'strict' not in kwargs:
            kwargs['strict'] = True
        super().__init__(*args, **kwargs)

    @property
    @abc.abstractmethod
    def _model_class(self) -> Callable[..., BaseMessage]:
        pass

    @post_load
    def make_model(self, data):
        print("IN POST_LOAD for {}".format(data))
        return self._model_class(**data)

