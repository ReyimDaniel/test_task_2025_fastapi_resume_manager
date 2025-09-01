from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from app_v1.models.resume import Resume
from app_v1.schemas.resume import ResumeCreate, ResumeUpdate, ResumeUpdatePartial


async def get_all_resumes(session: AsyncSession, ) -> list[Resume]:
    stmt = select(Resume).order_by(Resume.id)
    result: Result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_resume_by_id(session: AsyncSession, resume_id: int) -> Resume | None:
    return await session.get(Resume, resume_id)


async def create_resume(session: AsyncSession, resume_in: ResumeCreate) -> Resume:
    db_resume = Resume(title=resume_in.title,
                       description=resume_in.description,
                       owner_id=resume_in.owner_id)
    session.add(db_resume)
    await session.commit()
    await session.refresh(db_resume)
    return db_resume


async def update_resume(session: AsyncSession, resume: Resume, resume_update: ResumeUpdate | ResumeUpdatePartial,
                        partial: bool = False, ) -> Resume:
    for key, value in resume_update.model_dump(exclude_unset=partial).items():
        setattr(resume, key, value)
    await session.commit()
    await session.refresh(resume)
    return resume


async def delete_resume(session: AsyncSession, resume: Resume) -> None:
    await session.delete(resume)
    await session.commit()
