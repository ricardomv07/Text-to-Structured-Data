"""
Database module for storing extracted data
Uses PostgreSQL (Neon/Supabase) via SQLAlchemy
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup
Base = declarative_base()
engine = None
SessionLocal = None

class ExtractedData(Base):
    """Model for storing extracted document data"""
    __tablename__ = "extracted_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(255), nullable=False, index=True)
    monto = Column(Float, nullable=True)
    fecha = Column(String(50), nullable=True)
    tipo_solicitud = Column(String(100), nullable=True, index=True)
    raw_text = Column(Text, nullable=True)
    filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "cliente": self.cliente,
            "monto": self.monto,
            "fecha": self.fecha,
            "tipo_solicitud": self.tipo_solicitud,
            "filename": self.filename,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


def init_database():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not configured. Database features will be disabled.")
        return False
    
    try:
        # Fix for Neon/Render PostgreSQL URLs (postgres:// to postgresql://)
        db_url = DATABASE_URL.replace("postgres://", "postgresql://")
        
        engine = create_engine(db_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False


def get_db():
    """Get database session"""
    if SessionLocal is None:
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_extracted_data(cliente: str, monto: float, fecha: str, tipo_solicitud: str, 
                       raw_text: str = None, filename: str = None):
    """
    Save extracted data to database
    
    Args:
        cliente: Client name
        monto: Amount
        fecha: Date in DD/MM/YYYY format
        tipo_solicitud: Request type
        raw_text: Original text (optional)
        filename: Source filename (optional)
    
    Returns:
        dict: Saved record with ID or None if database not configured
    """
    if SessionLocal is None:
        logger.warning("Database not configured, skipping save")
        return None
    
    try:
        db = SessionLocal()
        
        # Create new record
        new_record = ExtractedData(
            cliente=cliente,
            monto=monto,
            fecha=fecha,
            tipo_solicitud=tipo_solicitud,
            raw_text=raw_text[:1000] if raw_text else None,  # Limit text length
            filename=filename
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        result = new_record.to_dict()
        logger.info(f"Saved record to database with ID: {result['id']}")
        
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        return None


def get_all_records(limit: int = 100, offset: int = 0):
    """
    Get all records from database
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
    
    Returns:
        list: List of records
    """
    if SessionLocal is None:
        return []
    
    try:
        db = SessionLocal()
        records = db.query(ExtractedData)\
                   .order_by(ExtractedData.created_at.desc())\
                   .limit(limit)\
                   .offset(offset)\
                   .all()
        
        result = [record.to_dict() for record in records]
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Error fetching records: {str(e)}")
        return []


def get_records_by_client(cliente: str):
    """
    Get records filtered by client name
    
    Args:
        cliente: Client name to search for
    
    Returns:
        list: List of matching records
    """
    if SessionLocal is None:
        return []
    
    try:
        db = SessionLocal()
        records = db.query(ExtractedData)\
                   .filter(ExtractedData.cliente.ilike(f"%{cliente}%"))\
                   .order_by(ExtractedData.created_at.desc())\
                   .all()
        
        result = [record.to_dict() for record in records]
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Error searching records: {str(e)}")
        return []


def get_records_by_type(tipo_solicitud: str):
    """
    Get records filtered by request type
    
    Args:
        tipo_solicitud: Request type to filter by
    
    Returns:
        list: List of matching records
    """
    if SessionLocal is None:
        return []
    
    try:
        db = SessionLocal()
        records = db.query(ExtractedData)\
                   .filter(ExtractedData.tipo_solicitud.ilike(f"%{tipo_solicitud}%"))\
                   .order_by(ExtractedData.created_at.desc())\
                   .all()
        
        result = [record.to_dict() for record in records]
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Error searching records: {str(e)}")
        return []


def get_database_stats():
    """
    Get database statistics
    
    Returns:
        dict: Statistics about stored data
    """
    if SessionLocal is None:
        return {"status": "not_configured"}
    
    try:
        db = SessionLocal()
        
        total_records = db.query(ExtractedData).count()
        
        # Count by type
        from sqlalchemy import func
        by_type = db.query(
            ExtractedData.tipo_solicitud,
            func.count(ExtractedData.id)
        ).group_by(ExtractedData.tipo_solicitud).all()
        
        # Total amount
        total_amount = db.query(func.sum(ExtractedData.monto)).scalar() or 0
        
        db.close()
        
        return {
            "status": "active",
            "total_records": total_records,
            "total_amount": float(total_amount),
            "by_type": {tipo: count for tipo, count in by_type if tipo}
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"status": "error", "message": str(e)}
