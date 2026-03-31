from sqlalchemy import Column, Integer, String, JSON, DateTime
from database import Base
import datetime

class VTRecord(Base):
    __tablename__ = "vt_records"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True)
    type = Column(String) # 'domain', 'ip', or 'hash'
    data = Column(JSON)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
