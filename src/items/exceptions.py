from src.exceptions import BadRequest, NotFound
from src.items.constants import ErrorCode


class ItemNotFound(NotFound):
    DETAIL = ErrorCode.ITEM_NOT_FOUND


class ItemTitleTaken(BadRequest):
    DETAIL = ErrorCode.ITEM_TITLE_TAKEN
