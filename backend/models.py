"""
Complete Advanced SQLAlchemy Models for Multi-Tenant Healthcare Platform
PostgreSQL 16 + RLS + Partitioning + JSONB + Encryption
"""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Dict, Any, List
import uuid
from sqlalchemy import (
    Column, ForeignKey, String, Text, Boolean, DateTime, Date, Time,
    Numeric, BigInteger, Integer, Index, UniqueConstraint, CheckConstraint,
    func, text
)
from sqlalchemy.dialects.postgresql import UUID, BYTEA, ARRAY, JSONB, ENUM
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()
Base = declarative_base()

# =====================================================================
# PYTHON ENUMS (matching PostgreSQL ENUMs)
# =====================================================================

class FacilityType(str, enum.Enum):
    HOSPITAL = "hospital"
    CLINIC = "clinic"
    LAB = "lab"
    IVF_CENTER = "ivf_center"
    BLOOD_BANK = "blood_bank"
    DIAGNOSTIC_CENTER = "diagnostic_center"
    MEDICAL_STORE = "medical_store"

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    FACILITY_ADMIN = "facility_admin"
    STAFF = "staff"
    PATIENT = "patient"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class BillStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"

class SettlementStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"

class SettlementType(str, enum.Enum):
    ONLINE_PG = "online_pg"
    CASH_COMMISSION = "cash_commission"
    MIXED = "mixed"

class CommissionType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

class AuditAction(str, enum.Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

# =====================================================================
# BASE MIXINS
# =====================================================================

class TimestampMixin:
    """Add created_at and updated_at columns"""
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

class UUIDPrimaryKey:
    """UUID primary key with auto-generation"""
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())

class TenantMixin:
    """Multi-tenant columns"""
    @declared_attr
    def tenant_id(cls):
        return Column(UUID(as_uuid=True), nullable=False, index=True)
    
    @declared_attr
    def facility_id(cls):
        return Column(UUID(as_uuid=True), nullable=False, index=True)

# =====================================================================
# APP SCHEMA MODELS
# =====================================================================

class Tenant(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "app"}

    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="active", index=True)

    # Relationships
    facilities = relationship("Facility", back_populates="tenant", cascade="all, delete-orphan", lazy="dynamic")
    users = relationship("User", back_populates="tenant", lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Facility(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "facilities"
    __table_args__ = (
        Index("idx_facilities_tenant_type", "tenant_id", "facility_type"),
        Index("idx_facilities_status", "status"),
        {"schema": "app"}
    )

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    facility_type = Column(ENUM(FacilityType, name="facility_type_enum", schema="app"), nullable=False)
    status = Column(String(20), nullable=False, default="onboarding")
    
    # Online payment MDR config
    pg_mdr_percent = Column(Numeric(6, 3), nullable=False, default=Decimal("0.000"))
    pg_mdr_gst_percent = Column(Numeric(6, 3), nullable=False, default=Decimal("0.000"))
    platform_mdr_percent = Column(Numeric(6, 3), nullable=False, default=Decimal("0.000"))
    platform_mdr_gst_percent = Column(Numeric(6, 3), nullable=False, default=Decimal("0.000"))
    
    # Cash commission config
    cash_commission_enabled = Column(Boolean, nullable=False, default=False)
    cash_commission_type = Column(ENUM(CommissionType, name="commission_type_enum", schema="app"), nullable=False, default=CommissionType.PERCENTAGE)
    cash_commission_rate = Column(Numeric(10, 4), nullable=False, default=Decimal("0.0000"))
    
    onboarded_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True))
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    tenant = relationship("Tenant", back_populates="facilities")
    users = relationship("User", back_populates="facility", lazy="dynamic")
    patients = relationship("Patient", back_populates="facility", lazy="dynamic")
    services = relationship("Service", back_populates="facility", lazy="dynamic")
    staff = relationship("Staff", back_populates="facility", lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "facility_type": self.facility_type.value,
            "status": self.status,
            "pg_mdr_percent": float(self.pg_mdr_percent),
            "pg_mdr_gst_percent": float(self.pg_mdr_gst_percent),
            "platform_mdr_percent": float(self.platform_mdr_percent),
            "platform_mdr_gst_percent": float(self.platform_mdr_gst_percent),
            "cash_commission_enabled": self.cash_commission_enabled,
            "cash_commission_type": self.cash_commission_type.value,
            "cash_commission_rate": float(self.cash_commission_rate),
            "onboarded_at": self.onboarded_at.isoformat() if self.onboarded_at else None,
        }

