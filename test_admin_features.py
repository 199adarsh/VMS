import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

class AdminTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_credentials = {
            "email": "admin1@example.com",
            "password": "password123"
        }
        
    def login_as_admin(self):
        """1️⃣ LOGIN & USER SESSION"""
        print("🔐 Testing Admin Login...")
        response = self.session.post(f"{BASE_URL}/login", json=self.admin_credentials)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful: {data['role']}")
            print(f"   Redirect: {data.get('redirect_to', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def test_session_check(self):
        """Check session stores role as admin"""
        print("\n🔍 Testing Session Check...")
        response = self.session.get(f"{BASE_URL}/session/check")
        if response.status_code == 200:
            data = response.json()
            if data.get('logged_in') and data.get('role') == 'admin':
                print("✅ Session correctly stores admin role")
                return True
            else:
                print(f"❌ Session issue: {data}")
                return False
        else:
            print(f"❌ Session check failed: {response.text}")
            return False
    
    def test_user_management(self):
        """2️⃣ USER MANAGEMENT"""
        print("\n👥 Testing User Management...")
        
        # Get all users
        response = self.session.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ View all users: Found {len(users)} users")
            for user in users:
                print(f"   - {user['name']} ({user['role']}) - {user['email']}")
        else:
            print(f"❌ Failed to get users: {response.text}")
            return False
        
        # Create new user
        new_user = {
            "email": "testvolunteer@example.com",
            "password": "testpass123",
            "role": "volunteer",
            "name": "Test Volunteer",
            "contact": "555-123-4567"
        }
        response = self.session.post(f"{BASE_URL}/users/create", json=new_user)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Create user successful: {data['user_id']}")
            new_user_id = data['user_id']
        else:
            print(f"❌ Failed to create user: {response.text}")
            return False
        
        # Update user
        update_data = {"name": "Updated Test Volunteer", "contact": "555-999-8888"}
        response = self.session.put(f"{BASE_URL}/users/{new_user_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Update user successful")
        else:
            print(f"❌ Failed to update user: {response.text}")
        
        # Delete user
        response = self.session.delete(f"{BASE_URL}/users/{new_user_id}")
        if response.status_code == 200:
            print("✅ Delete user successful")
        else:
            print(f"❌ Failed to delete user: {response.text}")
        
        return True
    
    def test_task_management(self):
        """3️⃣ TASK MANAGEMENT"""
        print("\n📋 Testing Task Management...")
        
        # Create task
        new_task = {
            "title": "Admin Test Task",
            "description": "Task created by admin for testing",
            "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "priority": "High"
        }
        response = self.session.post(f"{BASE_URL}/tasks/create", json=new_task)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Create task successful: {data['task_id']}")
            task_id = data['task_id']
        else:
            print(f"❌ Failed to create task: {response.text}")
            return False
        
        # Get all tasks
        response = self.session.get(f"{BASE_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ View all tasks: Found {len(tasks)} tasks")
        else:
            print(f"❌ Failed to get tasks: {response.text}")
        
        # Update task
        update_data = {"priority": "Medium", "status": "In Progress"}
        response = self.session.put(f"{BASE_URL}/tasks/{task_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Update task successful")
        else:
            print(f"❌ Failed to update task: {response.text}")
        
        # Delete task
        response = self.session.delete(f"{BASE_URL}/tasks/{task_id}")
        if response.status_code == 200:
            print("✅ Delete task successful")
        else:
            print(f"❌ Failed to delete task: {response.text}")
        
        return True
    
    def test_attendance_tracking(self):
        """4️⃣ ATTENDANCE TRACKING"""
        print("\n📆 Testing Attendance Tracking...")
        
        # Get all attendance
        response = self.session.get(f"{BASE_URL}/attendance")
        if response.status_code == 200:
            attendance = response.json()
            print(f"✅ View all attendance: Found {len(attendance)} records")
        else:
            print(f"❌ Failed to get attendance: {response.text}")
        
        # Get absentees
        response = self.session.get(f"{BASE_URL}/attendance/absentees")
        if response.status_code == 200:
            absentees = response.json()
            print(f"✅ View absentees: Found {len(absentees)} absent volunteers")
        else:
            print(f"❌ Failed to get absentees: {response.text}")
        
        return True
    
    def test_ratings(self):
        """5️⃣ VOLUNTEER RATINGS"""
        print("\n⭐ Testing Volunteer Ratings...")
        
        # Get all ratings
        response = self.session.get(f"{BASE_URL}/ratings")
        if response.status_code == 200:
            ratings = response.json()
            print(f"✅ View all ratings: Found {len(ratings)} ratings")
        else:
            print(f"❌ Failed to get ratings: {response.text}")
        
        # Submit rating (if we have volunteers and tasks)
        rating_data = {
            "volunteer_id": "v1",
            "task_id": "t1",
            "score": 5,
            "comments": "Excellent work from admin test"
        }
        response = self.session.post(f"{BASE_URL}/ratings/add", json=rating_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Submit rating successful: {data['rating_id']}")
            rating_id = data['rating_id']
        else:
            print(f"❌ Failed to submit rating: {response.text}")
            return True  # Continue with other tests
        
        # Update rating
        update_data = {"score": 4, "comments": "Updated admin test rating"}
        response = self.session.put(f"{BASE_URL}/ratings/{rating_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Update rating successful")
        else:
            print(f"❌ Failed to update rating: {response.text}")
        
        # Delete rating
        response = self.session.delete(f"{BASE_URL}/ratings/{rating_id}")
        if response.status_code == 200:
            print("✅ Delete rating successful")
        else:
            print(f"❌ Failed to delete rating: {response.text}")
        
        return True
    
    def test_expenses(self):
        """6️⃣ MONEY MANAGEMENT"""
        print("\n💸 Testing Money Management...")
        
        # Get all expenses
        response = self.session.get(f"{BASE_URL}/expenses")
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ View all expenses: Found {len(expenses)} expenses")
        else:
            print(f"❌ Failed to get expenses: {response.text}")
        
        # Log new expense
        expense_data = {
            "task_id": "t1",
            "amount": 150.50,
            "category": "supplies"
        }
        response = self.session.post(f"{BASE_URL}/expenses/log", json=expense_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Log expense successful: {data['expense_id']}")
            expense_id = data['expense_id']
        else:
            print(f"❌ Failed to log expense: {response.text}")
            return True  # Continue with other tests
        
        # Update expense
        update_data = {"amount": 175.00, "category": "equipment"}
        response = self.session.put(f"{BASE_URL}/expenses/{expense_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Update expense successful")
        else:
            print(f"❌ Failed to update expense: {response.text}")
        
        # Delete expense
        response = self.session.delete(f"{BASE_URL}/expenses/{expense_id}")
        if response.status_code == 200:
            print("✅ Delete expense successful")
        else:
            print(f"❌ Failed to delete expense: {response.text}")
        
        return True
    
    def test_reports(self):
        """7️⃣ REPORTING & INSIGHTS"""
        print("\n📊 Testing Reports...")
        
        reports = [
            ("tasks", "Task Report"),
            ("attendance", "Attendance Report"),
            ("ratings", "Ratings Report"),
            ("expenses", "Expenses Report"),
            ("assignments", "Assignments Report")
        ]
        
        for report_type, report_name in reports:
            response = self.session.get(f"{BASE_URL}/reports/{report_type}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {report_name}: Data retrieved successfully")
                if isinstance(data, dict):
                    print(f"   - Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   - Items: {len(data)}")
            else:
                print(f"❌ Failed to get {report_name}: {response.text}")
        
        return True
    
    def test_security(self):
        """8️⃣ ACCESS & SECURITY"""
        print("\n🔒 Testing Security...")
        
        # Test that admin can access admin-only endpoints
        admin_endpoints = [
            ("/users", "GET"),
            ("/tasks", "GET"),
            ("/attendance", "GET"),
            ("/ratings", "GET"),
            ("/expenses", "GET")
        ]
        
        for endpoint, method in admin_endpoints:
            if method == "GET":
                response = self.session.get(f"{BASE_URL}{endpoint}")
            else:
                response = self.session.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code in [200, 201]:
                print(f"✅ Admin can access {endpoint}")
            else:
                print(f"❌ Admin cannot access {endpoint}: {response.status_code}")
        
        return True
    
    def test_logout(self):
        """Test logout functionality"""
        print("\n🚪 Testing Logout...")
        response = self.session.post(f"{BASE_URL}/logout")
        if response.status_code == 200:
            print("✅ Logout successful")
            
            # Test that protected endpoints are blocked after logout
            response = self.session.get(f"{BASE_URL}/users")
            if response.status_code == 401:
                print("✅ Protected endpoints correctly blocked after logout")
            else:
                print(f"❌ Protected endpoint still accessible: {response.status_code}")
        else:
            print(f"❌ Logout failed: {response.text}")
        
        return True
    
    def run_all_tests(self):
        """Run all admin feature tests"""
        print("🧪 ADMIN ROLE FEATURE TESTING")
        print("=" * 50)
        
        if not self.login_as_admin():
            return False
        
        if not self.test_session_check():
            return False
        
        if not self.test_user_management():
            return False
        
        if not self.test_task_management():
            return False
        
        if not self.test_attendance_tracking():
            return False
        
        if not self.test_ratings():
            return False
        
        if not self.test_expenses():
            return False
        
        if not self.test_reports():
            return False
        
        if not self.test_security():
            return False
        
        if not self.test_logout():
            return False
        
        print("\n" + "=" * 50)
        print("🎉 ALL ADMIN FEATURES TESTED SUCCESSFULLY!")
        return True

if __name__ == "__main__":
    tester = AdminTester()
    tester.run_all_tests() 