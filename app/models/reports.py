from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
import json
from app.db.base import Base

class ReportMixin:
    id = Column(Integer, primary_key=True, index=True)
    malicious_count = Column(Integer, default=0)
    suspicious_count = Column(Integer, default=0)
    harmless_count = Column(Integer, default=0)
    undetected_count = Column(Integer, default=0)
    total_votes_harmless = Column(Integer, default=0)
    total_votes_malicious = Column(Integer, default=0)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'raw_data'}
        try:
            d['raw_data'] = json.loads(self.raw_data) if self.raw_data else {}
        except Exception:
            d['raw_data'] = {}
        return d

class DomainReport(ReportMixin, Base):
    __tablename__ = "domain_reports"
    
    domain = Column(String, unique=True, index=True, nullable=False)
    reputation = Column(Integer, default=0)
    categories = Column(JSON, nullable=True)

class IPReport(ReportMixin, Base):
    __tablename__ = "ip_reports"

    ip_address = Column(String, unique=True, index=True, nullable=False)
    asn = Column(Integer, nullable=True)
    as_owner = Column(String, nullable=True)
    country = Column(String, nullable=True)
    continent = Column(String, nullable=True)
    reputation = Column(Integer, default=0)

class FileHashReport(ReportMixin, Base):
    __tablename__ = "file_hash_reports"

    file_hash = Column(String, unique=True, index=True, nullable=False)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    md5 = Column(String, nullable=True)
    sha1 = Column(String, nullable=True)
    sha256 = Column(String, nullable=True)
    meaningful_name = Column(String, nullable=True)
    popular_threat_classification = Column(JSON, nullable=True)
    reputation = Column(Integer, default=0)