class User(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_users_role", "role"),
        {"schema": "app"}
    )

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id", ondelete="CASCADE"), nullable=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id", ondelete="SET NULL"))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(ENUM(UserRole, name="user_role_enum", schema="app"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    full_name = Column(String(255))
    phone = Column(String(20))
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    facility = relationship("Facility", back_populates="users")
    patients = relationship("Patient", back_populates="user", lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "facility_id": str(self.facility_id) if self.facility_id else None,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "full_name": self.full_name,
            "phone": self.phone,
        }

class Patient(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "patients"
    __table_args__ = (
        Index("idx_patients_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_patients_user", "user_id"),
        {"schema": "app"}
    )

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="SET NULL"))
    
    full_name = Column(String(255), nullable=False)
    gender = Column(String(20))
    dob = Column(Date)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    emergency_contact = Column(String(255))
    blood_group = Column(String(5))
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    facility = relationship("Facility", back_populates="patients")
    user = relationship("User", back_populates="patients")
    health_cards = relationship("HealthCard", back_populates="patient", lazy="dynamic")
    bills = relationship("Bill", back_populates="patient", lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "facility_id": str(self.facility_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "full_name": self.full_name,
            "gender": self.gender,
            "dob": self.dob.isoformat() if self.dob else None,
            "phone": self.phone,
            "email": self.email,
            "blood_group": self.blood_group,
        }

class HealthCard(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "health_cards"
    __table_args__ = (
        Index("idx_health_cards_patient", "patient_id"),
        Index("idx_health_cards_profile_gin", "medical_profile", postgresql_using="gin"),
        {"schema": "app"}
    )

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("app.patients.id", ondelete="CASCADE"), nullable=False)
    
    card_number = Column(String(100), unique=True, nullable=False, index=True)
    pin_encrypted = Column(BYTEA, nullable=False)
    medical_profile = Column(JSONB, nullable=False, default=dict)

    # Relationships
    patient = relationship("Patient", back_populates="health_cards")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id),
            "card_number": self.card_number,
            "medical_profile": self.medical_profile,
        }

class Service(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "services"
    __table_args__ = (
        Index("idx_services_tenant_facility", "tenant_id", "facility_id"),
        UniqueConstraint("facility_id", "code", name="uq_service_facility_code"),
        {"schema": "app"}
    )

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id", ondelete="CASCADE"), nullable=False)
    
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    base_price = Column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    facility = relationship("Facility", back_populates="services")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "base_price": float(self.base_price),
            "is_active": self.is_active,
        }

class Staff(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "staff"
    __table_args__ = (
        Index("idx_staff_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_staff_role", "role"),
        {"schema": "app"}
    )

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("app.tenants.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("app.facilities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="SET NULL"))
    
    full_name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    specialties = Column(ARRAY(String))
    qualification = Column(String(255))
    license_number = Column(String(100))
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    facility = relationship("Facility", back_populates="staff")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "role": self.role,
            "specialties": self.specialties,
            "is_active": self.is_active,
        }

# =====================================================================
# BILLING SCHEMA MODELS
# =====================================================================

