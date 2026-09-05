import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("vaanirakshak.redis")


class InMemorySessionStore:
    """Async in-memory fallback session store when Redis is unavailable."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._chunks: Dict[str, List[Dict[str, Any]]] = {}
        self._risk_history: Dict[str, List[Dict[str, Any]]] = {}

    async def set_session(self, session_id: str, data: Dict[str, Any], ttl_sec: int = 1800) -> None:
        self._sessions[session_id] = {
            **data,
            "created_at": data.get("created_at", datetime.utcnow().isoformat())
        }
        if session_id not in self._chunks:
            self._chunks[session_id] = []
        if session_id not in self._risk_history:
            self._risk_history[session_id] = []

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    async def add_chunk(self, session_id: str, chunk_payload: Dict[str, Any]) -> None:
        if session_id in self._chunks:
            self._chunks[session_id].append(chunk_payload)

    async def get_chunks(self, session_id: str) -> List[Dict[str, Any]]:
        return self._chunks.get(session_id, [])

    async def add_risk_record(self, session_id: str, risk_record: Dict[str, Any]) -> None:
        if session_id in self._risk_history:
            self._risk_history[session_id].append(risk_record)
            if session_id in self._sessions:
                self._sessions[session_id]["current_risk_score"] = risk_record.get("risk_score", 0)
                self._sessions[session_id]["current_band"] = risk_record.get("band", "SAFE")

    async def get_risk_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self._risk_history.get(session_id, [])

    async def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        self._chunks.pop(session_id, None)
        self._risk_history.pop(session_id, None)


class RedisSessionManager:
    """Redis Session Manager with graceful in-memory fallback."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis_client = None
        self._fallback_store = InMemorySessionStore()
        self._use_fallback = True

    async def initialize(self):
        """Attempts to connect to Redis server; switches to in-memory fallback if connection fails."""
        try:
            import redis.asyncio as aioredis
            self._redis_client = aioredis.from_url(self.redis_url, decode_responses=True)
            await self._redis_client.ping()
            self._use_fallback = False
            logger.info("Connected to Redis server successfully.")
        except Exception as e:
            self._use_fallback = True
            logger.warning(f"Redis connection unavailable ({e}). Using in-memory session fallback.")

    async def create_session(self, session_id: str, metadata: Dict[str, Any], ttl_sec: int = 1800) -> None:
        if self._use_fallback:
            await self._fallback_store.set_session(session_id, metadata, ttl_sec)
        else:
            key = f"session:{session_id}"
            await self._redis_client.set(key, json.dumps(metadata), ex=ttl_sec)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self._use_fallback:
            return await self._fallback_store.get_session(session_id)
        else:
            key = f"session:{session_id}"
            data = await self._redis_client.get(key)
            return json.loads(data) if data else None

    async def append_audio_chunk(self, session_id: str, chunk_payload: Dict[str, Any]) -> None:
        if self._use_fallback:
            await self._fallback_store.add_chunk(session_id, chunk_payload)
        else:
            key = f"session:{session_id}:chunks"
            await self._redis_client.rpush(key, json.dumps(chunk_payload))

    async def record_risk_update(self, session_id: str, risk_record: Dict[str, Any]) -> None:
        if self._use_fallback:
            await self._fallback_store.add_risk_record(session_id, risk_record)
        else:
            key = f"session:{session_id}:risk_history"
            await self._redis_client.rpush(key, json.dumps(risk_record))
            session_key = f"session:{session_id}"
            session = await self.get_session(session_id)
            if session:
                session["current_risk_score"] = risk_record.get("risk_score", 0)
                session["current_band"] = risk_record.get("band", "SAFE")
                await self._redis_client.set(session_key, json.dumps(session), ex=1800)

    async def get_risk_history(self, session_id: str) -> List[Dict[str, Any]]:
        if self._use_fallback:
            return await self._fallback_store.get_risk_history(session_id)
        else:
            key = f"session:{session_id}:risk_history"
            items = await self._redis_client.lrange(key, 0, -1)
            return [json.loads(item) for item in items]

    async def close_session(self, session_id: str) -> None:
        if self._use_fallback:
            await self._fallback_store.delete_session(session_id)
        else:
            await self._redis_client.delete(f"session:{session_id}")
            await self._redis_client.delete(f"session:{session_id}:chunks")
            await self._redis_client.delete(f"session:{session_id}:risk_history")


# Global Singleton Manager
session_manager = RedisSessionManager(redis_url="redis://localhost:6379/0")
