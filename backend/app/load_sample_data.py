"""
Sample Data Loading Script for Dental Appointment Booking System

This script generates realistic sample data for all tables in the dental
appointment booking database.

Usage:
    python load_sample_data.py

Requirements:
    - SQLAlchemy
    - PostgreSQL (or modify connection string for other databases)
"""

import asyncio
from datetime import datetime, timedelta, time, date
from decimal import Decimal
import random
import os
import sys


# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your models and database configuration
from app.models.dental_appointment_models import (
    Base, User, ServiceProvider, Service, Appointment, 
    BaseAvailabilityRule, AvailabilityException, RecurringPattern, AppointmentStatus, 
    RecurringType, ProviderService
)
from app.database import engine, AsyncSessionLocal
from app.config import settings

# For async database operations
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


# ============================================
# SAMPLE DATA DEFINITIONS
# ============================================

# Dental services based on ADA procedure codes
DENTAL_SERVICES = [
    {
        "service_name": "Comprehensive Oral Evaluation",
        "service_code": "D0150",
        "description": "Complete evaluation of oral health including examination of hard and soft tissues",
        "duration_minutes": 45,
        "buffer_time_minutes": 15,
        "base_price": Decimal("150.00"),
        "category": "Preventive",
        "is_emergency_service": False
    },
    {
        "service_name": "Periodic Oral Evaluation",
        "service_code": "D0120",
        "description": "Routine dental check-up for established patients",
        "duration_minutes": 30,
        "buffer_time_minutes": 10,
        "base_price": Decimal("85.00"),
        "category": "Preventive",
        "is_emergency_service": False
    },
    {
        "service_name": "Adult Prophylaxis (Cleaning)",
        "service_code": "D1110",
        "description": "Professional teeth cleaning and polishing",
        "duration_minutes": 60,
        "buffer_time_minutes": 15,
        "base_price": Decimal("120.00"),
        "category": "Preventive",
        "is_emergency_service": False
    },
    {
        "service_name": "Fluoride Treatment",
        "service_code": "D1206",
        "description": "Topical fluoride application for cavity prevention",
        "duration_minutes": 15,
        "buffer_time_minutes": 5,
        "base_price": Decimal("45.00"),
        "category": "Preventive",
        "is_emergency_service": False
    },
    {
        "service_name": "Dental X-rays (Full Mouth)",
        "service_code": "D0210",
        "description": "Complete intraoral radiographic images",
        "duration_minutes": 30,
        "buffer_time_minutes": 10,
        "base_price": Decimal("180.00"),
        "category": "Diagnostic",
        "requires_special_equipment": True,
        "is_emergency_service": False
    },
    {
        "service_name": "Panoramic X-ray",
        "service_code": "D0330",
        "description": "Full mouth radiographic view of jaw and teeth",
        "duration_minutes": 20,
        "buffer_time_minutes": 5,
        "base_price": Decimal("130.00"),
        "category": "Diagnostic",
        "requires_special_equipment": True,
        "is_emergency_service": False
    },
    {
        "service_name": "Composite Filling (One Surface)",
        "service_code": "D2391",
        "description": "Tooth-colored filling for one surface cavity",
        "duration_minutes": 45,
        "buffer_time_minutes": 15,
        "base_price": Decimal("185.00"),
        "category": "Restorative",
        "is_emergency_service": False
    },
    {
        "service_name": "Composite Filling (Two Surfaces)",
        "service_code": "D2392",
        "description": "Tooth-colored filling for two surface cavity",
        "duration_minutes": 60,
        "buffer_time_minutes": 15,
        "base_price": Decimal("240.00"),
        "category": "Restorative",
        "is_emergency_service": False
    },
    {
        "service_name": "Root Canal Therapy (Anterior)",
        "service_code": "D3310",
        "description": "Endodontic treatment for front tooth",
        "duration_minutes": 90,
        "buffer_time_minutes": 30,
        "base_price": Decimal("850.00"),
        "category": "Endodontic",
        "is_emergency_service": False
    },
    {
        "service_name": "Root Canal Therapy (Molar)",
        "service_code": "D3330",
        "description": "Endodontic treatment for back tooth",
        "duration_minutes": 120,
        "buffer_time_minutes": 30,
        "base_price": Decimal("1250.00"),
        "category": "Endodontic",
        "is_emergency_service": False
    },
    {
        "service_name": "Crown - Porcelain",
        "service_code": "D2740",
        "description": "Porcelain crown to restore damaged tooth",
        "duration_minutes": 90,
        "buffer_time_minutes": 30,
        "base_price": Decimal("1350.00"),
        "category": "Restorative",
        "is_emergency_service": False
    },
    {
        "service_name": "Tooth Extraction (Simple)",
        "service_code": "D7140",
        "description": "Removal of tooth without complications",
        "duration_minutes": 30,
        "buffer_time_minutes": 15,
        "base_price": Decimal("225.00"),
        "category": "Oral Surgery",
        "is_emergency_service": False
    },
    {
        "service_name": "Tooth Extraction (Surgical)",
        "service_code": "D7210",
        "description": "Surgical removal of impacted or complicated tooth",
        "duration_minutes": 60,
        "buffer_time_minutes": 30,
        "base_price": Decimal("385.00"),
        "category": "Oral Surgery",
        "is_emergency_service": False
    },
    {
        "service_name": "Teeth Whitening",
        "service_code": "D9972",
        "description": "Professional in-office teeth whitening treatment",
        "duration_minutes": 90,
        "buffer_time_minutes": 15,
        "base_price": Decimal("450.00"),
        "category": "Cosmetic",
        "is_emergency_service": False
    },
    {
        "service_name": "Emergency Dental Exam",
        "service_code": "D0140",
        "description": "Urgent evaluation for dental pain or trauma",
        "duration_minutes": 30,
        "buffer_time_minutes": 10,
        "base_price": Decimal("120.00"),
        "category": "Emergency",
        "is_emergency_service": True
    },
    {
        "service_name": "Scaling and Root Planing (Per Quadrant)",
        "service_code": "D4341",
        "description": "Deep cleaning for gum disease treatment",
        "duration_minutes": 60,
        "buffer_time_minutes": 15,
        "base_price": Decimal("280.00"),
        "category": "Periodontic",
        "is_emergency_service": False
    },
    {
        "service_name": "Dental Implant Placement",
        "service_code": "D6010",
        "description": "Surgical placement of dental implant",
        "duration_minutes": 120,
        "buffer_time_minutes": 30,
        "base_price": Decimal("2200.00"),
        "category": "Oral Surgery",
        "requires_special_equipment": True,
        "is_emergency_service": False
    },
    {
        "service_name": "Orthodontic Consultation",
        "service_code": "D8660",
        "description": "Initial evaluation for braces or aligners",
        "duration_minutes": 45,
        "buffer_time_minutes": 15,
        "base_price": Decimal("95.00"),
        "category": "Orthodontic",
        "is_emergency_service": False
    }
]


