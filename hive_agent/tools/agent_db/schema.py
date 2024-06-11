from sqlalchemy import create_engine, MetaData


def get_db_schemas(db_url: str):
    """
    Connect to the database specified by db_url, reflect its schema,
    and return a dictionary mapping table names to their schema definitions.

    :param db_url: The database URL connection string.
    :return: A dictionary where each key is a table name and the value is a list of dictionaries
             containing column details such as name, type, primary key status, and nullable status.
    """

    engine = create_engine(db_url)
    metadata = MetaData()

    metadata.reflect(engine)

    schemas = {}
    for table_name, table in metadata.tables.items():
        columns = []
        for column in table.columns:
            columns.append(
                {
                    "name": column.name,
                    "type": str(column.type),
                    "primary_key": column.primary_key,
                    "nullable": column.nullable,
                }
            )
        schemas[table_name] = columns
    return schemas
