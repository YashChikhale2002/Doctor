# =====================================================================
# HEALTHCARE PLATFORM API - React + Vite Frontend
# Pure REST API Backend with JWT Authentication
# =====================================================================

import os
import logging
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text, inspect

# Load environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================================
# IMPORT ROUTES
# =====================================================================

from routes.health_routes import health_bp


from models import db

# =====================================================================
# CREATE APPLICATION
# =====================================================================

def create_app(config_name='development'):
    """Create Flask API application"""
    
    app = Flask(__name__)
    
    # =====================================================================
    # CONFIGURATION
    # =====================================================================
    
    if config_name == 'production':
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL',
            'postgresql+psycopg2://app_user:secure123@localhost:5432/healthcare'
        )
    else:
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL',
            'postgresql+psycopg2://app_user:secure123@localhost:5432/healthcare'
        )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    
    # =====================================================================
    # INITIALIZE EXTENSIONS
    # =====================================================================
    
    db.init_app(app)
    jwt = JWTManager(app)
    
    # CORS configuration for React frontend
    CORS(app, resources={
        r"/*": { 
            "origins": [
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",   # Alternative React port
                "http://localhost:5174",   # Alternative Vite port
                os.environ.get('FRONTEND_URL', 'http://localhost:5173')
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    logger.info(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # =====================================================================
    # REGISTER API BLUEPRINTS
    # =====================================================================
    
    logger.info("📡 Registering API Blueprints...")
    app.register_blueprint(health_bp)

    
    # =====================================================================
    # ROOT ENDPOINT
    # =====================================================================
    
    @app.route('/')
    def index():
        """API root endpoint"""
        return jsonify({
            "message": "Healthcare Platform API",
            "version": "1.0.0",
            "status": "running",
            "documentation": "/api/docs",
            "endpoints": {
                "health": "/api/health",
                "auth": {
                    "login": "/api/auth/login",
                    "me": "/api/auth/me",
                    "refresh": "/api/auth/refresh"
                },
                "facilities": "/api/facilities",
                "patients": "/api/patients",
                "billing": "/api/billing",
                "analytics": "/api/analytics"
            }
        }), 200
    
    # =====================================================================
    # ERROR HANDLERS
    # =====================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found',
            'status': 404
        }), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status': 403
        }), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f"Internal error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'The request was invalid or malformed',
            'status': 400
        }), 400
    
    # =====================================================================
    # JWT ERROR HANDLERS
    # =====================================================================
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expired',
            'message': 'The authentication token has expired',
            'status': 401
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'The authentication token is invalid',
            'status': 401
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication token is missing',
            'status': 401
        }), 401
    
    # =====================================================================
    # REQUEST/RESPONSE MIDDLEWARE
    # =====================================================================
    
    @app.before_request
    def log_request():
        """Log all requests"""
        logger.info(f"{request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Add security headers"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app

# =====================================================================
# DATABASE MIGRATION
# =====================================================================

def migrate_database(app):
    """Initialize database with schemas and extensions"""
    with app.app_context():
        try:
            logger.info("🔧 Starting database migration...")
            
            # Create schemas
            logger.info("📁 Creating schemas...")
            schemas = ["app", "billing", "settlement", "audit", "analytics"]
            for schema in schemas:
                db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
            db.session.commit()
            logger.info("   ✅ Schemas created")
            
            # Create extensions
            logger.info("🔌 Installing extensions...")
            extensions = ["uuid-ossp", "pgcrypto", "pg_trgm", "btree_gin"]
            for ext in extensions:
                db.session.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}";'))
            db.session.commit()
            logger.info("   ✅ Extensions installed")
            
            # Create tables
            logger.info("📊 Creating tables from models...")
            db.create_all()
            logger.info("   ✅ All tables created")
            
            # Verify
            inspector = inspect(db.engine)
            for schema in ["app", "billing", "settlement"]:
                tables = inspector.get_table_names(schema=schema)
                logger.info(f"   📋 {schema} schema: {len(tables)} tables")
            
            logger.info("\n✅ Database migration completed!\n")
            return True
            
        except Exception as e:
            logger.error(f"\n❌ Migration failed: {str(e)}\n")
            db.session.rollback()
            return False

# =====================================================================
# CLI COMMANDS
# =====================================================================

def register_cli_commands(app):
    """Register Flask CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize database"""
        if migrate_database(app):
            logger.info("✅ Database initialized")
        else:
            logger.error("❌ Database initialization failed")
    
    @app.cli.command()
    def create_admin():
        """Create super admin user"""
        from models import User, Tenant, UserRole
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            try:
                # Get or create tenant
                tenant = Tenant.query.filter_by(code='DEFAULT').first()
                if not tenant:
                    tenant = Tenant(
                        code='DEFAULT',
                        name='Default Organization',
                        status='active'
                    )
                    db.session.add(tenant)
                    db.session.flush()
                
                # Check if admin exists
                if User.query.filter_by(email='admin@healthcare.com').first():
                    logger.warning("⚠️  Admin already exists")
                    return
                
                # Create admin
                admin = User(
                    tenant_id=tenant.id,
                    email='admin@healthcare.com',
                    password_hash=generate_password_hash('admin123'),
                    role=UserRole.SUPER_ADMIN,
                    is_active=True,
                    full_name='Super Administrator'
                )
                db.session.add(admin)
                db.session.commit()
                
                logger.info("✅ Admin created: admin@healthcare.com / admin123")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ Failed to create admin: {e}")

# =====================================================================
# CREATE APP INSTANCE
# =====================================================================

app = create_app(os.environ.get('FLASK_ENV', 'development'))
register_cli_commands(app)

# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║      🏥 HEALTHCARE PLATFORM API - REST API BACKEND          ║
    ║                                                               ║
    ║      Backend for React + Vite Frontend                       ║
    ║      JWT Authentication | Multi-tenant | PostgreSQL          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("📊 API FEATURES:")
    print("   ✅ RESTful API Design")
    print("   ✅ JWT Authentication")
    print("   ✅ Role-based Access Control")
    print("   ✅ Multi-tenant Support")
    print("   ✅ CORS Enabled for React")
    print("   ✅ PostgreSQL 16")
    print("   ✅ Comprehensive Logging")
    print()
    
    print("🔗 API ENDPOINTS:")
    print("   🌐 Base URL: http://localhost:8000")
    print("   📱 Health Check: http://localhost:8000/api/health")
    print("   🔐 Auth: http://localhost:8000/api/auth/login")
    print("   🏥 Facilities: http://localhost:8000/api/facilities")
    print("   👥 Patients: http://localhost:8000/api/patients")
    print("   💳 Billing: http://localhost:8000/api/billing")
    print("   📊 Analytics: http://localhost:8000/api/analytics")
    print()
    
    print("🎨 FRONTEND:")
    print("   React + Vite: http://localhost:5173")
    print("   (Run separately: npm run dev)")
    print()
    
    print("👤 DEFAULT CREDENTIALS:")
    print("   Email: admin@healthcare.com")
    print("   Password: admin123")
    print()
    
    print("💡 CLI COMMANDS:")
    print("   flask init-db       # Initialize database")
    print("   flask create-admin  # Create admin user")
    print()
    
    print("🚀 Starting API Server on http://localhost:8000")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=8000)
