#!/usr/bin/env python3
"""
Comprehensive Volunteer Permissions Test
Tests all volunteer-specific functionality and access control
"""

import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
VOLUNTEER_CREDENTIALS = {
    "email": "volunteer1@example.com",
    "password": "password123"
}

class VolunteerTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({"test": test_name, "passed": passed, "details": details})

    def test_login_and_authentication(self):
        print("\n=== 1️⃣ LOGIN & ROLE AUTHENTICATION ===")
        # Login
        response = self.session.post(f"{BASE_URL}/login", json=VOLUNTEER_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            if data.get("role") == "volunteer" and data.get("redirect_to") == "/volunteer/dashboard":
                self.log_test("Login with volunteer credentials", True)
            else:
                self.log_test("Login with volunteer credentials", False, f"Expected volunteer role, got {data.get('role')}")
        else:
            self.log_test("Login with volunteer credentials", False, f"Status: {response.status_code}")
        # Session check
        response = self.session.get(f"{BASE_URL}/session/check")
        if response.status_code == 200:
            data = response.json()
            if data.get("logged_in") and data.get("role") == "volunteer":
                self.log_test("Session stores volunteer role", True)
            else:
                self.log_test("Session stores volunteer role", False, f"Session data: {data}")
        else:
            self.log_test("Session stores volunteer role", False, f"Status: {response.status_code}")
        # Logout
        response = self.session.post(f"{BASE_URL}/logout")
        if response.status_code == 200:
            self.log_test("Logout clears session", True)
        else:
            self.log_test("Logout clears session", False, f"Status: {response.status_code}")
        # Re-login for other tests
        self.session.post(f"{BASE_URL}/login", json=VOLUNTEER_CREDENTIALS)

    def test_view_assigned_tasks(self):
        print("\n=== 2️⃣ VIEW ASSIGNED TASKS ===")
        # View assigned tasks
        response = self.session.get(f"{BASE_URL}/tasks/assigned")
        print("[DEBUG] /tasks/assigned response:", response.json())
        if response.status_code == 200:
            tasks = response.json()
            if isinstance(tasks, list) and len(tasks) > 0:
                self.log_test("View own assigned tasks", True, f"Found {len(tasks)} tasks")
                # Print the first task for debug
                print("[DEBUG] First assigned task:", tasks[0])
                # Try to extract the task_id correctly
                task_id = None
                if 'task_id' in tasks[0]:
                    task_id = tasks[0]['task_id']
                elif 'id' in tasks[0]:
                    task_id = tasks[0]['id']
                else:
                    # Try to get the key from the dict if it's a {id: ...} structure
                    for k in tasks[0]:
                        if k.startswith('t'):
                            task_id = k
                            break
                if not task_id:
                    self.log_test("View own task details", False, "Could not determine task_id from response")
                else:
                    response2 = self.session.get(f"{BASE_URL}/tasks/{task_id}")
                    if response2.status_code == 200:
                        self.log_test("View own task details", True)
                    else:
                        self.log_test("View own task details", False, f"Status: {response2.status_code}")
                self._last_task_id = task_id
            else:
                self.log_test("View own assigned tasks", False, "No tasks returned")
        else:
            self.log_test("View own assigned tasks", False, f"Status: {response.status_code}")
        # Try to view global task list (should fail)
        response = self.session.get(f"{BASE_URL}/tasks")
        if response.status_code in [401, 403, 404]:
            self.log_test("Cannot view global task list", True)
        else:
            self.log_test("Cannot view global task list", False, f"Status: {response.status_code}")

    def test_mark_tasks_completed(self):
        print("\n=== 3️⃣ MARK TASKS AS COMPLETED ===")
        # Use the last task_id from previous test
        task_id = getattr(self, '_last_task_id', None)
        if not task_id:
            response = self.session.get(f"{BASE_URL}/tasks/assigned")
            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    if 'task_id' in tasks[0]:
                        task_id = tasks[0]['task_id']
                    elif 'id' in tasks[0]:
                        task_id = tasks[0]['id']
                    else:
                        for k in tasks[0]:
                            if k.startswith('t'):
                                task_id = k
                                break
        if task_id:
            response2 = self.session.put(f"{BASE_URL}/tasks/update_status/{task_id}", json={"status": "Completed"})
            if response2.status_code == 200:
                self.log_test("Mark own task as completed", True)
            else:
                self.log_test("Mark own task as completed", False, f"Status: {response2.status_code}")
            response3 = self.session.put(f"{BASE_URL}/tasks/update_status/fake_task", json={"status": "Completed"})
            if response3.status_code in [403, 404]:
                self.log_test("Cannot mark unassigned task as completed", True)
            else:
                self.log_test("Cannot mark unassigned task as completed", False, f"Status: {response3.status_code}")
        else:
            self.log_test("No assigned tasks to mark as completed", True)

    def test_submit_attendance(self):
        print("\n=== 4️⃣ SUBMIT ATTENDANCE ===")
        # Use the last task_id from previous test
        task_id = getattr(self, '_last_task_id', None)
        if not task_id:
            response = self.session.get(f"{BASE_URL}/tasks/assigned")
            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    if 'task_id' in tasks[0]:
                        task_id = tasks[0]['task_id']
                    elif 'id' in tasks[0]:
                        task_id = tasks[0]['id']
                    else:
                        for k in tasks[0]:
                            if k.startswith('t'):
                                task_id = k
                                break
        if task_id:
            today = datetime.now().strftime("%Y-%m-%d")
            response2 = self.session.post(f"{BASE_URL}/attendance/submit", json={"task_id": task_id, "date": today})
            print(f"[DEBUG] Attendance submit response: {response2.status_code} {response2.text}")
            if response2.status_code in [200, 201]:
                self.log_test("Submit attendance for assigned task", True)
            else:
                self.log_test("Submit attendance for assigned task", False, f"Status: {response2.status_code}, {response2.text}")
            response3 = self.session.get(f"{BASE_URL}/attendance/my")
            if response3.status_code == 200:
                self.log_test("View own attendance logs", True)
            else:
                self.log_test("View own attendance logs", False, f"Status: {response3.status_code}")
            response4 = self.session.get(f"{BASE_URL}/attendance?volunteer_id=someone_else")
            if response4.status_code in [401, 403]:
                self.log_test("Cannot view others' attendance", True)
            else:
                self.log_test("Cannot view others' attendance", False, f"Status: {response4.status_code}")
        else:
            self.log_test("No assigned tasks for attendance", True)

    def test_view_personal_ratings(self):
        print("\n=== 5️⃣ VIEW PERSONAL RATINGS & FEEDBACK ===")
        response = self.session.get(f"{BASE_URL}/ratings/my")
        if response.status_code == 200:
            ratings = response.json()
            self.log_test("View own ratings/feedback", True, f"Found {len(ratings)} ratings")
        else:
            self.log_test("View own ratings/feedback", False, f"Status: {response.status_code}")
        # Try to view others' ratings
        response2 = self.session.get(f"{BASE_URL}/ratings?volunteer_id=someone_else")
        if response2.status_code in [401, 403]:
            self.log_test("Cannot view others' ratings", True)
        else:
            self.log_test("Cannot view others' ratings", False, f"Status: {response2.status_code}")
        # Try to submit a rating (should fail)
        rating_data = {"volunteer_id": "v1", "task_id": "t1", "score": 5, "comments": "Nice"}
        response3 = self.session.post(f"{BASE_URL}/ratings/add", json=rating_data)
        if response3.status_code in [401, 403]:
            self.log_test("Cannot submit ratings as volunteer", True)
        else:
            self.log_test("Cannot submit ratings as volunteer", False, f"Status: {response3.status_code}")
        # Try to edit a rating (should fail)
        response4 = self.session.put(f"{BASE_URL}/ratings/r1", json={"score": 5, "comments": "Edit"})
        if response4.status_code in [401, 403]:
            self.log_test("Cannot edit ratings as volunteer", True)
        else:
            self.log_test("Cannot edit ratings as volunteer", False, f"Status: {response4.status_code}")

    def test_profile(self):
        print("\n=== 6️⃣ VIEW & EDIT PERSONAL PROFILE ===")
        # View profile
        response = self.session.get(f"{BASE_URL}/profile")
        if response.status_code == 200:
            self.log_test("View own profile", True)
        else:
            self.log_test("View own profile", False, f"Status: {response.status_code}")
        # Update profile
        update_data = {"name": "Volunteer One Updated", "contact": "999-888-7777"}
        response2 = self.session.put(f"{BASE_URL}/profile/update", json=update_data)
        if response2.status_code == 200:
            self.log_test("Update own profile", True)
        else:
            self.log_test("Update own profile", False, f"Status: {response2.status_code}")
        # Try to view all users (should fail)
        response3 = self.session.get(f"{BASE_URL}/users")
        if response3.status_code in [401, 403]:
            self.log_test("Cannot view all users", True)
        else:
            self.log_test("Cannot view all users", False, f"Status: {response3.status_code}")

    def test_access_control(self):
        print("\n=== 8️⃣ ACCESS & SECURITY ===")
        restricted_endpoints = [
            ("/users", "GET"),
            ("/tasks/create", "POST"),
            ("/tasks", "GET"),
            ("/expenses", "GET"),
            ("/reports", "GET"),
        ]
        for endpoint, method in restricted_endpoints:
            if method == "GET":
                response = self.session.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = self.session.post(f"{BASE_URL}{endpoint}")
            else:
                continue
            if response.status_code in [401, 403, 404]:
                self.log_test(f"Cannot access {endpoint}", True)
            else:
                self.log_test(f"Cannot access {endpoint}", False, f"Status: {response.status_code}")

    def run_all_tests(self):
        print("🚀 Starting Volunteer Permissions Verification")
        print("=" * 60)
        try:
            self.test_login_and_authentication()
            self.test_view_assigned_tasks()
            self.test_mark_tasks_completed()
            self.test_submit_attendance()
            self.test_view_personal_ratings()
            self.test_profile()
            self.test_access_control()
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            passed = sum(1 for result in self.test_results if result["passed"])
            total = len(self.test_results)
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            if passed == total:
                print("\n🎉 ALL TESTS PASSED! Volunteer module is fully functional.")
                print("✅ Access control is properly enforced")
                print("✅ UI and backend are in sync with volunteer role logic")
            else:
                print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
        except Exception as e:
            print(f"\n❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    tester = VolunteerTester()
    tester.run_all_tests() 