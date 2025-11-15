from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.dental_appointment_models import User
from pydantic import BaseModel, ConfigDict
from datetime import date
class UserOut(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    phone: str | None = None
    insurance_provider: str | None = None
    insurance_policy_number: str | None = None
    date_of_birth: date | None = None
    allergies: list[str] | None = None
    medical_conditions: list[str] | None = None
    current_medications: list[str] | None = None
    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    timezone: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserService:
    """Service for handling user database operations"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[dict]:
        """Get a single user by ID"""
        user = await db.get(User, user_id)
        if not user:
            return None
            
        # Convert user to dict and handle date serialization
        user_dict = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'insurance_provider': user.insurance_provider,
            'insurance_policy_number': user.insurance_policy_number,
            'date_of_birth': str(user.date_of_birth) if user.date_of_birth else None,
            'allergies': user.allergies.split(',') if user.allergies else [],
            'medical_conditions': user.medical_conditions.split(',') if user.medical_conditions else [],
            'current_medications': user.current_medications.split(',') if user.current_medications else [],
            'street_address': user.street_address,
            'city': user.city,
            'state': user.state,
            'zip_code': user.zip_code,
            'timezone': user.timezone
        }
        
        return user_dict


    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get a single user by email"""
        user = await db.get(User, email)
        return UserOut.model_validate(user).model_dump()
