
Act as:
Enterprise PostgreSQL 16 Architect, Healthcare Compliance (HIPAA/GDPR) Expert, Multi-Tenant SaaS Designer with deep experience in fintech-style settlement systems.

🎯 Goal
Design and generate a complete, production-ready PostgreSQL 16 schema for a multi-tenant healthcare platform (hospitals, clinics, labs, IVF centers, medical stores, blood banks, diagnostic centers) with:
Full multi-tenant RLS security
Online + offline (cash) payment handling
Settlement & reconciliation engine
Commission tracking (software/platform commission pending & realized)
Super admin onboarding of hospitals
Enterprise features: partitioning, audit trail, JSONB analytics, materialized views, advanced indexing, encryption.

🧩 Core Functional Modules
Multi-Tenant & Facilities
Tenants = facilities (hospital, clinic, lab, IVF, blood bank, diagnostic, medical store).
facilities table must include:
Facility type, MDR rates, platform commission, settlement rules
Status (active, onboarding, suspended)
Super admin can:
Onboard new facility (create facility + admin user)
Configure MDR & settlement rules (for online + cash collections)
View all facilities’ performance, commissions, and settlements.
Users & Roles
users with roles:
super_admin – global access
facility_admin – single facility/tenant
staff – scoped by facility and RBAC
patient – only own data
Use RLS with session variables:
app.current_tenant (UUID or facility_id)
app.user_id
Patients & Health Cards
Patients linked to users (optional).
Health card table with:
Card number, encrypted PIN (pgp_sym_encrypt)
JSONB medical history, allergies, chronic conditions, insurance etc.
Services, Staff & Appointments
Services per facility (partitioned by facility_id).
Facility staff (doctor, nurse, billing, lab tech).
Appointments partitioned by date (RANGE), including:
status, facility, patient, service, staff, notes.
Billing & Line Items
Editable bill master + bill items:
Subtotal, discount, tax, total, status.
Link to patient, appointment, facility.
Bills must support both:
Online payments (gateway)
Offline cash payments collected directly by hospital
Payments (Online)
payments table for PG transactions:
Razorpay/PayU/etc. transaction_id
Amount, MDR, platform_commission, net_settlement, status
Commission logic:
Example: Razorpay MDR 1.10% + GST
Platform MDR to hospital: 1.20% + GST
Margin (0.10%) = platform commission
Include trigger/function to auto-calc commission from facility configuration.
Cash Collections & Settlement (New Requirement)
Design separate module for cash payments where:
Patient pays cash directly to hospital.
System still creates cash collection records linked to bills.
Requirements:
When a patient pays cash at hospital:
Create entry: cash_collections (or offline_payments) with:
facility_id, bill_id, patient_id
amount_collected
collection_date/time
collected_by (staff)
settlement_status (pending, partially_settled, settled)
Commission logic on cash:
Per facility, configuration for:
Whether software/platform commission applies on cash bills (yes/no)
Commission type (percentage or fixed fee per bill)
System must calculate:
commission_amount for each cash collection
Maintain outstanding commission balance per facility.
Settlement ledger:
Create settlements or facility_settlements table:
facility_id
settlement_type (online_pg, cash_commission, mixed)
total_collections_amount
total_commission_amount
hospital_share
platform_share
settlement_period (from_date, to_date)
settlement_status (draft, pending, approved, paid)
paid_at, paid_by (super admin)
Support:
Partial and full settlements
Link to specific bills/cash collections (via junction table if needed).
Visibility:
Facility admin can see:
All their bills, online payments, cash collections
Their pending commission payable to software/platform
Settlement history
Super admin can see:
All facilities’ outstanding commissions
All settlement records
Overall platform-level revenue & commission dashboards.
Reconciliation & Reporting
Materialized views and/or views to show:
Per facility:
Total billed (online + cash)
Total collected online (PG)
Total cash collections
Commission earned by platform (online + cash)
Pending commission not yet settled
Per platform (super admin):
All facilities summary
Aging of pending commissions
Provide optimized queries for:
“Kitna commission pending” per facility
“Hospital ke paas kitna payment hold hai jo software ko dena hai”
“Last settlement se abhi tak ka pending difference”

🔐 Security, RLS & Compliance
Use RLS on all multi-tenant tables (facilities, patients, appointments, bills, payments, cash_collections, settlements, etc.).
Policies:
super_admin: bypass tenant filter (global)
facility_admin and staff: facility_id = current_setting('app.current_tenant')::int
patient: only own records (patient_id or user_id match)
Audit trail:
audit_log partitioned by time with triggers on all critical tables.
Column encryption with pgcrypto for:
health card PIN, Aadhaar hash or other sensitive identifiers.
Use SECURITY DEFINER functions for:
Setting session tenant/user (set_current_tenant, set_current_user)
Administrative tasks like onboarding facility, performing settlement approval.

⚙️ PostgreSQL Features & Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pg_partman";

Use:
HASH partitioning by tenant/facility when needed
RANGE partitioning by date for time-series (appointments, audit_log, settlements)
GIN indexes for JSONB
BRIN indexes for time-based & large tables.

📊 Analytics & Materialized Views
Materialized views for:
Facility daily revenue (online + cash)
Facility pending commission summary
Patient lifetime value
Category-wise revenue (hospital vs clinic vs lab, etc.)
Provide recommended refresh strategies (manual, cron-based, or on-demand).

🧪 Output Requirements
Full SQL DDL:
All tables, constraints, indexes, partitioning
ENUM types
RLS policies
Functions & triggers (audit, commission calculation, settlements)
Cash collection & settlement schema with:
Sample commission calculation trigger/function for cash
Views/materialized views for pending commission & settlement dashboards.
No explanation text, only PostgreSQL SQL code blocks.
At the end, add a short deployment checklist (in comments) for:
Setting app.current_tenant, app.user_id
Enabling RLS
Creating initial super admin & first facility.

🏗 FULL TECH STACK REQUIREMENT
Also generate recommended technology stack for full solution:

LayerTechnologyWhy Chosen
Frontend
Vite 5.4 + Vue 3.5 + Tailwind CSS 4.0
1.8s dev startup, 45KB bundle, 98/100 Lighthouse ​
State
Pinia 2.2
javascript + Vue 3 optimized
Backend
Flask 3.0 + Gunicorn
Lightweight Python API, 25ms response
Database
PostgreSQL 16 + RLS
Multi-tenant, JSONB health cards, partitioning ​
Auth
Flask-JWT-Extended 4.6
HttpOnly cookies, 4 role types (super_admin → patient)
Real-time
Flask-SocketIO 5.4 
Live slot booking, 50ms updates
Payments
Razorpay SDK 1.4
Cash/Card/UPI, auto MDR + commission calc ​
ORM
SQLAlchemy 2.0 + Alembic
Zero-downtime migrations


following is my file stuctures 