# Sample patient data
SAMPLE_PATIENTS = [
    {
        "email": "john.smith@email.com",
        "password_hash": "$2b$12$KIXxSomeHashedPasswordHere123",  # In production, properly hash passwords
        "full_name": "John Smith",
        "phone": "(555) 123-4567",
        "insurance_provider": "Delta Dental",
        "insurance_policy_number": "DD123456789",
        "date_of_birth": date(1985, 3, 15),
        "allergies": "Penicillin",
        "medical_conditions": "None",
        "current_medications": "None",
        "street_address": "123 Main St",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60601",
        "timezone": "America/Chicago"
    },
    {
        "email": "sarah.johnson@email.com",
        "password_hash": "$2b$12$KIXxSomeHashedPasswordHere456",
        "full_name": "Sarah Johnson",
        "phone": "(555) 234-5678",
        "insurance_provider": "Cigna Dental",
        "insurance_policy_number": "CG987654321",
        "date_of_birth": date(1990, 7, 22),
        "allergies": "Latex",
        "medical_conditions": "Diabetes Type 2",
        "current_medications": "Metformin 500mg",
        "street_address": "456 Oak Ave",
        "city": "Naperville",
        "state": "IL",
        "zip_code": "60540",
        "timezone": "America/Chicago"
    },
    {
        "email": "michael.brown@email.com",
        "password_hash": "$2b$12$KIXxSomeHashedPasswordHere789",
        "full_name": "Michael Brown",
        "phone": "(555) 345-6789",
        "insurance_provider": "MetLife",
        "insurance_policy_number": "ML456789123",
        "date_of_birth": date(1978, 11, 8),
        "allergies": "None",
        "medical_conditions": "Hypertension",
        "current_medications": "Lisinopril 10mg",
        "street_address": "789 Elm Street",
        "city": "Aurora",
        "state": "IL",
        "zip_code": "60505",
        "timezone": "America/Chicago"
    },
    {
        "email": "emily.davis@email.com",
        "password_hash": "$2b$12$KIXxSomeHashedPasswordHere101",
        "full_name": "Emily Davis",
        "phone": "(555) 456-7890",
        "insurance_provider": "Aetna",
        "insurance_policy_number": "AE789123456",
        "date_of_birth": date(1995, 5, 30),
        "allergies": "Codeine",
        "medical_conditions": "Asthma",
        "current_medications": "Albuterol inhaler",
        "street_address": "321 Maple Dr",
        "city": "Joliet",
        "state": "IL",
        "zip_code": "60432",
        "timezone": "America/Chicago"
    },
    {
        "email": "david.wilson@email.com",
        "password_hash": "$2b$12$KIXxSomeHashedPasswordHere202",
        "full_name": "David Wilson",
        "phone": "(555) 567-8901",
        "insurance_provider": "United Healthcare",
        "insurance_policy_number": "UH321654987",
        "date_of_birth": date(1982, 9, 12),
        "allergies": "None",
        "medical_conditions": "None",
        "current_medications": "None",
        "street_address": "654 Pine St",
        "city": "Westmont",
        "state": "IL",
        "zip_code": "60559",
        "timezone": "America/Chicago"
    }
]


