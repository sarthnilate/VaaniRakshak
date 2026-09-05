import json
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, Column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.config import settings

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EnrolledSpeaker(Base):
    __tablename__ = "enrolled_speakers"

    speaker_id = Column(String, primary_key=True)
    display_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, index=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    embedding_json = Column(Text, nullable=False)  # JSON-encoded 192-d float array
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_embedding(self, embedding_vector: list[float]) -> None:
        self.embedding_json = json.dumps(embedding_vector)

    def get_embedding(self) -> list[float]:
        return json.loads(self.embedding_json)


class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    caller_phone = Column(String, nullable=False)
    peak_risk_score = Column(Integer, nullable=False)
    risk_band = Column(String, nullable=False)
    evidence_json = Column(Text, nullable=False)
    action_taken = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AttackLabProvenance(Base):
    __tablename__ = "attack_lab_provenance"

    provenance_id = Column(String, primary_key=True)
    sample_id = Column(String, nullable=False, index=True)
    generator_family = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    reference_speaker_id = Column(String, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)
    consent_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Async Engine & Session Setup
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """Initializes database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injector for database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
