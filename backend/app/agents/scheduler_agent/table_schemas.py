table_schemas = {
    "users": {
        "table_name": "users",
        "description": "Patient/Client table for dental appointment booking.",
        "columns": [
            {
                "name": "id",
                "description": "Unique ID for the user.",
                "use_cases": ["Used to uniquely identify users in the system and link them to appointments."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "email",
                "description": "User's email address.",
                "use_cases": ["Used for authentication, sending appointment confirmations, and reminders."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "password_hash",
                "description": "Encrypted password.",
                "use_cases": ["Used for secure user authentication during login."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "full_name",
                "description": "User's full name.",
                "use_cases": ["Used for display purposes in the UI and communication."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "phone",
                "description": "User's phone number.",
                "use_cases": ["Used for SMS reminders and urgent contact."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "insurance_provider",
                "description": "Name of insurance provider.",
                "use_cases": ["Used for billing and insurance verification."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "insurance_policy_number",
                "description": "User's insurance policy number.",
                "use_cases": ["Used for processing insurance claims."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "date_of_birth",
                "description": "User's date of birth.",
                "use_cases": ["Used for age verification and medical record requirements."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "allergies",
                "description": "User's allergy information.",
                "use_cases": ["Used to alert providers of potential medical risks during treatment."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "medical_conditions",
                "description": "User's medical conditions.",
                "use_cases": ["Used to inform providers of relevant health history."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "current_medications",
                "description": "Medications the user currently takes.",
                "use_cases": ["Used to check for drug interactions."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "street_address",
                "description": "User's street address.",
                "use_cases": ["Used for billing and mailing correspondence."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "city",
                "description": "User's city of residence.",
                "use_cases": ["Used for demographic analysis and billing."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "state",
                "description": "User's state of residence.",
                "use_cases": ["Used for billing and regional compliance."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "zip_code",
                "description": "User's postal code.",
                "use_cases": ["Used for location-based services and billing."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "timezone",
                "description": "User's preferred timezone.",
                "use_cases": ["Used to display appointment times in the user's local time."],
                "cardinality": "low",
                "unique_values": ["America/Chicago", "America/New_York", "America/Los_Angeles", "America/Denver"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when the user was created.",
                "use_cases": ["Used for auditing and account age tracking."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when the user was last updated.",
                "use_cases": ["Used for auditing and tracking profile changes."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "service_providers": {
        "table_name": "service_providers",
        "description": "Dentists and dental hygienists who provide services.",
        "columns": [
            {
                "name": "id",
                "description": "Unique ID for the service provider.",
                "use_cases": ["Used to identify providers and link them to services and appointments."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "email",
                "description": "Provider's email address.",
                "use_cases": ["Used for login, system notifications, and schedule updates."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "full_name",
                "description": "Provider's full name.",
                "use_cases": ["Used for display to users when booking appointments."],
                "cardinality": "high",
                "unique_values": ["Dr. Lisa Chen", "Jennifer Taylor, RDH", "Dr. Maria Martinez", "Dr. Robert Anderson"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "phone",
                "description": "Provider's phone number.",
                "use_cases": ["Used for administrative contact."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "specialty",
                "description": "Provider's dental specialty.",
                "use_cases": ["Used to filter providers based on patient needs (e.g., Orthodontist)."],
                "cardinality": "low",
                "unique_values": ["General Dentist", "Orthodontist", "Periodontist", "Endodontist"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "license_number",
                "description": "Provider's license ID.",
                "use_cases": ["Used for regulatory compliance and verification."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "years_of_experience",
                "description": "Years of experience in practice.",
                "use_cases": ["Used to display provider expertise to patients."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "is_active",
                "description": "Whether the provider is currently employed.",
                "use_cases": ["Used to filter available providers for booking."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "hire_date",
                "description": "Date the provider was hired.",
                "use_cases": ["Used for HR records."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "termination_date",
                "description": "Date the provider was terminated.",
                "use_cases": ["Used for historical records and preventing new bookings."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "timezone",
                "description": "Provider's timezone.",
                "use_cases": ["Used to manage the provider's schedule in their local time."],
                "cardinality": "low",
                "unique_values": ["America/Chicago"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when provider record was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when provider record was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "services": {
        "table_name": "services",
        "description": "Dental services/procedures that can be booked.",
        "columns": [
            {
                "name": "id",
                "description": "Unique ID for the service.",
                "use_cases": ["Used to identify services in bookings and billing."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "service_name",
                "description": "Name of the dental service.",
                "use_cases": ["Used for display in the booking menu (e.g., 'Teeth Cleaning')."],
                "cardinality": "medium",
                "unique_values": ["Panoramic X-ray",
"Comprehensive Oral Evaluation",
"Composite Filling (Two Surfaces)",
"Adult Prophylaxis (Cleaning)",
"Orthodontic Consultation",
"Tooth Extraction (Surgical)",
"Teeth Whitening",
"Fluoride Treatment",
"Crown - Porcelain",
"Dental X-rays (Full Mouth)",
"Dental Implant Placement",
"Emergency Dental Exam",
"Tooth Extraction (Simple)",
"Periodic Oral Evaluation",
"Root Canal Therapy (Anterior)",
"Composite Filling (One Surface)",
"Root Canal Therapy (Molar)",
"Scaling and Root Planing (Per Quadrant)"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "service_code",
                "description": "Standardized dental procedure code.",
                "use_cases": ["Used for insurance billing and standardization (e.g., CDT codes)."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "description",
                "description": "Description of the service.",
                "use_cases": ["Used to inform patients about what the service entails."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "duration_minutes",
                "description": "Length of service in minutes.",
                "use_cases": ["Used to calculate appointment slots and schedule availability."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "buffer_time_minutes",
                "description": "Buffer time after service.",
                "use_cases": ["Used to allow for room preparation between appointments."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "base_price",
                "description": "Base price of the service.",
                "use_cases": ["Used for calculating estimated costs and billing."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "category",
                "description": "Category of dental service.",
                "use_cases": ["Used for grouping services in the UI (e.g., 'Preventive', 'Cosmetic')."],
                "cardinality": "low",
                "unique_values": ["Preventive", "Restorative", "Cosmetic", "Emergency"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "requires_special_equipment",
                "description": "Indicates if special equipment is required.",
                "use_cases": ["Used for room allocation logic."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "is_emergency_service",
                "description": "Indicates if service is for emergencies.",
                "use_cases": ["Used to prioritize booking slots."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "is_active",
                "description": "Whether the service is active.",
                "use_cases": ["Used to hide discontinued services from the booking menu."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when service was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when service was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "appointments": {
        "table_name": "appointments",
        "description": "Central table for all dental appointments.",
        "columns": [
            {
                "name": "id",
                "description": "Unique appointment ID.",
                "use_cases": ["Used to identify and manage specific bookings."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "user_id",
                "description": "ID of the user the appointment is for.",
                "use_cases": ["Used to link the appointment to the patient's record."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "provider_id",
                "description": "ID of the provider performing the service.",
                "use_cases": ["Used to assign the appointment to a specific dentist/hygienist."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "service_id",
                "description": "ID of the service being provided.",
                "use_cases": ["Used to determine the duration and type of appointment."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "start_time",
                "description": "Appointment start time in UTC.",
                "use_cases": ["Used to reserve the time slot in the schedule."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "end_time",
                "description": "Appointment end time in UTC.",
                "use_cases": ["Used to determine when the provider becomes free again."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "timezone",
                "description": "Timezone used for displaying the appointment.",
                "use_cases": ["Used to show the correct time to the user/provider."],
                "cardinality": "low",
                "unique_values": ["America/Chicago"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "status",
                "description": "Current appointment status.",
                "use_cases": ["Used to track the lifecycle (e.g., scheduled, completed, cancelled)."],
                "cardinality": "low",
                "unique_values": ["scheduled", "confirmed", "cancelled", "completed", "no_show"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "is_recurring",
                "description": "Whether the appointment is part of a recurring series.",
                "use_cases": ["Used to handle series-level logic."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "parent_appointment_id",
                "description": "ID of the parent recurring appointment.",
                "use_cases": ["Used to group individual instances of a recurring series."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "notes",
                "description": "Appointment notes.",
                "use_cases": ["Used for internal communication about the appointment."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "chief_complaint",
                "description": "Patient's primary complaint.",
                "use_cases": ["Used to inform the provider of the reason for the visit."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "cancellation_reason",
                "description": "Explanation for appointment cancellation.",
                "use_cases": ["Used for analytics and patient history."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "cancelled_at",
                "description": "Timestamp of cancellation.",
                "use_cases": ["Used for auditing and history."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "cancelled_by",
                "description": "Who cancelled the appointment.",
                "use_cases": ["Used for auditing."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "confirmed_at",
                "description": "Timestamp when appointment was confirmed.",
                "use_cases": ["Used to verify appointment status."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "reminder_sent_at",
                "description": "Timestamp when reminder was sent.",
                "use_cases": ["Used to prevent duplicate reminders."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when appointment was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_by",
                "description": "Who created the appointment.",
                "use_cases": ["Used for auditing (e.g., user vs admin)."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when appointment was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "recurring_patterns": {
        "table_name": "recurring_patterns",
        "description": "Stores recurrence rules for recurring appointments.",
        "columns": [
            {
                "name": "id",
                "description": "Unique recurring pattern ID.",
                "use_cases": ["Used to identify the recurrence rule."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "appointment_id",
                "description": "ID of the associated appointment.",
                "use_cases": ["Used to link the pattern to the initial appointment."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "recurring_type",
                "description": "Type of recurrence (daily, weekly, etc.).",
                "use_cases": ["Used to calculate future appointment dates."],
                "cardinality": "low",
                "unique_values": ["daily", "weekly", "monthly", "yearly"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "separation_count",
                "description": "How many intervals between recurrences.",
                "use_cases": ["Used for patterns like 'every 2 weeks'."],
                "cardinality": "low",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "day_of_week",
                "description": "Day of week for weekly recurrence.",
                "use_cases": ["Used to anchor weekly appointments (e.g., every Monday)."],
                "cardinality": "low",
                "unique_values": [1, 2, 3, 4, 5, 6, 7],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "day_of_month",
                "description": "Day of month for monthly recurrence.",
                "use_cases": ["Used to anchor monthly appointments (e.g., 15th of the month)."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "week_of_month",
                "description": "Week index for monthly recurrence.",
                "use_cases": ["Used for patterns like '2nd Tuesday of the month'."],
                "cardinality": "low",
                "unique_values": [1, 2, 3, 4, 5],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "month_of_year",
                "description": "Month for yearly recurrence.",
                "use_cases": ["Used for annual appointments."],
                "cardinality": "low",
                "unique_values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "max_occurrences",
                "description": "Maximum number of recurrences.",
                "use_cases": ["Used to limit the series length."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "end_date",
                "description": "Date when recurrence ends.",
                "use_cases": ["Used to define the end of the series."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when pattern was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when pattern was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "appointment_exceptions": {
        "table_name": "appointment_exceptions",
        "description": "Handles modifications to individual instances of recurring appointments.",
        "columns": [
            {
                "name": "id",
                "description": "Unique exception ID.",
                "use_cases": ["Used to identify specific changes to a recurring series instance."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "parent_appointment_id",
                "description": "ID of the recurring appointment.",
                "use_cases": ["Used to link the exception to the main series."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "exception_date",
                "description": "Date the exception applies to.",
                "use_cases": ["Used to identify which instance in the series is modified."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "new_start_time",
                "description": "New start time if rescheduled.",
                "use_cases": ["Used to override the calculated series time."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "new_end_time",
                "description": "New end time if rescheduled.",
                "use_cases": ["Used to override the calculated series duration."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "is_cancelled",
                "description": "Whether the instance is cancelled.",
                "use_cases": ["Used to remove a specific instance from the schedule."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "is_rescheduled",
                "description": "Whether the instance is rescheduled.",
                "use_cases": ["Used to flag that this instance differs from the pattern."],
                "cardinality": "low",
                "unique_values": [True, False],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "reason",
                "description": "Reason for the exception.",
                "use_cases": ["Used for history and auditing."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when exception was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when exception was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "base_availability_rules": {
        "table_name": "base_availability_rules",
        "description": "Defines provider's base working hours per day of week.",
        "columns": [
            {
                "name": "id",
                "description": "Unique availability rule ID.",
                "use_cases": ["Used to identify a specific working hour rule."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "provider_id",
                "description": "ID of the provider.",
                "use_cases": ["Used to link the rule to a specific provider."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "day_of_week",
                "description": "Day the provider is available.",
                "use_cases": ["Used to define the weekly schedule (e.g., Mondays)."],
                "cardinality": "low",
                "unique_values": [1, 2, 3, 4, 5, 6, 7],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "start_time",
                "description": "Start of provider's working hours.",
                "use_cases": ["Used to determine when the provider starts taking appointments."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "end_time",
                "description": "End of provider's working hours.",
                "use_cases": ["Used to determine when the provider stops taking appointments."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "effective_from",
                "description": "Rule start date.",
                "use_cases": ["Used to handle schedule changes over time (e.g., summer hours)."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "effective_until",
                "description": "Rule end date.",
                "use_cases": ["Used to expire old schedule rules."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "timezone",
                "description": "Timezone for the rule.",
                "use_cases": ["Used to interpret the start/end times correctly."],
                "cardinality": "low",
                "unique_values": ["America/Chicago"],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "notes",
                "description": "Extra notes for the rule.",
                "use_cases": ["Used for administrative context."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when rule was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when rule was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "availability_exceptions": {
        "table_name": "availability_exceptions",
        "description": "Defines intervals where provider is unavailable within base working hours.",
        "columns": [
            {
                "name": "id",
                "description": "Unique availability exception ID.",
                "use_cases": ["Used to identify specific time off or extra hours."],
                "cardinality": "unique",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": False
            },
            {
                "name": "provider_id",
                "description": "ID of the provider.",
                "use_cases": ["Used to link the exception to the provider."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": True
            },
            {
                "name": "date",
                "description": "Date of unavailability.",
                "use_cases": ["Used to block off a specific day (e.g., holiday, sick day)."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "start_time",
                "description": "Start of unavailable period.",
                "use_cases": ["Used to define partial day off."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "end_time",
                "description": "End of unavailable period.",
                "use_cases": ["Used to define partial day off."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "reason",
                "description": "Reason for unavailability.",
                "use_cases": ["Used for administrative records (e.g., 'Vacation')."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "created_at",
                "description": "Timestamp when exception was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when exception was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    },
    "provider_services": {
        "table_name": "provider_services",
        "description": "Association object between ServiceProvider and Service.",
        "columns": [
            {
                "name": "provider_id",
                "description": "ID of the provider.",
                "use_cases": ["Used to link a provider to a service they can perform."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": True
            },
            {
                "name": "service_id",
                "description": "ID of the service.",
                "use_cases": ["Used to link a service to a provider."],
                "cardinality": "medium",
                "unique_values": [],
                "is_primary_key": True,
                "is_foreign_key": True
            },
            {
                "name": "created_at",
                "description": "Timestamp when relationship was created.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            },
            {
                "name": "updated_at",
                "description": "Timestamp when relationship was last updated.",
                "use_cases": ["Used for auditing."],
                "cardinality": "high",
                "unique_values": [],
                "is_primary_key": False,
                "is_foreign_key": False
            }
        ]
    }
}