# Sample dentists/hygienists
SAMPLE_PROVIDERS = [
    {
        "email": "dr.anderson@dentalclinic.com",
        "full_name": "Dr. Robert Anderson",
        "phone": "(555) 111-2222",
        "specialty": "General Dentist",
        "license_number": "DDS-IL-12345",
        "years_of_experience": 15,
        "is_active": True,
        "hire_date": date(2010, 1, 15),
        "timezone": "America/Chicago"
    },
    {
        "email": "dr.martinez@dentalclinic.com",
        "full_name": "Dr. Maria Martinez",
        "phone": "(555) 222-3333",
        "specialty": "Orthodontist",
        "license_number": "DDS-IL-23456",
        "years_of_experience": 12,
        "is_active": True,
        "hire_date": date(2013, 6, 1),
        "timezone": "America/Chicago"
    },
    {
        "email": "dr.chen@dentalclinic.com",
        "full_name": "Dr. Lisa Chen",
        "phone": "(555) 333-4444",
        "specialty": "Endodontist",
        "license_number": "DDS-IL-34567",
        "years_of_experience": 10,
        "is_active": True,
        "hire_date": date(2015, 3, 20),
        "timezone": "America/Chicago"
    },
    {
        "email": "hygienist.taylor@dentalclinic.com",
        "full_name": "Jennifer Taylor, RDH",
        "phone": "(555) 444-5555",
        "specialty": "Dental Hygienist",
        "license_number": "RDH-IL-45678",
        "years_of_experience": 8,
        "is_active": True,
        "hire_date": date(2017, 9, 10),
        "timezone": "America/Chicago"
    }
]


