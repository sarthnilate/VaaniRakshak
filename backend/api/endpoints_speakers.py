import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.schemas.incidents import SpeakerProfilePayload, SpeakerProfileResponse
from backend.db.database import get_async_db, EnrolledSpeaker

router = APIRouter(prefix="/speakers", tags=["Consented Speaker Enrollment"])


@router.post("/enroll", response_model=SpeakerProfileResponse, status_code=status.HTTP_201_CREATED)
async def enroll_speaker_profile(
    payload: SpeakerProfilePayload,
    db: AsyncSession = Depends(get_async_db)
):
    """Enrolls a trusted speaker's biometric embedding vector with explicit user consent."""
    if not payload.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit user consent is mandatory for speaker profile enrollment."
        )

    speaker_id = f"spk_{uuid.uuid4().hex[:10]}"
    speaker = EnrolledSpeaker(
        speaker_id=speaker_id,
        display_name=payload.display_name,
        phone_number=payload.phone_number,
        consent_given=payload.consent_given,
        created_at=datetime.utcnow()
    )
    speaker.set_embedding(payload.embedding)

    db.add(speaker)
    await db.commit()
    await db.refresh(speaker)

    return SpeakerProfileResponse(
        speaker_id=speaker.speaker_id,
        display_name=speaker.display_name,
        phone_number=speaker.phone_number,
        consent_given=speaker.consent_given,
        created_at=speaker.created_at
    )


@router.get("", response_model=List[SpeakerProfileResponse])
async def list_enrolled_speakers(db: AsyncSession = Depends(get_async_db)):
    """Lists all consented speaker profiles enrolled on the system."""
    result = await db.execute(select(EnrolledSpeaker))
    speakers = result.scalars().all()
    return [
        SpeakerProfileResponse(
            speaker_id=spk.speaker_id,
            display_name=spk.display_name,
            phone_number=spk.phone_number,
            consent_given=spk.consent_given,
            created_at=spk.created_at
        )
        for spk in speakers
    ]
