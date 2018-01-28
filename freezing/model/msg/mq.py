import enum
from datetime import datetime
from typing import Dict, Any

from freezing.model.msg import BaseMessage, BaseSchema
from freezing.model.msg.strava import AspectType
from marshmallow import fields
from marshmallow_enum import EnumField


class DefinedTubes(enum.Enum):
    activity_update = 'activity-update'


class ActivityUpdate(BaseMessage):
    """
    Represents a Webhook Event Subscription Update.
    """
    operation: AspectType = None
    athlete_id: int = None
    activity_id: int = None
    event_time: datetime = None
    updates: Dict[str, Any] = None

    def __repr__(self):
        return '[Activity {} id={} athlete={}]'.format(self.operation.value if self.operation else '?',
                                                       self.activity_id, self.athlete_id)


class ActivityUpdateSchema(BaseSchema):
    """
    Represents a Webhook Event Subscription Update.
    """
    _model_class = ActivityUpdate

    operation = EnumField(AspectType)
    athlete_id = fields.Int()
    activity_id = fields.Int()
    event_time = fields.DateTime()
    updates = fields.Dict()