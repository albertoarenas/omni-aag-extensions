import dataclasses
import uuid
import datetime

@dataclasses.dataclass
class Person:
    name: str
    role: str
    id: uuid.UUID

@dataclasses.dataclass
class Asset:
    name: str
    type: str
    id: uuid.UUID

@dataclasses.dataclass
class ReviewSession:
    name:str
    date:datetime.datetime
    id:uuid.UUID

@dataclasses.dataclass
class Context:
    asset: Asset
    time: float
    review_session: ReviewSession

@dataclasses.dataclass
class Note:
    giver: Person
    receiver: Person
    author: Person
    context: Context
    message: str
    latitude: float

    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)

    def to_dict(self):
        return dataclasses.asdict(self)

    # def to_json(self):
    #     return json.dumps(self, cls=NoteJsonEncoder)


# class NoteJsonEncoder(json.JSONEncoder):

#     def default(self, obj):
#         try:
#             to_serialize = obj.to_dict()
#             to_serialize["code"] = str(obj.code)
#             return to_serialize
#         except AttributeError:
#             return super().default(obj)