class Bill(Base, TimestampMixin):
    __tablename__ = "bills"
    __table_args__ = (
        Index("idx_bills_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_bills_patient", "patient_id"),
        Index("idx_bills_status", "status"),
        {"schema": "billing"}
    )

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("app.patients.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(BigInteger)
    appointment_date = Column(Date)
    
    bill_number = Column(String(100), unique=True, nullable=False, index=True)
    subtotal_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    discount_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    tax_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    total_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    status = Column(ENUM(BillStatus, name="bill_status_enum", schema="app"), nullable=False, default=BillStatus.DRAFT)
    currency = Column(String(3), nullable=False, default="INR")
    
    notes = Column(Text)
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    patient = relationship("Patient", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan", lazy="dynamic")
    payments = relationship("Payment", back_populates="bill", lazy="dynamic")
    cash_collections = relationship("CashCollection", back_populates="bill", lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bill_number": self.bill_number,
            "patient_id": str(self.patient_id),
            "subtotal_amount": float(self.subtotal_amount),
            "discount_amount": float(self.discount_amount),
            "tax_amount": float(self.tax_amount),
            "total_amount": float(self.total_amount),
            "status": self.status.value,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class BillItem(Base):
    __tablename__ = "bill_items"
    __table_args__ = (
        Index("idx_bill_items_bill", "bill_id"),
        {"schema": "billing"}
    )

    id = Column(BigInteger, primary_key=True)
    bill_id = Column(BigInteger, ForeignKey("billing.bills.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(UUID(as_uuid=True))
    
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False, default=Decimal("1"))
    unit_price = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    line_total = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    bill = relationship("Bill", back_populates="items")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "quantity": float(self.quantity),
            "unit_price": float(self.unit_price),
            "line_total": float(self.line_total),
        }

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (
        Index("idx_payments_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_payments_bill", "bill_id"),
        Index("idx_payments_status", "status"),
        UniqueConstraint("gateway", "gateway_transaction_id", name="uq_payment_gateway_txn"),
        {"schema": "billing"}
    )

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    bill_id = Column(BigInteger, ForeignKey("billing.bills.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    
    gateway = Column(String(50), nullable=False)
    gateway_transaction_id = Column(String(200), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(ENUM(PaymentStatus, name="payment_status_enum", schema="app"), nullable=False)
    
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
    payment_method = Column(String(50))
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    bill = relationship("Bill", back_populates="payments")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "gateway": self.gateway,
            "gateway_transaction_id": self.gateway_transaction_id,
            "amount": float(self.amount),
            "status": self.status.value,
            "platform_commission_amount": float(self.platform_commission_amount),
            "net_settlement_to_facility": float(self.net_settlement_to_facility),
        }

class CashCollection(Base, TimestampMixin):
    __tablename__ = "cash_collections"
    __table_args__ = (
        Index("idx_cash_collections_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_cash_collections_bill", "bill_id"),
        Index("idx_cash_collections_status", "settlement_status"),
        {"schema": "billing"}
    )

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    bill_id = Column(BigInteger, ForeignKey("billing.bills.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    collected_by_user_id = Column(UUID(as_uuid=True))
    
    amount_collected = Column(Numeric(14, 2), nullable=False)
    collection_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    commission_applicable = Column(Boolean, nullable=False, default=True)
    commission_type = Column(ENUM(CommissionType, name="commission_type_enum", schema="app"), nullable=False)
    commission_rate = Column(Numeric(10, 4), nullable=False)
    commission_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    
    settlement_status = Column(ENUM(SettlementStatus, name="settlement_status_enum", schema="app"), nullable=False, default=SettlementStatus.PENDING)
    settled_in_settlement_id = Column(BigInteger)
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    # Relationships
    bill = relationship("Bill", back_populates="cash_collections")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "amount_collected": float(self.amount_collected),
            "commission_amount": float(self.commission_amount),
            "settlement_status": self.settlement_status.value,
            "collection_timestamp": self.collection_timestamp.isoformat() if self.collection_timestamp else None,
        }

# =====================================================================
# SETTLEMENT SCHEMA MODELS
# =====================================================================

class FacilitySettlement(Base, TimestampMixin):
    __tablename__ = "facility_settlements"
    __table_args__ = (
        Index("idx_settlements_tenant_facility", "tenant_id", "facility_id"),
        Index("idx_settlements_status", "settlement_status"),
        Index("idx_settlements_dates", "from_date", "to_date"),
        {"schema": "settlement"}
    )

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    facility_id = Column(UUID(as_uuid=True), nullable=False)
    
    settlement_type = Column(ENUM(SettlementType, name="settlement_type_enum", schema="app"), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    
    total_collections_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    total_commission_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    hospital_share_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    platform_share_amount = Column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    
    settlement_status = Column(ENUM(SettlementStatus, name="settlement_status_enum", schema="app"), nullable=False, default=SettlementStatus.DRAFT)
    
    created_by_user_id = Column(UUID(as_uuid=True))
    approved_by_user_id = Column(UUID(as_uuid=True))
    paid_by_user_id = Column(UUID(as_uuid=True))
    
    approved_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    
    notes = Column(Text)
    extra_data = Column(JSONB, default=dict)  # ✅ RENAMED from metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "facility_id": str(self.facility_id),
            "settlement_type": self.settlement_type.value,
            "from_date": self.from_date.isoformat() if self.from_date else None,
            "to_date": self.to_date.isoformat() if self.to_date else None,
            "total_collections_amount": float(self.total_collections_amount),
            "total_commission_amount": float(self.total_commission_amount),
            "hospital_share_amount": float(self.hospital_share_amount),
            "platform_share_amount": float(self.platform_share_amount),
            "settlement_status": self.settlement_status.value,
        }

class SettlementPayment(Base):
    __tablename__ = "settlement_payments"
    __table_args__ = {"schema": "settlement"}

    settlement_id = Column(BigInteger, ForeignKey("settlement.facility_settlements.id", ondelete="CASCADE"), primary_key=True)
    payment_id = Column(BigInteger, ForeignKey("billing.payments.id", ondelete="CASCADE"), primary_key=True)

class SettlementCashCollection(Base):
    __tablename__ = "settlement_cash_collections"
    __table_args__ = {"schema": "settlement"}

    settlement_id = Column(BigInteger, ForeignKey("settlement.facility_settlements.id", ondelete="CASCADE"), primary_key=True)
    cash_collection_id = Column(BigInteger, ForeignKey("billing.cash_collections.id", ondelete="CASCADE"), primary_key=True)

# =====================================================================
# AUDIT SCHEMA MODELS
# =====================================================================

class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("idx_audit_log_table", "table_name"),
        Index("idx_audit_log_tenant", "tenant_id", "facility_id"),
        {"schema": "audit"}
    )

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True))
    facility_id = Column(UUID(as_uuid=True))
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(200), nullable=False)
    action = Column(ENUM(AuditAction, name="audit_action_enum", schema="app"), nullable=False)
    old_data = Column(JSONB)
    new_data = Column(JSONB)
    performed_by = Column(UUID(as_uuid=True))
    performed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS app;"))
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS billing;"))
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS settlement;"))
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS audit;"))
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS analytics;"))
        
        db.session.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        db.session.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
        db.session.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm";'))
        
        db.session.commit()
        db.create_all()
