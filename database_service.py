from firebase_config import get_firestore_db
from datetime import datetime
import uuid
from typing import List, Dict, Optional, Any

class DatabaseService:
    """Database service layer for Firebase Firestore operations"""
    
    def __init__(self):
        self.db = get_firestore_db()
        self.fallback_storage = {}  # In-memory fallback storage
        self.collections = {
            'users': 'users',
            'tasks': 'tasks', 
            'attendance': 'attendance_logs',
            'ratings': 'ratings',
            'expenses': 'expenses',
            'absentees': 'absentees_logs',
            'events': 'events',
            'groups': 'groups',
            'attendance_sessions': 'attendance_sessions',
            'announcements': 'announcements'
        }
        
        # If Firebase is not available, initialize with test users
        if not self.db:
            self._initialize_fallback_users()
    
    def _initialize_fallback_users(self):
        """Initialize fallback users when Firebase is not available"""
        test_users = [
            {
                "user_id": "test_admin_1",
                "name": "Admin One",
                "email": "admin1@example.com",
                "password": "password123",
                "role": "admin",
                "contact": "1234567892",
                "created_at": datetime.now().isoformat()
            },
            {
                "user_id": "test_coord_1", 
                "name": "Coordinator One",
                "email": "coordinator1@example.com",
                "password": "password123",
                "role": "coordinator",
                "contact": "1234567891",
                "created_at": datetime.now().isoformat()
            },
            {
                "user_id": "test_vol_1",
                "name": "Volunteer One",
                "email": "volunteer1@example.com", 
                "password": "password123",
                "role": "volunteer",
                "contact": "1234567890",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        self.fallback_storage['users'] = {user['email']: user for user in test_users}
        print(f"Initialized {len(test_users)} fallback users")
    
    def _get_collection_ref(self, collection_name: str):
        """Get Firestore collection reference"""
        if not self.db:
            return None
        return self.db.collection(self.collections.get(collection_name, collection_name))
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        if not self.db:
            return None
        
        user_id = user_data.get('user_id', f"{user_data.get('role', 'u')[0]}{uuid.uuid4().hex[:8]}")
        user_data['user_id'] = user_id
        user_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('users').document(user_id)
        doc_ref.set(user_data)
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('users').document(user_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if not self.db:
            # Use fallback storage
            return self.fallback_storage.get('users', {}).get(email)
        
        users_ref = self._get_collection_ref('users')
        query = users_ref.where('email', '==', email).limit(1)
        docs = query.get()
        
        for doc in docs:
            return doc.to_dict()
        return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        if not self.db:
            # Use fallback storage
            return list(self.fallback_storage.get('users', {}).values())
        
        users_ref = self._get_collection_ref('users')
        docs = users_ref.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get users by role"""
        if not self.db:
            return []
        
        users_ref = self._get_collection_ref('users')
        query = users_ref.where('role', '==', role)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('users').document(user_id)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('users').document(user_id)
        doc_ref.delete()
        return True
    
    # Task operations
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task"""
        if not self.db:
            return None
        
        task_id = task_data.get('task_id', f"t{uuid.uuid4().hex[:8]}")
        task_data['task_id'] = task_id
        task_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('tasks').document(task_id)
        doc_ref.set(task_data)
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('tasks').document(task_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        if not self.db:
            return []
        
        tasks_ref = self._get_collection_ref('tasks')
        docs = tasks_ref.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get tasks by status"""
        if not self.db:
            return []
        
        tasks_ref = self._get_collection_ref('tasks')
        query = tasks_ref.where('status', '==', status)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_tasks_by_assignee(self, assignee_id: str) -> List[Dict[str, Any]]:
        """Get tasks assigned to a specific user (supports both single and multiple assignees)"""
        if not self.db:
            return []
        
        tasks_ref = self._get_collection_ref('tasks')
        docs = tasks_ref.stream()
        tasks = [doc.to_dict() for doc in docs]
        
        # Filter tasks where the user is either the single assignee or in the multiple assignees list
        filtered_tasks = []
        for task in tasks:
            if task.get('assigned_to') == assignee_id:
                filtered_tasks.append(task)
            elif task.get('assigned_volunteers') and assignee_id in task.get('assigned_volunteers', []):
                filtered_tasks.append(task)
        
        return filtered_tasks
    
    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update task data"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('tasks').document(task_id)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('tasks').document(task_id)
        doc_ref.delete()
        return True
    
    def assign_multiple_volunteers(self, task_id: str, volunteer_ids: List[str]) -> bool:
        """Assign multiple volunteers to a task"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('tasks').document(task_id)
        update_data = {
            'assigned_volunteers': volunteer_ids,
            'updated_at': datetime.now()
        }
        doc_ref.update(update_data)
        return True
    
    def add_volunteer_to_task(self, task_id: str, volunteer_id: str) -> bool:
        """Add a volunteer to an existing task's assignee list"""
        if not self.db:
            return False
        
        task = self.get_task(task_id)
        if not task:
            return False
        
        current_volunteers = task.get('assigned_volunteers', [])
        if volunteer_id not in current_volunteers:
            current_volunteers.append(volunteer_id)
            
            doc_ref = self._get_collection_ref('tasks').document(task_id)
            update_data = {
                'assigned_volunteers': current_volunteers,
                'updated_at': datetime.now()
            }
            doc_ref.update(update_data)
        
        return True
    
    def remove_volunteer_from_task(self, task_id: str, volunteer_id: str) -> bool:
        """Remove a volunteer from a task's assignee list"""
        if not self.db:
            return False
        
        task = self.get_task(task_id)
        if not task:
            return False
        
        current_volunteers = task.get('assigned_volunteers', [])
        if volunteer_id in current_volunteers:
            current_volunteers.remove(volunteer_id)
            
            doc_ref = self._get_collection_ref('tasks').document(task_id)
            update_data = {
                'assigned_volunteers': current_volunteers,
                'updated_at': datetime.now()
            }
            doc_ref.update(update_data)
        
        return True
    
    # Attendance operations
    def create_attendance_log(self, attendance_data: Dict[str, Any]) -> str:
        """Create attendance log"""
        if not self.db:
            return None
        
        log_id = attendance_data.get('log_id', f"att{uuid.uuid4().hex[:8]}")
        attendance_data['log_id'] = log_id
        attendance_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('attendance').document(log_id)
        doc_ref.set(attendance_data)
        return log_id
    
    def get_attendance_logs(self, user_id: Optional[str] = None, task_id: Optional[str] = None, date: Optional[str] = None, event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get attendance logs with optional filters"""
        if not self.db:
            return []
        
        attendance_ref = self._get_collection_ref('attendance')
        query = attendance_ref
        
        if user_id:
            query = query.where('user_id', '==', user_id)
        if task_id:
            query = query.where('task_id', '==', task_id)
        if date:
            query = query.where('date', '==', date)
        if event_id:
            query = query.where('event_id', '==', event_id)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    
    # Rating operations
    def create_rating(self, rating_data: Dict[str, Any]) -> str:
        """Create rating"""
        if not self.db:
            return None
        
        rating_id = rating_data.get('rating_id', f"r{uuid.uuid4().hex[:8]}")
        rating_data['rating_id'] = rating_id
        rating_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('ratings').document(rating_id)
        doc_ref.set(rating_data)
        return rating_id
    
    def get_ratings(self, volunteer_id: Optional[str] = None, task_id: Optional[str] = None, coordinator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ratings with optional filters"""
        if not self.db:
            return []
        
        ratings_ref = self._get_collection_ref('ratings')
        query = ratings_ref
        
        if volunteer_id:
            query = query.where('volunteer_id', '==', volunteer_id)
        if task_id:
            query = query.where('task_id', '==', task_id)
        if coordinator_id:
            query = query.where('coordinator_id', '==', coordinator_id)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_rating(self, rating_id: str) -> Optional[Dict[str, Any]]:
        """Get rating by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('ratings').document(rating_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def update_rating(self, rating_id: str, update_data: Dict[str, Any]) -> bool:
        """Update rating"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('ratings').document(rating_id)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        return True
    
    def delete_rating(self, rating_id: str) -> bool:
        """Delete rating"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('ratings').document(rating_id)
        doc_ref.delete()
        return True
    
    # Expense operations
    def create_expense(self, expense_data: Dict[str, Any]) -> str:
        """Create expense"""
        if not self.db:
            return None
        
        expense_id = expense_data.get('expense_id', f"e{uuid.uuid4().hex[:8]}")
        expense_data['expense_id'] = expense_id
        expense_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('expenses').document(expense_id)
        doc_ref.set(expense_data)
        return expense_id
    
    def get_expenses(self, task_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get expenses with optional filters"""
        if not self.db:
            return []
        
        expenses_ref = self._get_collection_ref('expenses')
        query = expenses_ref
        
        if task_id:
            query = query.where('task_id', '==', task_id)
        if category:
            query = query.where('category', '==', category)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_expense(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Get expense by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('expenses').document(expense_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def update_expense(self, expense_id: str, update_data: Dict[str, Any]) -> bool:
        """Update expense"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('expenses').document(expense_id)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        return True
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete expense"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('expenses').document(expense_id)
        doc_ref.delete()
        return True
    
    # Absentee operations
    def create_absentee_log(self, absentee_data: Dict[str, Any]) -> str:
        """Create absentee log"""
        if not self.db:
            return None
        
        log_id = absentee_data.get('log_id', f"abs{uuid.uuid4().hex[:8]}")
        absentee_data['log_id'] = log_id
        absentee_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('absentees').document(log_id)
        doc_ref.set(absentee_data)
        return log_id
    
    def get_absentee_logs(self, user_id: Optional[str] = None, task_id: Optional[str] = None, date: Optional[str] = None, event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get absentee logs with optional filters"""
        if not self.db:
            return []
        
        absentees_ref = self._get_collection_ref('absentees')
        query = absentees_ref
        
        if user_id:
            query = query.where('user_id', '==', user_id)
        if task_id:
            query = query.where('task_id', '==', task_id)
        if date:
            query = query.where('date', '==', date)
        if event_id:
            query = query.where('event_id', '==', event_id)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def check_absentee_exists(self, user_id: str, task_id: str, date: str) -> bool:
        """Check if absentee log already exists for user, task, and date"""
        if not self.db:
            return False
        
        absentees_ref = self._get_collection_ref('absentees')
        query = absentees_ref.where('user_id', '==', user_id).where('task_id', '==', task_id).where('date', '==', date)
        docs = query.limit(1).get()
        return len(docs) > 0
    
    # Event operations
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create a new event"""
        if not self.db:
            return None
        
        event_id = event_data.get('event_id', f"evt{uuid.uuid4().hex[:8]}")
        event_data['event_id'] = event_id
        event_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('events').document(event_id)
        doc_ref.set(event_data)
        return event_id
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('events').document(event_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all events"""
        if not self.db:
            return []
        
        events_ref = self._get_collection_ref('events')
        docs = events_ref.stream()
        return [doc.to_dict() for doc in docs]
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> bool:
        """Update event data"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('events').document(event_id)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        return True
    
    def delete_event(self, event_id: str) -> bool:
        """Delete event"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('events').document(event_id)
        doc_ref.delete()
        return True
    
    # Group operations
    def create_group(self, group_data: Dict[str, Any]) -> str:
        """Create a new group"""
        if not self.db:
            return None
        
        group_id = group_data.get('group_id', f"grp{uuid.uuid4().hex[:8]}")
        group_data['group_id'] = group_id
        group_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('groups').document(group_id)
        doc_ref.set(group_data)
        return group_id
    
    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get group by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('groups').document(group_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Get all groups"""
        if not self.db:
            return []
        
        groups_ref = self._get_collection_ref('groups')
        docs = groups_ref.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_users_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        """Get users by group"""
        if not self.db:
            return []
        
        users_ref = self._get_collection_ref('users')
        query = users_ref.where('group_id', '==', group_id)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def update_group(self, group_id: str, update_data: Dict[str, Any]) -> bool:
        """Update group data"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('groups').document(group_id)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        return True
    
    def delete_group(self, group_id: str) -> bool:
        """Delete group"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('groups').document(group_id)
        doc_ref.delete()
        return True
    
    # Enhanced Attendance Operations
    def create_attendance_session(self, session_data: Dict[str, Any]) -> str:
        """Create an attendance session for bulk marking"""
        if not self.db:
            return None
        
        session_id = session_data.get('session_id', f"ses{uuid.uuid4().hex[:8]}")
        session_data['session_id'] = session_id
        session_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('attendance_sessions').document(session_id)
        doc_ref.set(session_data)
        return session_id
    
    def get_attendance_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get attendance session by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('attendance_sessions').document(session_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_attendance_sessions(self, event_id: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get attendance sessions with optional filters"""
        if not self.db:
            return []
        
        sessions_ref = self._get_collection_ref('attendance_sessions')
        query = sessions_ref
        
        if event_id:
            query = query.where('event_id', '==', event_id)
        if date:
            query = query.where('date', '==', date)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def bulk_mark_attendance(self, attendance_records: List[Dict[str, Any]]) -> List[str]:
        """Bulk mark attendance for multiple users"""
        if not self.db:
            return []
        
        created_ids = []
        batch = self.db.batch()
        
        for record in attendance_records:
            log_id = record.get('log_id', f"att{uuid.uuid4().hex[:8]}")
            record['log_id'] = log_id
            record['created_at'] = datetime.now()
            
            doc_ref = self._get_collection_ref('attendance').document(log_id)
            batch.set(doc_ref, record)
            created_ids.append(log_id)
        
        batch.commit()
        return created_ids
    
    def get_attendance_insights(self, event_id: Optional[str] = None, date: Optional[str] = None, group_id: Optional[str] = None) -> Dict[str, Any]:
        """Get attendance insights and statistics"""
        if not self.db:
            print("Database not connected")
            return {}
        
        print(f"Getting insights for event_id={event_id}, date={date}, group_id={group_id}")
        
        # Get all users (filtered by group if specified)
        if group_id:
            users = self.get_users_by_group(group_id)
        else:
            users = self.get_users_by_role('volunteer')
        
        print(f"Found {len(users)} users")
        
        # Get attendance logs
        attendance_logs = self.get_attendance_logs(date=date)
        if event_id:
            attendance_logs = [log for log in attendance_logs if log.get('event_id') == event_id]
        
        print(f"Found {len(attendance_logs)} attendance logs")
        
        # Get absentee logs
        absentee_logs = self.get_absentee_logs(date=date)
        if event_id:
            absentee_logs = [log for log in absentee_logs if log.get('event_id') == event_id]
        
        print(f"Found {len(absentee_logs)} absentee logs")
        
        # Calculate statistics
        total_users = len(users)
        present_users = len(set(log['user_id'] for log in attendance_logs))
        absent_users = len(set(log['user_id'] for log in absentee_logs))
        unmarked_users = total_users - present_users - absent_users
        
        attendance_percentage = (present_users / total_users * 100) if total_users > 0 else 0
        
        # Get individual user attendance percentages
        user_stats = []
        for user in users:
            user_id = user['user_id']
            user_attendance = [log for log in attendance_logs if log['user_id'] == user_id]
            user_absent = [log for log in absentee_logs if log['user_id'] == user_id]
            
            # Calculate user's attendance percentage (simplified - would need more complex logic for real implementation)
            user_total_sessions = len(user_attendance) + len(user_absent)
            user_attendance_percentage = (len(user_attendance) / user_total_sessions * 100) if user_total_sessions > 0 else 0
            
            user_stats.append({
                'user_id': user_id,
                'name': user['name'],
                'email': user['email'],
                'attendance_percentage': round(user_attendance_percentage, 2),
                'present_count': len(user_attendance),
                'absent_count': len(user_absent)
            })
        
        result = {
            'total_users': total_users,
            'present_users': present_users,
            'absent_users': absent_users,
            'unmarked_users': unmarked_users,
            'attendance_percentage': round(attendance_percentage, 2),
            'user_stats': user_stats,
            'date': date,
            'event_id': event_id,
            'group_id': group_id
        }
        
        print(f"Insights result: {result}")
        return result
    
    def get_attendance_by_date_range(self, start_date: str, end_date: str, event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get attendance records within a date range"""
        if not self.db:
            return []
        
        attendance_ref = self._get_collection_ref('attendance')
        query = attendance_ref.where('date', '>=', start_date).where('date', '<=', end_date)
        
        if event_id:
            query = query.where('event_id', '==', event_id)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def get_absentee_list(self, event_id: Optional[str] = None, date: Optional[str] = None, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of absentees"""
        if not self.db:
            return []
        
        # Get all users (filtered by group if specified)
        if group_id:
            users = self.get_users_by_group(group_id)
        else:
            users = self.get_users_by_role('volunteer')
        
        # Get attendance logs for the specified criteria
        attendance_logs = self.get_attendance_logs(date=date)
        if event_id:
            attendance_logs = [log for log in attendance_logs if log.get('event_id') == event_id]
        
        # Get absentee logs
        absentee_logs = self.get_absentee_logs(date=date)
        if event_id:
            absentee_logs = [log for log in absentee_logs if log.get('event_id') == event_id]
        
        # Find users who are absent (either marked absent or didn't show up)
        present_user_ids = set(log['user_id'] for log in attendance_logs)
        absent_user_ids = set(log['user_id'] for log in absentee_logs)
        
        absentees = []
        for user in users:
            user_id = user['user_id']
            if user_id not in present_user_ids:
                absentees.append({
                    'user_id': user_id,
                    'name': user['name'],
                    'email': user['email'],
                    'status': 'marked_absent' if user_id in absent_user_ids else 'unmarked'
                })
        
        return absentees

    # Announcement operations
    def create_announcement(self, announcement_data: Dict[str, Any]) -> str:
        """Create a new announcement"""
        if not self.db:
            return None
        
        announcement_id = f"ann_{uuid.uuid4().hex[:8]}"
        announcement_data['announcement_id'] = announcement_id
        announcement_data['created_at'] = datetime.now()
        
        doc_ref = self._get_collection_ref('announcements').document(announcement_id)
        doc_ref.set(announcement_data)
        return announcement_id
    
    def get_announcement(self, announcement_id: str) -> Optional[Dict[str, Any]]:
        """Get announcement by ID"""
        if not self.db:
            return None
        
        doc_ref = self._get_collection_ref('announcements').document(announcement_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_announcements(self) -> List[Dict[str, Any]]:
        """Get all announcements"""
        if not self.db:
            return []
        
        collection_ref = self._get_collection_ref('announcements')
        docs = collection_ref.stream()
        
        announcements = []
        for doc in docs:
            announcement_data = doc.to_dict()
            announcements.append(announcement_data)
        
        return announcements
    
    def get_announcements_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """Get announcements for a specific event"""
        if not self.db:
            return []
        
        collection_ref = self._get_collection_ref('announcements')
        query = collection_ref.where('event_id', '==', event_id)
        docs = query.stream()
        
        announcements = []
        for doc in docs:
            announcement_data = doc.to_dict()
            announcements.append(announcement_data)
        
        return announcements
    
    def get_announcements_by_creator(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get announcements created by a specific user"""
        if not self.db:
            return []
        
        collection_ref = self._get_collection_ref('announcements')
        query = collection_ref.where('created_by', '==', creator_id)
        docs = query.stream()
        
        announcements = []
        for doc in docs:
            announcement_data = doc.to_dict()
            announcements.append(announcement_data)
        
        return announcements
    
    def update_announcement(self, announcement_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an announcement"""
        if not self.db:
            return False
        
        update_data['updated_at'] = datetime.now()
        doc_ref = self._get_collection_ref('announcements').document(announcement_id)
        doc_ref.update(update_data)
        return True
    
    def delete_announcement(self, announcement_id: str) -> bool:
        """Delete an announcement"""
        if not self.db:
            return False
        
        doc_ref = self._get_collection_ref('announcements').document(announcement_id)
        doc_ref.delete()
        return True

# Global database service instance
db_service = DatabaseService()
