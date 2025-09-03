from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.templating import Jinja2Templates

from app.app_v1.core import db_helper
from app.app_v1.auth.service.jwt_service import create_access_token, decode_jwt_token, verify_password
from app.app_v1.models.user import User
from app.app_v1.schemas.resume import ResumeCreate, ResumeUpdate, ResumeUpdatePartial
from app.app_v1.repositories import user_repository, resume_repository
from app.app_v1.schemas.user import UserCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/login")
async def login_submit(
        email: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    db_user = await user_repository.get_user_by_email(session, email)
    if not db_user or not verify_password(password, db_user.password):
        return RedirectResponse("/login?msg=Неверные данные", status_code=HTTP_303_SEE_OTHER)
    token = create_access_token({"sub": db_user.email})
    response = RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.post("/register")
async def register_user(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    exists = await user_repository.get_user_by_email(session, email)
    if exists:
        return RedirectResponse("/register?msg=Email уже зарегистрирован", status_code=HTTP_303_SEE_OTHER)
    await user_repository.create_user(session, UserCreate(name=name, email=email, password=password))
    return RedirectResponse("/login?msg=Регистрация успешна! Теперь войдите", status_code=HTTP_303_SEE_OTHER)


async def get_current_user_from_cookie(request: Request, session: AsyncSession):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_jwt_token(token)
    email = payload.get("sub")
    if not email:
        return None
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user


@router.get("/index")
async def index(request: Request, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    resumes = await resume_repository.get_resumes(session, owner_id=user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "resumes": resumes})


@router.post("/create_resume")
async def create_resume(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    await resume_repository.create_resume(session, ResumeCreate(title=title, description=description), owner_id=user.id)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/delete_resume/{resume_id}")
async def delete_resume(resume_id: int, request: Request,
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if resume and resume.owner_id == user.id:
        await resume_repository.delete_resume(session, resume)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/update_resume")
async def update_resume(
        resume_id: int = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        request: Request = None,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if resume and resume.owner_id == user.id:
        await resume_repository.update_resume(session, resume, ResumeUpdate(title=title, description=description))
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/update_resume_partial")
async def update_resume_partial(
        resume_id: int = Form(...),
        title: str | None = Form(None),
        description: str | None = Form(None),
        request: Request = None,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if not resume or resume.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    update_data = {
        "title": title if title and title.strip() else None,
        "description": description if description and description.strip() else None,
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}
    if update_data:
        resume_update = ResumeUpdatePartial(**update_data)
        await resume_repository.update_resume(session, resume, resume_update, partial=True)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/improve_resume")
async def improve_resume_web(
        resume_id: int = Form(...),
        request: Request = None,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    resume = await resume_repository.get_resume_by_id(session, resume_id)
    if resume and resume.owner_id == user.id:
        await resume_repository.improve_resume(session, resume)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)
