import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.cache import cache_service
from app.services.virustotal_client import VirusTotalClient
from app.models.reports import DomainReport, IPReport, FileHashReport

class PipelineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _extract_stats(self, data: dict) -> tuple:
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        votes = attrs.get("total_votes", {})
        return (
            stats.get("malicious", 0),
            stats.get("suspicious", 0),
            stats.get("harmless", 0),
            stats.get("undetected", 0),
            votes.get("harmless", 0),
            votes.get("malicious", 0)
        )

    async def get_domain(self, domain: str, force_refresh: bool = False) -> dict:
        if not force_refresh:
            cached = await cache_service.get_domain(domain)
            if cached:
                cached["source"] = "cache"
                return cached
            
            result = await self.db.execute(select(DomainReport).filter_by(domain=domain))
            record = result.scalars().first()
            if record:
                data = record.to_dict()
                await cache_service.set_domain(domain, data)
                data["source"] = "database"
                return data

        async with VirusTotalClient() as vt_client:
            vt_data = await vt_client.get_domain_report(domain)

        if not vt_data:
            return {"error": "not_found", "domain": domain}

        attrs = vt_data.get("data", {}).get("attributes", {})
        malicious, suspicious, harmless, undetected, votes_harmless, votes_malicious = self._extract_stats(vt_data)
        
        result = await self.db.execute(select(DomainReport).filter_by(domain=domain))
        record = result.scalars().first()

        if not record:
            record = DomainReport(domain=domain)
            self.db.add(record)

        record.malicious_count = malicious
        record.suspicious_count = suspicious
        record.harmless_count = harmless
        record.undetected_count = undetected
        record.total_votes_harmless = votes_harmless
        record.total_votes_malicious = votes_malicious
        record.reputation = attrs.get("reputation", 0)
        record.categories = attrs.get("categories", {})
        record.raw_data = json.dumps(vt_data)

        await self.db.flush()

        data = record.to_dict()
        await cache_service.set_domain(domain, data)
        data["source"] = "virustotal"
        return data

    async def get_ip(self, ip_address: str, force_refresh: bool = False) -> dict:
        if not force_refresh:
            cached = await cache_service.get_ip(ip_address)
            if cached:
                cached["source"] = "cache"
                return cached
            
            result = await self.db.execute(select(IPReport).filter_by(ip_address=ip_address))
            record = result.scalars().first()
            if record:
                data = record.to_dict()
                await cache_service.set_ip(ip_address, data)
                data["source"] = "database"
                return data

        async with VirusTotalClient() as vt_client:
            vt_data = await vt_client.get_ip_report(ip_address)

        if not vt_data:
            return {"error": "not_found", "ip_address": ip_address}

        attrs = vt_data.get("data", {}).get("attributes", {})
        malicious, suspicious, harmless, undetected, votes_harmless, votes_malicious = self._extract_stats(vt_data)
        
        result = await self.db.execute(select(IPReport).filter_by(ip_address=ip_address))
        record = result.scalars().first()

        if not record:
            record = IPReport(ip_address=ip_address)
            self.db.add(record)

        record.malicious_count = malicious
        record.suspicious_count = suspicious
        record.harmless_count = harmless
        record.undetected_count = undetected
        record.total_votes_harmless = votes_harmless
        record.total_votes_malicious = votes_malicious
        record.asn = attrs.get("asn")
        record.as_owner = attrs.get("as_owner")
        record.country = attrs.get("country")
        record.continent = attrs.get("continent")
        record.reputation = attrs.get("reputation", 0)
        record.raw_data = json.dumps(vt_data)

        await self.db.flush()

        data = record.to_dict()
        await cache_service.set_ip(ip_address, data)
        data["source"] = "virustotal"
        return data

    async def get_file_hash(self, file_hash: str, force_refresh: bool = False) -> dict:
        if not force_refresh:
            cached = await cache_service.get_hash(file_hash)
            if cached:
                cached["source"] = "cache"
                return cached
            
            result = await self.db.execute(select(FileHashReport).filter_by(file_hash=file_hash))
            record = result.scalars().first()
            if record:
                data = record.to_dict()
                await cache_service.set_hash(file_hash, data)
                data["source"] = "database"
                return data

        async with VirusTotalClient() as vt_client:
            vt_data = await vt_client.get_file_report(file_hash)

        if not vt_data:
            return {"error": "not_found", "file_hash": file_hash}

        attrs = vt_data.get("data", {}).get("attributes", {})
        malicious, suspicious, harmless, undetected, votes_harmless, votes_malicious = self._extract_stats(vt_data)
        
        result = await self.db.execute(select(FileHashReport).filter_by(file_hash=file_hash))
        record = result.scalars().first()

        if not record:
            record = FileHashReport(file_hash=file_hash)
            self.db.add(record)

        record.malicious_count = malicious
        record.suspicious_count = suspicious
        record.harmless_count = harmless
        record.undetected_count = undetected
        record.total_votes_harmless = votes_harmless
        record.total_votes_malicious = votes_malicious
        
        names = attrs.get("names", [])
        record.file_name = names[0] if names else None
        record.file_type = attrs.get("type_description")
        record.file_size = attrs.get("size")
        record.md5 = attrs.get("md5")
        record.sha1 = attrs.get("sha1")
        record.sha256 = attrs.get("sha256", file_hash)
        record.meaningful_name = attrs.get("meaningful_name")
        record.popular_threat_classification = attrs.get("popular_threat_classification")
        record.reputation = attrs.get("reputation", 0)
        record.raw_data = json.dumps(vt_data)

        await self.db.flush()

        data = record.to_dict()
        await cache_service.set_hash(file_hash, data)
        data["source"] = "virustotal"
        return data
