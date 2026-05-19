# Import each feature's models module so its Table objects are registered on
# metadata before Alembic autogenerate runs. Add one import per feature here.
from src.items import models as items_models  # noqa: F401
