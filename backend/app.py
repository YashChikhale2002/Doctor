from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text

# ---------------------------------
# Load env & basic config
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

# Allow React dev server
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})

raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    raw_url = "postgresql+psycopg2://app_user:secure123@localhost:5432/healthcare"

app.config["SQLALCHEMY_DATABASE_URI"] = raw_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")

print("RAW DATABASE_URL           ->", repr(os.getenv("DATABASE_URL")))
print("SQLALCHEMY_DATABASE_URI    ->", repr(app.config["SQLALCHEMY_DATABASE_URI"]))

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ---------------------------------
# Helper: direct PG connection (for raw SQL/RLS tests)
# ---------------------------------
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "healthcare"),
        user=os.getenv("DB_USER", "app_user"),
        password=os.getenv("DB_PASSWORD", "secure123"),
        port=os.getenv("DB_PORT", "5432"),
        cursor_factory=RealDictCursor,
    )


def set_rls_context(conn, tenant_id, user_id):
    """Set PostgreSQL RLS context (if functions exist)."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT app.set_current_tenant(%s)", (tenant_id,))
        cur.execute("SELECT app.set_current_user(%s)", (user_id,))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        cur.close()

# ---------------------------------
# Simple SQLAlchemy model (just to test ORM)
# ---------------------------------
class Facility(db.Model):
    __tablename__ = "facilities"
    __table_args__ = {"schema": "app"}

    id = db.Column(db.Uuid, primary_key=True)
    tenant_id = db.Column(db.Uuid, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    facility_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "facility_type": self.facility_type,
            "status": self.status,
        }

# ---------------------------------
# Basic test routes
# ---------------------------------
@app.route("/api/health")
def health():
    """Basic health check hitting PostgreSQL."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        row = cur.fetchone()
        version = row["version"] if isinstance(row, dict) else row[0]
        cur.close()
        conn.close()

        return jsonify(
            {
                "status": "healthy",
                "database": "PostgreSQL 16",
                "version": version,
                "time": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------------------------
# Auth routes (dummy)
# ---------------------------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    """Dummy login that always returns a token (replace later)."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    identity = {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "facility_id": None,
        "email": email,
        "role": "super_admin" if "admin" in email else "facility_admin",
    }
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token, "user": identity})

@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    """Return current JWT identity."""
    current = get_jwt_identity()
    return jsonify({"user": current})

# ---------------------------------
# Facilities routes
# ---------------------------------
@app.route("/api/facilities/orm", methods=["GET"])
@jwt_required()
def list_facilities_orm():
    """List facilities via SQLAlchemy ORM."""
    facilities = Facility.query.limit(50).all()
    return jsonify([f.to_dict() for f in facilities])

@app.route("/api/facilities/raw", methods=["GET"])
@jwt_required()
def list_facilities_raw():
    """List facilities via raw SQL (tests RLS + direct psycopg2)."""
    current = get_jwt_identity()
    conn = get_db()
    set_rls_context(conn, current["tenant_id"], current["user_id"])
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, tenant_id, name, facility_type, status
        FROM app.facilities
        ORDER BY name
        LIMIT 50;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# ---------------------------------
# Entry point
# ---------------------------------
if __name__ == "__main__":
    with app.app_context():
        # Ensure app schema exists for our model
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS app;"))
        db.session.commit()
        db.create_all()

    print("🚀 Flask backend starting on http://localhost:8000")
    app.run(debug=True, port=8000, host="0.0.0.0")
