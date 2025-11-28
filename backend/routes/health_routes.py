"""
Health check routes - Test if API structure works
GET /api/health - Basic health check
GET /api/stats - Database statistics
"""

from flask import Blueprint, jsonify
from datetime import datetime
from sqlalchemy import text, inspect
from models import db
import logging

logger = logging.getLogger(__name__)

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health')
def health():
    """Basic health check"""
    try:
        # Test database connection
        result = db.session.execute(text("SELECT version();"))
        version = result.scalar()
        
        # Get schema info
        inspector = inspect(db.engine)
        schemas = inspector.get_schema_names()
        
        return jsonify({
            "status": "healthy",
            "message": "Healthcare API is running!",
            "database": {
                "connected": True,
                "version": version,
                "schemas": schemas
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "message": "Database connection failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@health_bp.route('/stats')
def stats():
    """Get database statistics"""
    try:
        def get_count(schema, table):
            """Helper to get table count"""
            try:
                result = db.session.execute(
                    text(f"SELECT COUNT(*) FROM {schema}.{table}")
                )
                return result.scalar()
            except:
                return 0
        
        stats_data = {
            "app_schema": {
                "tenants": get_count("app", "tenants"),
                "facilities": get_count("app", "facilities"),
                "users": get_count("app", "users"),
                "patients": get_count("app", "patients"),
                "services": get_count("app", "services"),
                "staff": get_count("app", "staff"),
            },
            "billing_schema": {
                "bills": get_count("billing", "bills"),
                "payments": get_count("billing", "payments"),
                "cash_collections": get_count("billing", "cash_collections"),
            },
            "settlement_schema": {
                "settlements": get_count("settlement", "facility_settlements"),
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        return jsonify({
            "error": "Failed to get statistics",
            "message": str(e)
        }), 500

@health_bp.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({
        "status": "pong",
        "timestamp": datetime.now().isoformat()
    }), 200
