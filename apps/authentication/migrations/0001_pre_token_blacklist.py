"""Drop UNIQUE constraints on token_blacklist tables that block
simplejwt's 0008_migrate_to_bigautofield from ALTER-ing the token_id column
on SQL Server. SQL Server refuses to alter a column that has dependent
constraints; we drop them here and let subsequent simplejwt migrations
recreate what is needed.

This is a no-op on non-SQL Server engines (e.g. SQLite used in tests).
"""
from django.db import migrations


def drop_unique_constraints(apps, schema_editor):
    if schema_editor.connection.vendor != 'microsoft' and schema_editor.connection.vendor != 'mssql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            DECLARE @sql NVARCHAR(MAX) = N'';

            SELECT @sql += 'ALTER TABLE [token_blacklist_outstandingtoken] DROP CONSTRAINT '
                         + QUOTENAME(name) + ';' + CHAR(13)
            FROM sys.key_constraints
            WHERE parent_object_id = OBJECT_ID('token_blacklist_outstandingtoken')
              AND type = 'UQ';

            SELECT @sql += 'ALTER TABLE [token_blacklist_blacklistedtoken] DROP CONSTRAINT '
                         + QUOTENAME(name) + ';' + CHAR(13)
            FROM sys.key_constraints
            WHERE parent_object_id = OBJECT_ID('token_blacklist_blacklistedtoken')
              AND type = 'UQ';

            EXEC sp_executesql @sql;
        """)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('token_blacklist', '0007_auto_20171017_2214'),
    ]

    operations = [
        migrations.RunPython(drop_unique_constraints, noop_reverse),
    ]
