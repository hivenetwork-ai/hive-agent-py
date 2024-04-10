from datetime import datetime

from sqlalchemy import delete, update
from sqlalchemy.future import select

from hive_agent.store import DataEntry


class Store:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def add(self, namespace, data):
        async with self.session_factory() as session:
            new_entry = DataEntry(namespace=namespace, data=data, timestamp=datetime.now())
            session.add(new_entry)
            await session.commit()
            await session.refresh(new_entry)

            return new_entry

    async def get(self, namespace):
        async with self.session_factory() as session:
            stmt = select(DataEntry).where(DataEntry.namespace == namespace)
            result = await session.execute(stmt)

            return result.scalars().all()

    async def get_by_id(self, namespace, entry_id):
        async with self.session_factory() as session:
            stmt = select(DataEntry).where(DataEntry.id == entry_id, DataEntry.namespace == namespace)
            result = await session.execute(stmt)

            return result.scalars().first()

    async def update(self, namespace, entry_id, new_data):
        async with self.session_factory() as session:
            stmt = (
                update(DataEntry)
                .where(DataEntry.id == entry_id, DataEntry.namespace == namespace)
                .values(new_data)
            )

            await session.execute(stmt)
            await session.commit()

    async def delete(self, namespace, entry_id):
        async with self.session_factory() as session:
            stmt = (
                delete(DataEntry)
                .where(DataEntry.id == entry_id, DataEntry.namespace == namespace)
            )

            await session.execute(stmt)
            await session.commit()
