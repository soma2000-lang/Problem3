from sqlmodel import Session

from app import crud
from app.models import TaskModel,TaskCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_task(db: Session) -> TaskCreate:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = TaskModel(title=title, description=description)
    return crud.create_task(session=db, item_in=item_in, owner_id=owner_id)