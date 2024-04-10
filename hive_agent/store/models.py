from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DataEntry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    namespace = Column(String)
    timestamp = Column(DateTime)
    data = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "namespace": self.namespace,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "data": self.data
        }
