import datetime

from pydantic import BaseModel
from domain.user.user_schema import User


class AnswerCreate(BaseModel):
    content: str


class Answer(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime
    user: User | None
    question_id: int
    modify_date: datetime.datetime | None = None
    voter: list[User] = []


class AnswerUpdate(AnswerCreate):
    answer_id: int


class AnswerDelete(BaseModel):
    answer_id: int


class AnswerVote(BaseModel):
    answer_id: int
    

class AnswerList(BaseModel):
    total: int
    answer_list: list[Answer] = []
    