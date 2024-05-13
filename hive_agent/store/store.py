import logging
import sys
from datetime import datetime

from sqlalchemy import delete, update
from sqlalchemy.future import select

from hive_agent.store import DataEntry

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class Store:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        logging.info("Database session initialized")

    async def add(self, namespace, data):
        async with self.session_factory() as session:
            new_entry = DataEntry(namespace=namespace, data=data, timestamp=datetime.now())
            session.add(new_entry)
            await session.commit()
            await session.refresh(new_entry)
            logging.info(f"Added new entry: {new_entry.id} in namespace {namespace}")
            return new_entry

    async def get(self, namespace):
        async with self.session_factory() as session:
            stmt = select(DataEntry).where(DataEntry.namespace == namespace)
            result = await session.execute(stmt)
            logging.info(f"Retrieved entries for namespace {namespace}")
            return result.scalars().all()

    async def get_by_id(self, namespace, entry_id):
        async with self.session_factory() as session:
            stmt = select(DataEntry).where(DataEntry.id == entry_id, DataEntry.namespace == namespace)
            result = await session.execute(stmt)
            logging.info(f"Retrieved entry by ID {entry_id} for namespace {namespace}")
            return result.scalars().first()

    async def update(self, namespace, entry_id, new_data):
        async with self.session_factory() as session:
            stmt = (
                update(DataEntry)
                .where(DataEntry.id == entry_id, DataEntry.namespace == namespace)
                .values(new_data)
            )
            logging.info(f"Updated entry {entry_id} in namespace {namespace}")
            await session.execute(stmt)
            await session.commit()

    async def delete(self, namespace, entry_id):
        async with self.session_factory() as session:
            stmt = (
                delete(DataEntry)
                .where(DataEntry.id == entry_id, DataEntry.namespace == namespace)
            )
            logging.info(f"Deleted entry {entry_id} from namespace {namespace}")
            await session.execute(stmt)
            await session.commit()
