from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr
    
    role: str

    departments: list[str] = Field(default_factory=list)

    @field_validator("departments", mode="before")
    @classmethod
    def department_codes(cls, value):
        return [
            department.code if hasattr(department, "code") else department
            for department in value
        ]

    model_config = {
        "from_attributes": True,
    }


class LoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user: UserResponse
