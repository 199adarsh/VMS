"""
Migration script to populate Firebase with existing VMS data
Run this script once to migrate from in-memory storage to Firebase
"""

from database_service import db_service
from datetime import datetime

def migrate_data():
    """Migrate all existing data to Firebase"""
    
    print("Starting migration to Firebase...")
    
    # Sample data from the original backend.py
    users_data = {
        "v1": {"email": "volunteer1@example.com", "password": "password123", "role": "volunteer", "user_id": "v1", "name": "Volunteer One", "contact": "111-222-3333"},
        "c1": {"email": "coordinator1@example.com", "password": "password123", "role": "coordinator", "user_id": "c1", "name": "Coordinator One", "contact": "444-555-6666"},
        "a1": {"email": "admin1@example.com", "password": "password123", "role": "admin", "user_id": "a1", "name": "Admin One", "contact": "777-888-9999"},
    }
    
    tasks_data = {
        "t1": {"title": "Cleanup Drive", "description": "Community park cleanup", "deadline": "2025-07-15", "priority": "High", "status": "Pending", "assigned_to": "v1"},
        "t2": {"title": "Food Distribution", "description": "Distribute food to needy families", "deadline": "2025-07-10", "priority": "Medium", "status": "In Progress", "assigned_to": "v1"},
        "t3": {"title": "Event Setup", "description": "Set up stage for charity event", "deadline": "2025-07-20", "priority": "High", "status": "Pending", "assigned_to": None},
        "t4": {"title": "Fundraising Call", "description": "Call potential donors", "deadline": "2025-07-25", "priority": "Medium", "status": "Pending", "assigned_to": None},
    }
    
    attendance_data = [
        {"log_id": "att1", "user_id": "v1", "task_id": "t1", "date": "2025-07-05"},
        {"log_id": "att2", "user_id": "v1", "task_id": "t2", "date": "2025-07-06"},
    ]
    
    ratings_data = [
        {"rating_id": "r1", "volunteer_id": "v1", "coordinator_id": "c1", "task_id": "t1", "score": 4, "comments": "Good effort on cleanup."},
    ]
    
    expenses_data = [
        {"expense_id": "e1", "task_id": "t1", "amount": 100, "category": "decoration", "logged_by": "a1"},
        {"expense_id": "e2", "task_id": "t2", "amount": 50, "category": "food", "logged_by": "a1"},
    ]
    
    try:
        # Migrate users
        print("Migrating users...")
        for user_id, user_data in users_data.items():
            db_service.create_user(user_data)
        print(f"✓ Migrated {len(users_data)} users")
        
        # Migrate tasks
        print("Migrating tasks...")
        for task_id, task_data in tasks_data.items():
            db_service.create_task(task_data)
        print(f"✓ Migrated {len(tasks_data)} tasks")
        
        # Migrate attendance logs
        print("Migrating attendance logs...")
        for attendance in attendance_data:
            db_service.create_attendance_log(attendance)
        print(f"✓ Migrated {len(attendance_data)} attendance logs")
        
        # Migrate ratings
        print("Migrating ratings...")
        for rating in ratings_data:
            db_service.create_rating(rating)
        print(f"✓ Migrated {len(ratings_data)} ratings")
        
        # Migrate expenses
        print("Migrating expenses...")
        for expense in expenses_data:
            db_service.create_expense(expense)
        print(f"✓ Migrated {len(expenses_data)} expenses")
        
        print("\n🎉 Migration completed successfully!")
        print("All data has been migrated to Firebase Firestore.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Please check your Firebase configuration and try again.")

if __name__ == "__main__":
    migrate_data()


