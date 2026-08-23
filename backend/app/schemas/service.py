from pydantic import BaseModel
from typing import Optional


class DepartmentResponse(BaseModel):
    id: int
    code: str
    name_en: str
    website_url: Optional[str] = None
    hotline: Optional[str] = None

    model_config = {"from_attributes": True}


class ServiceResponse(BaseModel):
    id: int
    service_code: str
    title_en: str
    description: Optional[str] = None
    processing_time: Optional[str] = None
    fee_description: Optional[str] = None
    department: DepartmentResponse

    model_config = {"from_attributes": True}


class ServiceListResponse(BaseModel):
    services: list[ServiceResponse]
    total: int