async def load_provider_services(session, providers, services):
    """Associate providers with the services they offer"""
    print("\nLinking providers to services...")

    provider_services = []

    # Get services by category for easy matching
    def get_services_by_category(category):
        return [s for s in services if s.category == category]

    # Dr. Anderson (General Dentist)
    anderson_services = (
        get_services_by_category("Preventive") +
        get_services_by_category("Restorative") +
        get_services_by_category("Diagnostic") +
        get_services_by_category("Emergency")
    )

    for svc in anderson_services:
        ps = ProviderService(
            provider_id=providers[0].id,
            service_id=svc.id,
        )
        provider_services.append(ps)
        session.add(ps)

    # Dr. Martinez (Orthodontist)
    martinez_services = (
        get_services_by_category("Orthodontic") +
        [s for s in services if s.service_code in ["D0150", "D0210", "D0330"]]
    )
    for svc in martinez_services:
        ps = ProviderService(
            provider_id=providers[1].id,
            service_id=svc.id,
        )
        provider_services.append(ps)
        session.add(ps)

    # Dr. Chen (Endodontist)
    chen_services = [
        s for s in services if s.category in ["Endodontic", "Diagnostic", "Emergency"]
    ]
    for svc in chen_services:
        ps = ProviderService(
            provider_id=providers[2].id,
            service_id=svc.id,
        )
        provider_services.append(ps)
        session.add(ps)

    # Jennifer Taylor (Hygienist)
    taylor_services = [
        s for s in services if s.service_code in ["D1110", "D1206", "D0120", "D4341"]
    ]
    for svc in taylor_services:
        ps = ProviderService(
            provider_id=providers[3].id,
            service_id=svc.id,
        )
        provider_services.append(ps)
        session.add(ps)

    await session.commit()
    print(f"✓ Linked {len(provider_services)} provider-service relationships")
    return provider_services

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created successfully")


async def load_services(session):
    """Load dental services into database"""
    print("\nLoading dental services...")
    services = []
    for service_data in DENTAL_SERVICES:
        service = Service(**service_data)
        services.append(service)
        session.add(service)

    await session.commit()
    print(f"✓ Loaded {len(services)} dental services")
    return services


async def load_patients(session):
    """Load sample patients into database"""
    print("\nLoading sample patients...")
    patients = []
    for patient_data in SAMPLE_PATIENTS:
        patient = User(**patient_data)
        patients.append(patient)
        session.add(patient)

    await session.commit()
    print(f"✓ Loaded {len(patients)} patients")
    return patients


async def load_providers(session):
    """Load service providers into database"""
    print("\nLoading service providers...")
    providers = []
    for provider_data in SAMPLE_PROVIDERS:
        provider = ServiceProvider(**provider_data)
        providers.append(provider)
        session.add(provider)

    await session.commit()
    print(f"✓ Loaded {len(providers)} service providers")
    return providers



async def create_sample_availability(session, providers):
    """Create base availability and exceptions for providers"""
    print("\nCreating base availability and exceptions...")

    base_rules = []
    exceptions = []

    for provider in providers:
        # Base working hours: Monday to Friday 9:00 - 17:00
        for day in range(1, 6):  # 1=Monday, 5=Friday
            rule = BaseAvailabilityRule(
                provider_id=provider.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                effective_from=date(2024, 1, 1),
                effective_until=None,
                timezone="America/Chicago",
                notes="Regular working hours"
            )
            base_rules.append(rule)
            session.add(rule)

        # Lunch break: 12:00 - 13:00 as exception
        for day in range(1, 6):
            # For weekly recurring lunch, create exceptions for next 7 days as sample
            for d in range(0, 7):
                exception_date = date.today()  # or calculate actual date for day-of-week
                lunch_exception = AvailabilityException(
                    provider_id=provider.id,
                    date=exception_date,
                    start_time=time(12, 0),
                    end_time=time(13, 0),
                    reason="Lunch break"
                )
                exceptions.append(lunch_exception)
                session.add(lunch_exception)

    await session.commit()
    print(f"✓ Created {len(base_rules)} base rules and {len(exceptions)} exceptions")
    return base_rules, exceptions



