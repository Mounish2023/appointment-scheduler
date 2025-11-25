"""
SQLAlchemy Models for Dental Appointment Booking System
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Date, ForeignKey, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column, Date, DateTime, Boolean, Numeric, ForeignKey, func, UniqueConstraint
)
# Import Base from models.base
from .base import Base


# Enum types
class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class RecurringType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class DayOfWeek(enum.Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


# ============================================
# 1. USERS/CLIENTS TABLE
# ============================================
class User(Base):
    """Patient/Client table for dental appointment booking"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    # Dental-specific fields
    insurance_provider = Column(String(100))
    insurance_policy_number = Column(String(100))
    date_of_birth = Column(Date, nullable=False)

    # Medical history
    allergies = Column(Text)
    medical_conditions = Column(Text)
    current_medications = Column(Text)

    # Address information
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))

    # Timezone for appointment scheduling
    timezone = Column(String(50), default="America/Chicago", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")


# ============================================
# 2. SERVICE PROVIDERS/EMPLOYEES TABLE
# ============================================
class ServiceProvider(Base):
    """Dentists and dental hygienists who provide services"""
    __tablename__ = "service_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    # Professional information
    specialty = Column(String(100))  # e.g., "General Dentist", "Orthodontist", "Periodontist", "Endodontist"
    license_number = Column(String(50), unique=True, nullable=False)
    years_of_experience = Column(Integer)

    # Employment information
    is_active = Column(Boolean, default=True, nullable=False)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)

    # Scheduling
    timezone = Column(String(50), default="America/Chicago", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="provider")
    base_availability_rules = relationship("BaseAvailabilityRule", back_populates="provider", cascade="all, delete-orphan")
    # relationship to association objects (ProviderService)
    provider_services = relationship(
        "ProviderService",
        back_populates="provider",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    availability_exceptions = relationship("AvailabilityException", back_populates="provider", cascade="all, delete-orphan")

    # convenience many-to-many to Service (via the provider_services table)
    services = relationship(
        "Service",
        secondary="provider_services",
        back_populates="providers",
        viewonly=True  # set viewonly=True if you want to manage links via ProviderService objects
    )


# ============================================
# 3. SERVICES TABLE (Dental-specific)
# ============================================
class Service(Base):
    """Dental services/procedures that can be booked"""
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(255), nullable=False, index=True)
    service_code = Column(String(20), unique=True, nullable=False)  # e.g., D0120, D1110
    description = Column(Text)

    # Scheduling details
    duration_minutes = Column(Integer, nullable=False)
    buffer_time_minutes = Column(Integer, default=0)  # Time needed between appointments

    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)

    # Service category
    category = Column(String(100))  # e.g., "Preventive", "Restorative", "Cosmetic", "Emergency"

    # Indicates if service requires specific equipment or special scheduling
    requires_special_equipment = Column(Boolean, default=False)
    is_emergency_service = Column(Boolean, default=False)

    # Active/inactive status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="service")
    # relationship to association objects (ProviderService)
    provider_services = relationship(
        "ProviderService",
        back_populates="service",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    # convenience many-to-many to ServiceProvider
    providers = relationship(
        "ServiceProvider",
        secondary="provider_services",
        back_populates="services",
        viewonly=True
    )


# ============================================
# 4. APPOINTMENTS TABLE
# ============================================
class Appointment(Base):
    """Central table for all dental appointments"""
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("service_providers.id"), nullable=False, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)

    # Appointment timing (stored in UTC)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Display timezone (for user reference)
    timezone = Column(String(50), nullable=False)

    # Status
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False, index=True)

    # Recurring appointment support
    is_recurring = Column(Boolean, default=False, nullable=False)
    parent_appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)

    # Additional information
    notes = Column(Text)  # Special instructions or patient notes
    chief_complaint = Column(Text)  # Primary reason for visit

    # Cancellation tracking
    cancellation_reason = Column(Text)
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(String(100))  # user ID or staff name

    # Confirmation tracking
    confirmed_at = Column(DateTime(timezone=True))

    # Reminder tracking
    reminder_sent_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))  # Who created the appointment
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="appointments")
    provider = relationship("ServiceProvider", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    child_appointments = relationship("Appointment", backref="parent_appointment", remote_side=[id])
    recurring_pattern = relationship("RecurringPattern", back_populates="appointment", uselist=False, cascade="all, delete-orphan")
    exceptions = relationship("AppointmentException", back_populates="parent_appointment", cascade="all, delete-orphan")


# ============================================
# 5. RECURRING PATTERNS TABLE
# ============================================
class RecurringPattern(Base):
    """Stores recurrence rules for recurring appointments"""
    __tablename__ = "recurring_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False, unique=True)

    # Recurrence type
    recurring_type = Column(Enum(RecurringType), nullable=False)

    # Interval between occurrences (0 = every, 1 = every other, etc.)
    separation_count = Column(Integer, default=0, nullable=False)

    # For weekly patterns
    day_of_week = Column(Integer)  # 1-7 (1=Monday, 7=Sunday)

    # For monthly patterns
    day_of_month = Column(Integer)  # 1-31 or negative for last days
    week_of_month = Column(Integer)  # 1-5 (1=first, -1=last)

    # For yearly patterns
    month_of_year = Column(Integer)  # 1-12

    # End conditions (at least one should be set)
    max_occurrences = Column(Integer)  # Total number of occurrences
    end_date = Column(Date)  # When recurrence stops

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    appointment = relationship("Appointment", back_populates="recurring_pattern")


# ============================================
# 6. APPOINTMENT EXCEPTIONS TABLE
# ============================================
class AppointmentException(Base):
    """Handles modifications to individual instances of recurring appointments"""
    __tablename__ = "appointment_exceptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False, index=True)

    # Date of the exception
    exception_date = Column(Date, nullable=False, index=True)

    # Rescheduled time (if moved)
    new_start_time = Column(DateTime(timezone=True))
    new_end_time = Column(DateTime(timezone=True))

    # Exception type flags
    is_cancelled = Column(Boolean, default=False, nullable=False)
    is_rescheduled = Column(Boolean, default=False, nullable=False)

    # Reason for exception
    reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent_appointment = relationship("Appointment", back_populates="exceptions")


# ============================================
# Base Availability Table
# ============================================
class BaseAvailabilityRule(Base):
    """Defines provider's base working hours per day of week"""
    __tablename__ = "base_availability_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("service_providers.id"), nullable=False, index=True)

    # Day of week (1=Monday, 7=Sunday)
    day_of_week = Column(Integer, nullable=False)

    # Daily working window
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Effective date range
    effective_from = Column(Date, nullable=False)
    effective_until = Column(Date)  # Nullable for indefinite rules

    # Timezone
    timezone = Column(String(50), default="America/Chicago", nullable=False)

    # Additional information
    notes = Column(Text)  # e.g., "Regular working hours"

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    provider = relationship("ServiceProvider", back_populates="base_availability_rules")

# ============================================
# Availability Exceptions Table
# ============================================
class AvailabilityException(Base):
    """Defines intervals where provider is unavailable within base working hours"""
    __tablename__ = "availability_exceptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("service_providers.id"), nullable=False, index=True)

    # Specific date of the exception
    date = Column(Date, nullable=False)

    # Blocked interval on that date
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Reason for unavailability
    reason = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    provider = relationship("ServiceProvider", back_populates="availability_exceptions")

class ProviderService(Base):
    """
    Association object between ServiceProvider and Service.
    Composite primary key: (provider_id, service_id)
    Optional metadata columns (hourly_rate, is_primary, effective_from/until) are included.
    """
    __tablename__ = "provider_services"

    provider_id = Column(UUID(as_uuid=True), ForeignKey("service_providers.id", ondelete="CASCADE"), primary_key=True)
    service_id  = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True)

    # # Optional metadata for the relation
    # is_primary = Column(Boolean, nullable=False, default=False)   # optionally mark a provider's primary service
    # hourly_rate = Column(Numeric(10, 2), nullable=True)           # per-service rate (if needed)
    # effective_from = Column(Date, nullable=True)                  # when provider started offering this service
    # effective_until = Column(Date, nullable=True)                 # when provider stopped offering this service

    # audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationships back to models
    provider = relationship("ServiceProvider", back_populates="provider_services")
    service  = relationship("Service", back_populates="provider_services")

    __table_args__ = (
        UniqueConstraint("provider_id", "service_id", name="uq_provider_service"),
    )