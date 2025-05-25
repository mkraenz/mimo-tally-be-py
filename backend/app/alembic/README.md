# Alembic

Generic single-database configuration.

## Naming convention

To automatically generate _proper_ migration files, constraints etc should be named, so they can be reverted properly if needed.

`app/models.py` defines our naming convention as

```py
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
target_metadata = SQLModel.metadata
target_metadata.naming_convention = NAMING_CONVENTION
```
