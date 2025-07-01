"""
Database management for Astra voice assistant.
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import settings
from .logging import get_logger
from .security import security_manager


Base = declarative_base()


class User(Base):
    """User model for authentication and management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    settings = Column(Text)  # JSON string for user preferences


class Session(Base):
    """User session model."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_token = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)


class AuditLog(Base):
    """Audit log model for enterprise edition."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String(100))
    resource = Column(String(255))
    details = Column(Text)  # JSON string for additional details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Manages database operations for Astra."""
    
    def __init__(self):
        self.logger = get_logger("database")
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection."""
        try:
            # Create database URL with encryption
            if settings.database_encryption_key:
                # Use SQLCipher for encryption
                database_url = f"sqlite:///{settings.data_dir}/astra.db"
                self.engine = create_engine(
                    database_url,
                    connect_args={
                        "check_same_thread": False,
                        "pragmas": {
                            "key": settings.database_encryption_key,
                            "cipher": "aes256",
                        }
                    },
                    poolclass=StaticPool,
                )
            else:
                # Use regular SQLite
                database_url = f"sqlite:///{settings.data_dir}/astra.db"
                self.engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error("Database initialization failed", error=str(e))
            raise
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def create_user(self, username: str, email: str, password: str, role: str = "user") -> User:
        """Create a new user."""
        try:
            with self.get_session() as session:
                # Check if user already exists
                existing_user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    raise ValueError("User already exists")
                
                # Create new user
                hashed_password = security_manager.hash_password(password)
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    role=role,
                    settings=json.dumps({})
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                self.logger.info("User created successfully", username=username)
                return user
                
        except Exception as e:
            self.logger.error("User creation failed", error=str(e))
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                
                if user and security_manager.verify_password(password, user.hashed_password):
                    # Update last login
                    user.last_login = datetime.utcnow()
                    session.commit()
                    
                    self.logger.info("User authenticated successfully", username=username)
                    return user
                
                return None
                
        except Exception as e:
            self.logger.error("User authentication failed", error=str(e))
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            with self.get_session() as session:
                return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            self.logger.error("Failed to get user by ID", error=str(e))
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            with self.get_session() as session:
                return session.query(User).filter(User.username == username).first()
        except Exception as e:
            self.logger.error("Failed to get user by username", error=str(e))
            return None
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Update user settings."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.settings = json.dumps(settings)
                    session.commit()
                    return True
                return False
        except Exception as e:
            self.logger.error("Failed to update user settings", error=str(e))
            return False
    
    def create_session(self, user_id: int, session_token: str, expires_at: datetime) -> bool:
        """Create user session."""
        try:
            with self.get_session() as session:
                # Deactivate existing sessions for user
                session.query(Session).filter(
                    Session.user_id == user_id,
                    Session.is_active == True
                ).update({"is_active": False})
                
                # Create new session
                new_session = Session(
                    user_id=user_id,
                    session_token=session_token,
                    expires_at=expires_at
                )
                
                session.add(new_session)
                session.commit()
                return True
                
        except Exception as e:
            self.logger.error("Failed to create session", error=str(e))
            return False
    
    def validate_session(self, session_token: str) -> Optional[Session]:
        """Validate session token."""
        try:
            with self.get_session() as session:
                db_session = session.query(Session).filter(
                    Session.session_token == session_token,
                    Session.is_active == True,
                    Session.expires_at > datetime.utcnow()
                ).first()
                
                return db_session
                
        except Exception as e:
            self.logger.error("Failed to validate session", error=str(e))
            return None
    
    def log_audit_event(self, user_id: int, action: str, resource: str, 
                       details: Dict[str, Any] = None, ip_address: str = None,
                       user_agent: str = None) -> bool:
        """Log audit event (Enterprise only)."""
        if not settings.is_enterprise:
            return True
        
        try:
            with self.get_session() as session:
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource=resource,
                    details=json.dumps(details) if details else None,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                session.add(audit_log)
                session.commit()
                return True
                
        except Exception as e:
            self.logger.error("Failed to log audit event", error=str(e))
            return False
    
    def get_audit_logs(self, user_id: Optional[int] = None, 
                      action: Optional[str] = None,
                      limit: int = 100) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        if not settings.is_enterprise:
            return []
        
        try:
            with self.get_session() as session:
                query = session.query(AuditLog)
                
                if user_id:
                    query = query.filter(AuditLog.user_id == user_id)
                
                if action:
                    query = query.filter(AuditLog.action == action)
                
                return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
                
        except Exception as e:
            self.logger.error("Failed to get audit logs", error=str(e))
            return []
    
    def backup_database(self, backup_path: Path) -> bool:
        """Create database backup."""
        try:
            import shutil
            source_db = settings.data_dir / "astra.db"
            shutil.copy2(source_db, backup_path)
            
            self.logger.info("Database backup created", backup_path=str(backup_path))
            return True
            
        except Exception as e:
            self.logger.error("Database backup failed", error=str(e))
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """Restore database from backup."""
        try:
            import shutil
            target_db = settings.data_dir / "astra.db"
            shutil.copy2(backup_path, target_db)
            
            self.logger.info("Database restored from backup", backup_path=str(backup_path))
            return True
            
        except Exception as e:
            self.logger.error("Database restore failed", error=str(e))
            return False


# Global database manager instance
database_manager = DatabaseManager() 