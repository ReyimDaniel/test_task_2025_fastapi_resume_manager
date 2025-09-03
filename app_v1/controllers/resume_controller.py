from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_v1.auth.service.jwt_service import get_current_user
from app_v1.models import User
from app_v1.core import db_helper
from app_v1.repositories import resume_repository
from app_v1.schemas.resume import ResumeRead, ResumeCreate, ResumeUpdate, ResumeUpdatePartial

router = APIRouter(tags=['resumes'])


@router.get('/', response_model=list[ResumeRead],
            summary="Получить список всех резюме из базы данных",
            description="Эндпоинт для получения списка всех резюме из базы данных.")
async def read_resumes(session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                       current_user: User = Depends(get_current_user)):
    return await resume_repository.get_resumes(session=session, owner_id=current_user.id)


@router.post('/', response_model=ResumeRead, status_code=status.HTTP_201_CREATED,
             summary="Создать новое резюме",
             description="Эндпоинт для создания нового резюме. ")
async def create_resume(
        resume_in: ResumeCreate,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user: User = Depends(get_current_user)
):
    return await resume_repository.create_resume(
        session=session,
        resume_in=resume_in,
        owner_id=current_user.id
    )


async def get_resume_by_id(resume_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                           current_user: User = Depends(get_current_user)):
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if not resume or resume.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get('/{resume_id}', response_model=ResumeRead,
            summary="Получить информацию о конкретном резюме по его ID.",
            description="Эндпоинт для получения информации о существующем резюме из базы данных. "
                        "Необходимо ввести ID резюме.")
async def get_resume(resume: ResumeRead = Depends(get_resume_by_id)):
    return resume


@router.put('/{resume_id}', response_model=ResumeRead,
            summary="Обновить всю информацию в резюме",
            description="Эндпоинт для обновления всей информации в резюме, существующего в базе данных. ")
async def update_resume(resume_id: int, resume_update: ResumeUpdate,
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                        current_user: User = Depends(get_current_user)):
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if not resume or resume.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return await resume_repository.update_resume(session, resume, resume_update, partial=False)


@router.patch("/{resume_id}", response_model=ResumeRead,
              summary="Обновить информацию в резюме частично",
              description="Эндпоинт для обновления некоторой информации в резюме, существующего в базе данных. ")
async def partial_update_resume(resume_id: int, resume_update: ResumeUpdatePartial,
                                session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                                current_user: User = Depends(get_current_user)):
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if not resume or resume.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return await resume_repository.update_resume(session, resume, resume_update, partial=True)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удалить резюме",
               description="Эндпоинт для удаления резюме, существующего в базы данных. "
                           "Необходимо ввести ID резюме, которое нужно удалить.")
async def delete_resume(resume_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                        current_user: User = Depends(get_current_user)):
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if not resume or resume.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    await resume_repository.delete_resume(session, resume)
    return None
