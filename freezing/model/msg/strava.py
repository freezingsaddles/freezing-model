import abc
import enum
from datetime import datetime
from typing import Any, Callable, Dict

import arrow
from marshmallow import Schema, fields, post_load, pre_load
from marshmallow_enum import EnumField

from . import BaseMessage, BaseSchema


class ObjectType(enum.Enum):
    activity = "activity"


class AspectType(enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"


class Subscription(BaseMessage):
    """
    Represents a Webhook Event Subscription.

    http://strava.github.io/api/partner/v3/events/
    """

    application_id: int = None
    object_type: ObjectType = None
    aspect_type: AspectType = None
    callback_url: str = None
    created_at: datetime = None
    updated_at: datetime = None


class SubscriptionSchema(BaseSchema):
    """
    Represents a Webhook Event Subscription.

    http://strava.github.io/api/partner/v3/events/
    """

    _model_class = Subscription

    application_id = fields.Int()
    object_type = EnumField(ObjectType)
    aspect_type = EnumField(AspectType)
    callback_url = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class SubscriptionCallback(BaseMessage):
    """
    Represents a Webhook Event Subscription Callback.
    """

    hub_mode: str = None
    hub_verify_token: str = None
    hub_challenge: str = None


class SubscriptionCallbackSchema(BaseSchema):
    """
    Represents a Webhook Event Subscription Callback.
    """

    _model_class = SubscriptionCallback

    hub_mode = fields.Str(data_key="hub.mode")
    hub_verify_token = fields.Str(data_key="hub.verify_token")
    hub_challenge = fields.Str(data_key="hub.challenge")


class SubscriptionUpdate(BaseMessage):
    """
    Represents a Webhook Event Subscription Update.
    """

    subscription_id: int = None
    owner_id: int = None
    object_id: int = None
    object_type: ObjectType = None
    aspect_type: str = None
    event_time: datetime = None
    updates: Dict[str, Any] = None


class SubscriptionUpdateSchema(BaseSchema):
    """
    Represents a Webhook Event Subscription Update.
    """

    _model_class = SubscriptionUpdate

    subscription_id = fields.Int()
    owner_id = fields.Int()
    object_id = fields.Int()
    object_type = EnumField(ObjectType)
    aspect_type = EnumField(AspectType)
    event_time = fields.DateTime()
    updates = fields.Dict()

    @pre_load
    def parse_dt(self, in_data, **kwargs):
        if in_data.get("event_time"):
            in_data["event_time"] = arrow.get(in_data["event_time"]).isoformat()
        return in_data
