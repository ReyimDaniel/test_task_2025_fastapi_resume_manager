from pydantic import BaseModel, ConfigDict


class ResumeBase(BaseModel):
    title: str
    description: str
    owner_id: int  # TODO Remove


class ResumeCreate(ResumeBase):
    pass


class ResumeRead(BaseModel):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class ResumeUpdate(ResumeBase):
    pass


class ResumeUpdatePartial(ResumeBase):
    title: str | None = None
    description: str | None = None


class Resume(ResumeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
