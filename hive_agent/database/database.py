import json
import os
import logging

from typing import Dict, Any, Optional, List

from sqlalchemy import Column, Integer, String, MetaData, Table, select, text, JSON
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


# TODO: get log level from config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs("hive-agent-data/db", exist_ok=True)
db_url = os.getenv(
    "HIVE_AGENT_DATABASE_URL", "sqlite+aiosqlite:///hive-agent-data/db/hive_agent.db"
)

engine = create_async_engine(db_url, echo=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class TableDefinition(Base):
    __tablename__ = "table_definitions"
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, unique=True, index=True)
    columns = Column(String)  # JSON string to store column definitions


async def initialize_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as session:
        yield session


class DatabaseManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_table(self, table_name: str, columns: Dict[str, str]):
        logger.info(f"Creating table {table_name} with columns {columns}")
        try:
            if not isinstance(columns, dict):
                raise ValueError("columns must be a dictionary")

            columns_json = json.dumps(columns)
            table_definition = TableDefinition(
                table_name=table_name, columns=columns_json
            )
            self.db.add(table_definition)
            await self.db.commit()
            logger.info(f"Table definition for {table_name} saved.")

            metadata = MetaData()
            columns_list = []
            for name, column_type in columns.items():
                if column_type == "JSON":
                    columns_list.append(Column(name, JSON))
                else:
                    columns_list.append(Column(name, eval(column_type)))
            columns_list.insert(0, Column("id", Integer, primary_key=True))
            table = Table(table_name, metadata, *columns_list)
            async with engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            logger.info(f"Table {table_name} created successfully.")
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating table {table_name}: {str(e)}")
            raise ValueError(f"Error creating table: {str(e)}")

    async def get_table_definition(self, table_name: str):
        logger.info(f"Retrieving table definition for {table_name}")
        try:
            result = await self.db.execute(
                select(TableDefinition).filter_by(table_name=table_name)
            )
            table_definition = result.scalars().first()
            if table_definition:
                logger.info(
                    f"Table definition for {table_name} retrieved successfully."
                )
                return table_definition.columns
            logger.warning(f"Table definition for {table_name} not found.")
            return None
        except SQLAlchemyError as e:
            logger.error(
                f"Error retrieving table definition for {table_name}: {str(e)}"
            )
            raise ValueError(f"Error retrieving table definition: {str(e)}")

    async def insert_data(self, table_name: str, data: Dict[str, Any]):
        logger.info(f"Inserting data into table {table_name}: {data}")
        try:
            columns_json = await self.get_table_definition(table_name)
            if not columns_json:
                raise ValueError(f"Table {table_name} does not exist.")

            columns = json.loads(columns_json)
            metadata = MetaData()
            columns_list = [
                Column(name, JSON if column_type == "JSON" else eval(column_type))
                for name, column_type in columns.items()
            ]
            columns_list.insert(0, Column("id", Integer, primary_key=True))
            table = Table(table_name, metadata, *columns_list)

            class_name = table_name.capitalize()
            model = type(
                class_name,
                (Base,),
                {
                    "__tablename__": table_name,
                    "__table__": table,
                    "__mapper_args__": {"eager_defaults": True},
                },
            )

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            instance = model(**data)
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            logger.info(
                f"Data inserted into table {table_name} successfully, id: {instance.id}"
            )
            return instance
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error inserting data into table {table_name}: {str(e)}")
            raise ValueError(f"Error inserting data: {str(e)}")

    async def read_data(
        self, table_name: str, filters: Optional[Dict[str, List[Any]]] = None
    ):
        logger.info(f"Reading data from table {table_name} with filters: {filters}")
        try:
            columns_json = await self.get_table_definition(table_name)
            if not columns_json:
                raise ValueError(f"Table {table_name} does not exist.")

            columns = json.loads(columns_json)
            metadata = MetaData()
            columns_list = [
                Column(name, JSON if column_type == "JSON" else eval(column_type))
                for name, column_type in columns.items()
            ]
            columns_list.insert(0, Column("id", Integer, primary_key=True))
            table = Table(table_name, metadata, *columns_list)

            class_name = table_name.capitalize()
            model = type(
                class_name,
                (Base,),
                {
                    "__tablename__": table_name,
                    "__table__": table,
                    "__mapper_args__": {"eager_defaults": True},
                },
            )

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            query = select(model)
            if filters:
                for key, values in filters.items():
                    if key == "details":
                        for value in values:
                            for sub_key, sub_value in value.items():
                                query = query.where(
                                    text(
                                        f"json_extract({key}, '$.{sub_key}') = :sub_value"
                                    )
                                ).params(sub_value=sub_value)
                    else:
                        query = query.filter(getattr(model, key).in_(values))

            result = await self.db.execute(query)
            print(f"result is actually - {result}")
            instances = result.scalars().all()
            data = [
                {column: getattr(instance, column) for column in columns.keys()}
                for instance in instances
            ]
            logger.info(f"Data read from table {table_name} successfully.")
            return data
        except SQLAlchemyError as e:
            logger.error(f"Error reading data from table {table_name}: {str(e)}")
            raise ValueError(f"Error reading data: {str(e)}")

    async def update_data(self, table_name: str, row_id: int, new_data: Dict[str, Any]):
        logger.info(
            f"Updating data in table {table_name} for id {row_id} with new data: {new_data}"
        )
        try:
            columns_json = await self.get_table_definition(table_name)
            if not columns_json:
                raise ValueError(f"Table {table_name} does not exist.")

            columns = json.loads(columns_json)
            metadata = MetaData()
            columns_list = [
                Column(name, JSON if column_type == "JSON" else eval(column_type))
                for name, column_type in columns.items()
            ]
            columns_list.insert(0, Column("id", Integer, primary_key=True))
            table = Table(table_name, metadata, *columns_list)

            class_name = table_name.capitalize()
            model = type(
                class_name,
                (Base,),
                {
                    "__tablename__": table_name,
                    "__table__": table,
                    "__mapper_args__": {"eager_defaults": True},
                },
            )

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            instance = await self.db.get(model, row_id)
            if instance:
                for key, value in new_data.items():
                    setattr(instance, key, value)
                await self.db.commit()
                await self.db.refresh(instance)
                logger.info(
                    f"Data in table {table_name} for id {row_id} updated successfully."
                )
            else:
                logger.warning(f"No data found with id {row_id} in table {table_name}.")
                raise ValueError(
                    f"No data found with id {row_id} in table {table_name}."
                )
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                f"Error updating data in table {table_name} for id {row_id}: {str(e)}"
            )
            raise ValueError(f"Error updating data: {str(e)}")

    async def delete_data(self, table_name: str, row_id: int):
        logger.info(f"Deleting data from table {table_name} for id {row_id}")
        try:
            columns_json = await self.get_table_definition(table_name)
            if not columns_json:
                raise ValueError(f"Table {table_name} does not exist.")

            columns = json.loads(columns_json)
            metadata = MetaData()
            columns_list = [
                Column(name, JSON if column_type == "JSON" else eval(column_type))
                for name, column_type in columns.items()
            ]
            columns_list.insert(0, Column("id", Integer, primary_key=True))
            table = Table(table_name, metadata, *columns_list)

            class_name = table_name.capitalize()
            model = type(
                class_name,
                (Base,),
                {
                    "__tablename__": table_name,
                    "__table__": table,
                    "__mapper_args__": {"eager_defaults": True},
                },
            )

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            instance = await self.db.get(model, row_id)
            if instance:
                await self.db.delete(instance)
                await self.db.commit()
                logger.info(
                    f"Data deleted from table {table_name} for id {row_id} successfully."
                )
            else:
                logger.warning(f"No data found with id {row_id} in table {table_name}.")
                raise ValueError(
                    f"No data found with id {row_id} in table {table_name}."
                )
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                f"Error deleting data from table {table_name} for id {row_id}: {str(e)}"
            )
            raise ValueError(f"Error deleting data: {str(e)}")
