from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_v1.schemas.resume import Resume
from app_v1.core import db_helper
from app_v1.repositories import resume_repository
from app_v1.schemas.resume import ResumeRead, ResumeCreate, ResumeUpdate, ResumeUpdatePartial

router = APIRouter(tags=['resumes'])


@router.get('/', response_model=list[Resume],
            summary="Получить список всех резюме из базы данных",
            description="Эндпоинт для получения списка всех резюме из базы данных.")
async def get_all_resumes(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await resume_repository.get_all_resumes(session=session)


@router.post('/', response_model=ResumeRead, status_code=status.HTTP_201_CREATED,
             summary="Создать новое резюме",
             description="Эндпоинт для создания нового резюме. ")
async def create_resume(resume_in: ResumeCreate,
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await resume_repository.create_resume(session=session, resume_in=resume_in)


async def get_resume_by_id(resume_id: Annotated[int, Path],
                           session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> Resume:
    resume = await resume_repository.get_resume_by_id(session=session, resume_id=resume_id)
    if resume is not None:
        return resume
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Resume {resume_id} not found")


@router.get('/{resume_id}', response_model=Resume,
            summary="Получить информацию о конкретном резюме по его ID.",
            description="Эндпоинт для получения информации о существующем резюме из базы данных. "
                        "Необходимо ввести ID резюме.")
async def get_resume(resume: Resume = Depends(get_resume_by_id)):
    return resume


@router.put('/{resume_id}', response_model=Resume,
            summary="Обновить всю информацию в резюме",
            description="Эндпоинт для обновления всей информации в резюме, существующего в базе данных. ")
async def update_resume(resume_update: ResumeUpdate,
                        resume: Resume = Depends(get_resume_by_id),
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await resume_repository.update_resume(session=session, resume=resume, resume_update=resume_update)


@router.patch("/{resume_id}", response_model=Resume,
            summary="Обновить информацию в резюме частично",
            description="Эндпоинт для обновления некоторой информации в резюме, существующего в базе данных. ")
async def update_resume_partial(resume_update: ResumeUpdatePartial,
                                resume: Resume = Depends(get_resume_by_id),
                                session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await resume_repository.update_resume(session=session, resume=resume, resume_update=resume_update,
                                                 partial=True)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Удалить резюме",
            description="Эндпоинт для удаления резюме, существующего в базы данных. "
                        "Необходимо ввести ID резюме, которое нужно удалить.")
async def delete_resume(resume: Resume = Depends(get_resume_by_id),
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await resume_repository.delete_resume(session=session, resume=resume)
