from firebase_config import get_firestore_db
from datetime import datetime
import uuid
from typing import List, Dict, Optional, Any

class DatabaseService:
    """Database service layer for Firebase Firestore operations"""
    
    def __init__(self):
        self.db = get_firestore_db()
        self.collections = {
            'users': 'users',
            'tasks': 'tasks', 
            'attendance': 'attendance_logs',
            'ratings': 'ratings',
            'expenses': 'expenses',
            'absentees': 'absentees_logs'
        }
    
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
            return None
        
        users_ref = self._get_collection_ref('users')
        query = users_ref.where('email', '==', email).limit(1)
        docs = query.get()
        
        for doc in docs:
            return doc.to_dict()
        return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        if not self.db:
            return []
        
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
        """Get tasks assigned to a specific user"""
        if not self.db:
            return []
        
        tasks_ref = self._get_collection_ref('tasks')
        query = tasks_ref.where('assigned_to', '==', assignee_id)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
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
    
    def get_attendance_logs(self, user_id: Optional[str] = None, task_id: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
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
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def check_attendance_exists(self, user_id: str, task_id: str, date: str) -> bool:
        """Check if attendance already exists for user, task, and date"""
        if not self.db:
            return False
        
        attendance_ref = self._get_collection_ref('attendance')
        query = attendance_ref.where('user_id', '==', user_id).where('task_id', '==', task_id).where('date', '==', date)
        docs = query.limit(1).get()
        return len(docs) > 0
    
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
    
    def get_absentee_logs(self, user_id: Optional[str] = None, task_id: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
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

# Global database service instance
db_service = DatabaseService()
