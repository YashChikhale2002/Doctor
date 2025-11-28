"""
Complete SQLAlchemy models for Multi-Tenant Healthcare Platform
Matches PostgreSQL 16 schema with RLS, partitioning, enums, JSONB, and schemas
"""

from datetime import datetime
import uuid
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import (
    create_engine, Column, ForeignKey, Integer, BigInteger, String, Text, Boolean,
    DateTime, Date, Time, Numeric, Enum as SQLEnum, JSON, func, text, Index
)
from sqlalchemy.dialects.postgresql import UUID, BYTEA, ARRAY, CITEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import expression
from enum import Enum as PyEnum
import enum

Base = declarative_base()
db = None  # Will be initialized externally

# =====================================================================
# ENUMS (matching PostgreSQL enums)
# =====================================================================

class FacilityType(str, PyEnum):
    HOSPITAL = "hospital"
    CLINIC = "clinic"
    LAB = "lab"
    IVF_CENTER = "ivf_center"
    BLOOD_BANK = "blood_bank"
    DIAGNOSTIC_CENTER = "diagnostic_center"
    MEDICAL_STORE = "medical_store"

class UserRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    FACILITY_ADMIN = "facility_admin"
    STAFF = "staff"
    PATIENT = "patient"

class AppointmentStatus(str, PyEnum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class BillStatus(str, PyEnum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, PyEnum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"

class SettlementStatus(str, PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"

class SettlementType(str, PyEnum):
    ONLINE_PG = "online_pg"
    CASH_COMMISSION = "cash_commission"
    MIXED = "mixed"

class CommissionType(str, PyEnum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

class AuditAction(str, PyEnum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

# =====================================================================
# APP SCHEMA MODELS
# =====================================================================

class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), nullable=False, default="active")

    facilities = relationship("Facility", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="tenant")
    patients = relationship("Patient", back_populates="tenant")

class Facility(Base):
    __tablename__ = "facilities"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    facility_type = Column(SQLEnum(FacilityType), nullable=False)
    status = Column(String(20), nullable=False, default="onboarding")
    
    # Online payment MDR config
    pg_mdr_percent = Column(Numeric(6, 3), nullable=False, default=Decimal('0.000'))
    pg_mdr_gst_percent = Column(Numeric(6, 3), nullable=False, default=Decimal('0.000'))
    platform_mdr_percent = Column(Numeric(6, 3), nullable=False, default=Decimal('0.000'))
    platform_mdr_gst_percent = Column(Numeric(6, 3), nullable=False, default=Decimal('0.000'))
    
    # Cash commission config
    cash_commission_enabled = Column(Boolean, nullable=False, default=False)
    cash_commission_type = Column(SQLEnum(CommissionType), nullable=False, default=CommissionType.PERCENTAGE)
    cash_commission_rate = Column(Numeric(10, 4), nullable=False, default=Decimal('0.0000'))
    
    onboarded_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant = relationship("Tenant", back_populates="facilities")

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id"), nullable=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id"))
    email = Column(CITEXT, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant = relationship("Tenant")
    patients = relationship("Patient", back_populates="user")
    facility = relationship("Facility")

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id"))
    full_name = Column(String(255), nullable=False)
    gender = Column(String(20))
    dob = Column(Date)
    phone = Column(String(20))
    email = Column(CITEXT)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant = relationship("Tenant")
    user = relationship("User", back_populates="patients")
    facility = relationship("Facility")
    health_cards = relationship("HealthCard", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")

class HealthCard(Base):
    __tablename__ = "health_cards"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("app.patients.id"), nullable=False)
    card_number = Column(String(100), unique=True, nullable=False)
    pin_encrypted = Column(BYTEA, nullable=False)
    medical_profile = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="health_cards")

class Service(Base):
    __tablename__ = "services"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    base_price = Column(Numeric(12, 2), nullable=False, default=Decimal('0'))
    is_active = Column(Boolean, nullable=False, default=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Staff(Base):
    __tablename__ = "staff"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id"))
    full_name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    specialties = Column(ARRAY(String))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# =====================================================================
# BILLING SCHEMA MODELS
# =====================================================================

class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = {"schema": "billing"}

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    appointment_id = Column(BigInteger)
    appointment_date = Column(Date)
    bill_number = Column(String(100), unique=True, nullable=False)
    subtotal_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    discount_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    tax_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    total_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    status = Column(SQLEnum(BillStatus), nullable=False, default=BillStatus.DRAFT)
    currency = Column(String(3), nullable=False, default="INR")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="bill")
    cash_collections = relationship("CashCollection", back_populates="bill")

class BillItem(Base):
    __tablename__ = "bill_items"
    __table_args__ = {"schema": "billing"}

    id = Column(BigInteger, primary_key=True)
    bill_id = Column(BigInteger, ForeignKey("billing.bills.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True))
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False, default=Decimal('1'))
    unit_price = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    line_total = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    metadata = Column(JSON, default=dict)

    bill = relationship("Bill", back_populates="items")

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "billing"}

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    bill_id = Column(BigInteger, ForeignKey("billing.bills.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    gateway = Column(String(50), nullable=False)
    gateway_transaction_id = Column(String(200), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(SQLEnum(PaymentStatus), nullable=False)
    
    # MDR & Commission fields
    mdr_percent = Column(Numeric(6, 3), nullable=False)
    mdr_amount = Column(Numeric(14, 2), nullable=False)
    mdr_gst_percent = Column(Numeric(6, 3), nullable=False)
    mdr_gst_amount = Column(Numeric(14, 2), nullable=False)
    platform_mdr_percent = Column(Numeric(6, 3), nullable=False)
    platform_mdr_amount = Column(Numeric(14, 2), nullable=False)
    platform_mdr_gst_percent = Column(Numeric(6, 3), nullable=False)
    platform_mdr_gst_amount = Column(Numeric(14, 2), nullable=False)
    platform_commission_amount = Column(Numeric(14, 2), nullable=False)
    net_settlement_to_facility = Column(Numeric(14, 2), nullable=False)
    
    settled_in_settlement_id = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    bill = relationship("Bill", back_populates="payments")

class CashCollection(Base):
    __tablename__ = "cash_collections"
    __table_args__ = {"schema": "billing"}

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    bill_id = Column(BigInteger, ForeignKey("billing.bills.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    collected_by_user_id = Column(UUID(as_uuid=True))
    amount_collected = Column(Numeric(14, 2), nullable=False)
    collection_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    commission_applicable = Column(Boolean, nullable=False, default=True)
    commission_type = Column(SQLEnum(CommissionType), nullable=False)
    commission_rate = Column(Numeric(10, 4), nullable=False)
    commission_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    settlement_status = Column(SQLEnum(SettlementStatus), nullable=False, default=SettlementStatus.PENDING)
    settled_in_settlement_id = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    bill = relationship("Bill", back_populates="cash_collections")

# =====================================================================
# SETTLEMENT SCHEMA MODELS
# =====================================================================

class FacilitySettlement(Base):
    __tablename__ = "facility_settlements"
    __table_args__ = {"schema": "settlement"}

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    settlement_type = Column(SQLEnum(SettlementType), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    total_collections_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    total_commission_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    hospital_share_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    platform_share_amount = Column(Numeric(14, 2), nullable=False, default=Decimal('0'))
    settlement_status = Column(SQLEnum(SettlementStatus), nullable=False, default=SettlementStatus.DRAFT)
    created_by_user_id = Column(UUID(as_uuid=True))
    approved_by_user_id = Column(UUID(as_uuid=True))
    paid_by_user_id = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class SettlementPayment(Base):
    __tablename__ = "settlement_payments"
    __table_args__ = {"schema": "settlement"}

    settlement_id = Column(BigInteger, ForeignKey("settlement.facility_settlements.id"), primary_key=True)
    payment_id = Column(BigInteger, ForeignKey("billing.payments.id"), primary_key=True)

class SettlementCashCollection(Base):
    __tablename__ = "settlement_cash_collections"
    __table_args__ = {"schema": "settlement"}

    settlement_id = Column(BigInteger, ForeignKey("settlement.facility_settlements.id"), primary_key=True)
    cash_collection_id = Column(BigInteger, ForeignKey("billing.cash_collections.id"), primary_key=True)

# =====================================================================
# AUDIT SCHEMA MODELS (partitioned tables need special handling)
# =====================================================================

class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit"}

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True))
    facility_id = Column(UUID(as_uuid=True))
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(200), nullable=False)
    action = Column(SQLEnum(AuditAction), nullable=False)
    old_data = Column(JSON)
    new_data = Column(JSON)
    performed_by = Column(UUID(as_uuid=True))
    performed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# =====================================================================
# UTILITY FUNCTIONS (to match PostgreSQL functions)
# =====================================================================

def set_session_context(tenant_id: str, user_id: str):
    """Call these in Flask middleware after authentication"""
    from sqlalchemy import text
    return text(f"""
        SELECT app.set_current_tenant('{tenant_id}');
        SELECT app.set_current_user('{user_id}');
    """)

# =====================================================================
# USAGE IN FLASK APP
# =====================================================================
