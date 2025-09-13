"""
Test script to verify Firebase integration is working correctly
Run this script to test the Firebase connection and basic operations
"""

from database_service import db_service
import json

def test_firebase_connection():
    """Test basic Firebase connection"""
    print("Testing Firebase connection...")
    
    try:
        # Test if we can get the database instance
        db = db_service.db
        if db is None:
            print("❌ Firebase connection failed - database is None")
            return False
        
        print("✅ Firebase connection successful")
        return True
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False

def test_user_operations():
    """Test user CRUD operations"""
    print("\nTesting user operations...")
    
    try:
        # Test creating a user
        test_user = {
            "email": "test@example.com",
            "password": "testpass123",
            "role": "volunteer",
            "name": "Test User",
            "contact": "123-456-7890"
        }
        
        user_id = db_service.create_user(test_user)
        if not user_id:
            print("❌ Failed to create user")
            return False
        print(f"✅ User created with ID: {user_id}")
        
        # Test getting user
        user = db_service.get_user(user_id)
        if not user:
            print("❌ Failed to get user")
            return False
        print("✅ User retrieved successfully")
        
        # Test updating user
        update_data = {"name": "Updated Test User"}
        success = db_service.update_user(user_id, update_data)
        if not success:
            print("❌ Failed to update user")
            return False
        print("✅ User updated successfully")
        
        # Test getting user by email
        user_by_email = db_service.get_user_by_email("test@example.com")
        if not user_by_email:
            print("❌ Failed to get user by email")
            return False
        print("✅ User retrieved by email successfully")
        
        # Clean up - delete test user
        db_service.delete_user(user_id)
        print("✅ Test user cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ User operations failed: {e}")
        return False

def test_task_operations():
    """Test task CRUD operations"""
    print("\nTesting task operations...")
    
    try:
        # Test creating a task
        test_task = {
            "title": "Test Task",
            "description": "This is a test task",
            "deadline": "2025-12-31",
            "priority": "High",
            "status": "Pending",
            "assigned_to": None
        }
        
        task_id = db_service.create_task(test_task)
        if not task_id:
            print("❌ Failed to create task")
            return False
        print(f"✅ Task created with ID: {task_id}")
        
        # Test getting task
        task = db_service.get_task(task_id)
        if not task:
            print("❌ Failed to get task")
            return False
        print("✅ Task retrieved successfully")
        
        # Test updating task
        update_data = {"status": "In Progress"}
        success = db_service.update_task(task_id, update_data)
        if not success:
            print("❌ Failed to update task")
            return False
        print("✅ Task updated successfully")
        
        # Clean up - delete test task
        db_service.delete_task(task_id)
        print("✅ Test task cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Task operations failed: {e}")
        return False

def test_attendance_operations():
    """Test attendance operations"""
    print("\nTesting attendance operations...")
    
    try:
        # Create a test user first
        test_user = {
            "email": "attendance_test@example.com",
            "password": "testpass123",
            "role": "volunteer",
            "name": "Attendance Test User",
            "contact": "123-456-7890"
        }
        user_id = db_service.create_user(test_user)
        
        # Create a test task
        test_task = {
            "title": "Attendance Test Task",
            "description": "This is a test task for attendance",
            "deadline": "2025-12-31",
            "priority": "Medium",
            "status": "Pending",
            "assigned_to": user_id
        }
        task_id = db_service.create_task(test_task)
        
        # Test creating attendance log
        attendance_data = {
            "user_id": user_id,
            "task_id": task_id,
            "date": "2025-01-15"
        }
        
        log_id = db_service.create_attendance_log(attendance_data)
        if not log_id:
            print("❌ Failed to create attendance log")
            return False
        print(f"✅ Attendance log created with ID: {log_id}")
        
        # Test getting attendance logs
        logs = db_service.get_attendance_logs(user_id=user_id)
        if not logs:
            print("❌ Failed to get attendance logs")
            return False
        print("✅ Attendance logs retrieved successfully")
        
        # Clean up
        db_service.delete_user(user_id)
        db_service.delete_task(task_id)
        print("✅ Test data cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Attendance operations failed: {e}")
        return False

def run_all_tests():
    """Run all Firebase integration tests"""
    print("🚀 Starting Firebase Integration Tests")
    print("=" * 50)
    
    tests = [
        test_firebase_connection,
        test_user_operations,
        test_task_operations,
        test_attendance_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Firebase integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check your Firebase configuration.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()


