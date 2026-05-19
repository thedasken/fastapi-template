from src.exceptions import NotFound
from src.items.constants import ErrorCode


class ItemNotFound(NotFound):
    DETAIL = ErrorCode.ITEM_NOT_FOUND
