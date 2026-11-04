from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

DepartmentCode = Literal["rrhh", "tecnico", "marketing"]


class AdminUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    departments: list[DepartmentCode] = Field(default_factory=list)


class AdminUserUpdate(BaseModel):
    role: Literal["user", "admin"] | None = None
    is_active: bool | None = None
    departments: list[DepartmentCode] | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Debe indicarse role, is_active o departments.")

        if "role" in self.model_fields_set and self.role is None:
            raise ValueError("El rol no puede ser nulo.")

        if "is_active" in self.model_fields_set and self.is_active is None:
            raise ValueError("El estado no puede ser nulo.")

        if "departments" in self.model_fields_set and self.departments is None:
            raise ValueError("Los departamentos no pueden ser nulos.")

        return self


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    departments: list[str]
    created_at: datetime

    @field_validator("departments", mode="before")
    @classmethod
    def department_codes(cls, value):
        return [
            department.code if hasattr(department, "code") else department
            for department in value
        ]

    model_config = {"from_attributes": True}