async def create_sample_appointments(session, patients, providers, services):
    """Create sample appointments"""
    print("\nCreating sample appointments...")
    appointments = []

    # Get specific services for common appointments
    checkup_service = next((s for s in services if s.service_code == "D0120"), services[0])
    cleaning_service = next((s for s in services if s.service_code == "D1110"), services[0])
    filling_service = next((s for s in services if s.service_code == "D2391"), services[0])

    # Create appointments over the next 2 weeks
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    # Appointment 1: Regular checkup (scheduled)
    appt1 = Appointment(
        user_id=patients[0].id,
        provider_id=providers[0].id,
        service_id=checkup_service.id,
        start_time=base_date + timedelta(days=2),
        end_time=base_date + timedelta(days=2, minutes=checkup_service.duration_minutes),
        timezone="America/Chicago",
        status=AppointmentStatus.SCHEDULED,
        chief_complaint="Routine checkup",
        notes="Patient prefers morning appointments",
        created_by="patient"
    )
    appointments.append(appt1)
    session.add(appt1)

    # Appointment 2: Cleaning (confirmed)
    appt2 = Appointment(
        user_id=patients[1].id,
        provider_id=providers[3].id,  # Hygienist
        service_id=cleaning_service.id,
        start_time=base_date + timedelta(days=3, hours=1),
        end_time=base_date + timedelta(days=3, hours=1, minutes=cleaning_service.duration_minutes),
        timezone="America/Chicago",
        status=AppointmentStatus.CONFIRMED,
        chief_complaint="6-month cleaning",
        confirmed_at=datetime.now() - timedelta(days=1),
        created_by="patient"
    )
    appointments.append(appt2)
    session.add(appt2)

    # Appointment 3: Filling (scheduled)
    appt3 = Appointment(
        user_id=patients[2].id,
        provider_id=providers[0].id,
        service_id=filling_service.id,
        start_time=base_date + timedelta(days=5, hours=2),
        end_time=base_date + timedelta(days=5, hours=2, minutes=filling_service.duration_minutes),
        timezone="America/Chicago",
        status=AppointmentStatus.SCHEDULED,
        chief_complaint="Cavity on upper left molar",
        notes="Patient is anxious about needles",
        created_by="staff"
    )
    appointments.append(appt3)
    session.add(appt3)

    # Appointment 4: Past completed appointment
    past_appt = Appointment(
        user_id=patients[3].id,
        provider_id=providers[0].id,
        service_id=checkup_service.id,
        start_time=base_date - timedelta(days=14),
        end_time=base_date - timedelta(days=14, minutes=-checkup_service.duration_minutes),
        timezone="America/Chicago",
        status=AppointmentStatus.COMPLETED,
        chief_complaint="Regular checkup",
        notes="No issues found",
        created_by="patient"
    )
    appointments.append(past_appt)
    session.add(past_appt)

    # Appointment 5: Recurring appointment (every 6 months)
    recurring_appt = Appointment(
        user_id=patients[4].id,
        provider_id=providers[3].id,
        service_id=cleaning_service.id,
        start_time=base_date + timedelta(days=7),
        end_time=base_date + timedelta(days=7, minutes=cleaning_service.duration_minutes),
        timezone="America/Chicago",
        status=AppointmentStatus.SCHEDULED,
        is_recurring=True,
        chief_complaint="Regular cleaning",
        notes="Patient prefers 6-month cleaning schedule",
        created_by="patient"
    )
    appointments.append(recurring_appt)
    session.add(recurring_appt)
    await session.flush()  # Get the appointment ID

    # Create recurring pattern for the cleaning
    pattern = RecurringPattern(
        appointment_id=recurring_appt.id,
        recurring_type=RecurringType.MONTHLY,
        separation_count=5,  # Every 6 months (separation of 5 months)
        max_occurrences=4,  # 2 years worth
        day_of_month=7
    )
    session.add(pattern)

    await session.commit()
    print(f"✓ Created {len(appointments)} sample appointments")
    return appointments


async def async_main():
    """Async main function to load all sample data"""
    print("=" * 60)
    print("DENTAL APPOINTMENT BOOKING SYSTEM - SAMPLE DATA LOADER")
    print("=" * 60)

    # Create database tables
    await create_tables()

    # Create database session
    async with AsyncSessionLocal() as session:
        try:
            # Load all data
            services = await load_services(session)
            patients = await load_patients(session)
            providers = await load_providers(session)
            provider_services = await load_provider_services(session, providers, services)

            availability_rules = await create_sample_availability(session, providers)
            appointments = await create_sample_appointments(session, patients, providers, services)

            print("\n" + "=" * 60)
            print("✓ SAMPLE DATA LOADED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\nDatabase Summary:")
            print(f"  - Services: {len(services)}")
            print(f"  - Patients: {len(patients)}")
            print(f"  - Providers: {len(providers)}")
            print(f"  - Provider-Service Links: {len(provider_services)}")

            print(f"  - Availability Rules: {len(availability_rules)}")
            print(f"  - Appointments: {len(appointments)}")
            print("\nYou can now start using the dental appointment booking system!")

        except Exception as e:
            print(f"\n✗ Error loading data: {str(e)}")
            await session.rollback()
            raise


def main():
    """Synchronous wrapper for the async main function"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
