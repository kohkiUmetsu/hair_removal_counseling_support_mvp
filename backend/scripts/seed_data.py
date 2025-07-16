"""
Seed initial data for development
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.clinic import Clinic
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.session import Session as CounselingSession, SessionStatus
from datetime import datetime, timedelta
import uuid


def create_tables():
    """Create all tables"""
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)


def seed_clinics(db: Session) -> dict:
    """Seed clinic data"""
    clinics = [
        {
            "name": "美容クリニック東京",
            "address": "東京都渋谷区渋谷1-1-1",
            "phone": "03-1234-5678"
        },
        {
            "name": "ビューティークリニック大阪",
            "address": "大阪府大阪市中央区本町1-1-1",
            "phone": "06-1234-5678"
        }
    ]
    
    clinic_objects = {}
    for clinic_data in clinics:
        clinic = Clinic(**clinic_data)
        db.add(clinic)
        db.flush()  # Get the ID
        clinic_objects[clinic_data["name"]] = clinic
    
    return clinic_objects


def seed_users(db: Session, clinics: dict) -> dict:
    """Seed user data"""
    tokyo_clinic = clinics["美容クリニック東京"]
    osaka_clinic = clinics["ビューティークリニック大阪"]
    
    users = [
        {
            "email": "admin@clinic.example.com",
            "password": "admin123",
            "name": "システム管理者",
            "role": UserRole.ADMIN,
            "clinic_id": None
        },
        {
            "email": "manager.tokyo@clinic.example.com",
            "password": "manager123",
            "name": "東京店長",
            "role": UserRole.MANAGER,
            "clinic_id": tokyo_clinic.id
        },
        {
            "email": "manager.osaka@clinic.example.com",
            "password": "manager123",
            "name": "大阪店長",
            "role": UserRole.MANAGER,
            "clinic_id": osaka_clinic.id
        },
        {
            "email": "counselor1.tokyo@clinic.example.com",
            "password": "counselor123",
            "name": "田中花子",
            "role": UserRole.COUNSELOR,
            "clinic_id": tokyo_clinic.id
        },
        {
            "email": "counselor2.tokyo@clinic.example.com",
            "password": "counselor123",
            "name": "佐藤美咲",
            "role": UserRole.COUNSELOR,
            "clinic_id": tokyo_clinic.id
        },
        {
            "email": "counselor1.osaka@clinic.example.com",
            "password": "counselor123",
            "name": "山田優子",
            "role": UserRole.COUNSELOR,
            "clinic_id": osaka_clinic.id
        }
    ]
    
    user_objects = {}
    for user_data in users:
        password = user_data.pop("password")
        user = User(
            **user_data,
            password_hash=get_password_hash(password)
        )
        db.add(user)
        db.flush()
        user_objects[user_data["email"]] = user
    
    return user_objects


def seed_customers(db: Session, clinics: dict) -> dict:
    """Seed customer data"""
    tokyo_clinic = clinics["美容クリニック東京"]
    osaka_clinic = clinics["ビューティークリニック大阪"]
    
    customers = [
        {
            "name": "鈴木太郎",
            "phone": "090-1234-5678",
            "email": "suzuki@example.com",
            "clinic_id": tokyo_clinic.id
        },
        {
            "name": "高橋花子",
            "phone": "090-2345-6789",
            "email": "takahashi@example.com",
            "clinic_id": tokyo_clinic.id
        },
        {
            "name": "伊藤次郎",
            "phone": "090-3456-7890",
            "email": "itou@example.com",
            "clinic_id": tokyo_clinic.id
        },
        {
            "name": "渡辺美香",
            "phone": "090-4567-8901",
            "email": "watanabe@example.com",
            "clinic_id": osaka_clinic.id
        },
        {
            "name": "中村健一",
            "phone": "090-5678-9012",
            "email": "nakamura@example.com",
            "clinic_id": osaka_clinic.id
        }
    ]
    
    customer_objects = {}
    for customer_data in customers:
        customer = Customer(**customer_data)
        db.add(customer)
        db.flush()
        customer_objects[customer_data["name"]] = customer
    
    return customer_objects


def seed_sessions(db: Session, customers: dict, users: dict) -> None:
    """Seed session data"""
    # Get counselors
    counselors = [user for user in users.values() if user.role == UserRole.COUNSELOR]
    customer_list = list(customers.values())
    
    # Sample analysis results
    sample_analysis = {
        "overall_score": 7.5,
        "questioning": {
            "score": 8.0,
            "open_question_ratio": 0.7,
            "suggestions": ["より深掘りする質問を増やしましょう"]
        },
        "anxiety_handling": {
            "score": 7.0,
            "empathy_score": 8.0,
            "suggestions": ["不安に対する共感をもっと表現しましょう"]
        },
        "closing": {
            "score": 7.5,
            "timing_score": 8.0,
            "suggestions": ["クロージングのタイミングを見極めましょう"]
        },
        "flow": {
            "score": 8.0,
            "structure_score": 8.5,
            "suggestions": ["全体的な流れは良好です"]
        }
    }
    
    # Create sessions for the past 30 days
    for i in range(20):
        session_date = datetime.utcnow() - timedelta(days=i % 30)
        customer = customer_list[i % len(customer_list)]
        counselor = counselors[i % len(counselors)]
        
        session = CounselingSession(
            customer_id=customer.id,
            counselor_id=counselor.id,
            session_date=session_date,
            duration_minutes=30 + (i % 30),  # 30-59 minutes
            status=SessionStatus.COMPLETED if i < 15 else SessionStatus.RECORDED,
            audio_file_path=f"audio/{customer.clinic_id}/{customer.id}/{session_date.strftime('%Y%m%d')}/session_{uuid.uuid4()}.webm",
            transcription_text="カウンセラー: こんにちは、本日はご来店いただきありがとうございます。\n顧客: よろしくお願いします。" if i < 15 else None,
            analysis_result=sample_analysis if i < 15 else None,
            notes=f"カウンセリングセッション #{i+1}"
        )
        
        db.add(session)


def main():
    """Main seeding function"""
    print("Creating tables...")
    create_tables()
    
    print("Starting data seeding...")
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_clinics = db.query(Clinic).count()
        if existing_clinics > 0:
            print("Data already exists. Skipping seeding.")
            return
        
        print("Seeding clinics...")
        clinics = seed_clinics(db)
        
        print("Seeding users...")
        users = seed_users(db, clinics)
        
        print("Seeding customers...")
        customers = seed_customers(db, clinics)
        
        print("Seeding sessions...")
        seed_sessions(db, customers, users)
        
        db.commit()
        print("Data seeding completed successfully!")
        
        # Print login credentials
        print("\n=== Login Credentials ===")
        print("Admin: admin@clinic.example.com / admin123")
        print("Manager (Tokyo): manager.tokyo@clinic.example.com / manager123")
        print("Manager (Osaka): manager.osaka@clinic.example.com / manager123")
        print("Counselor (Tokyo): counselor1.tokyo@clinic.example.com / counselor123")
        print("Counselor (Tokyo): counselor2.tokyo@clinic.example.com / counselor123")
        print("Counselor (Osaka): counselor1.osaka@clinic.example.com / counselor123")
        
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()