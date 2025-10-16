from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS
import uuid
import os
from functools import wraps
from datetime import datetime
from database_service import db_service
from firebase_auth_service import firebase_auth_service
from firebase_config import firebase_config
from ai_service import ai_service
import jwt
import firebase_admin

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_super_secret_key') # Use environment variable in production
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session-based auth first
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        # Check token-based auth
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Verify JWT token
                decoded_token = jwt.decode(token, app.secret_key, algorithms=['HS256'])
                user_id = decoded_token.get('user_id')
                if user_id:
                    # Set session for this request
                    session['user_id'] = user_id
                    session['role'] = decoded_token.get('role')
                    session['provider'] = decoded_token.get('provider', 'email')
                    return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token"}), 401
        
        return jsonify({"message": "Unauthorized: Login required"}), 401
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                print('DEBUG: No user_id in session')
                return jsonify({"message": "Unauthorized: Login required"}), 401
            current_user_id = session['user_id']
            user_data = db_service.get_user(current_user_id)
            print(f'DEBUG: user_id={current_user_id}, session_role={session.get("role")}, user_data_role={user_data["role"] if user_data else None}, allowed_roles={allowed_roles}')
            if not user_data or user_data['role'] not in allowed_roles:
                print('DEBUG: Forbidden - insufficient permissions')
                return jsonify({"message": "Forbidden: Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Blueprints ---
# from vol import vol_bp
# app.register_blueprint(vol_bp)

# --- UI Route ---
@app.context_processor
def inject_current_user():
    user = db_service.get_user(session['user_id']) if 'user_id' in session else None
    return dict(current_user=user)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/dashbords')
@login_required
def dashbords():
    return render_template('dashbords.html')

# --- Authentication Endpoints ---

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    return_token = data.get('return_token', False)  # Option to return JWT token

    user = db_service.get_user_by_email(email)
    
    if user and user.get('password') == password:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        session['provider'] = user.get('provider', 'email')
        
        response_data = {
            "message": "Login successful", 
            "role": user['role'], 
            "redirect_to": "/dashbords",
            "user": {
                "user_id": user['user_id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role'],
                "profile_picture": user.get('profile_picture', '')
            }
        }
        
        if return_token:
            # Generate JWT token
            token_payload = {
                'user_id': user['user_id'],
                'role': user['role'],
                'provider': user.get('provider', 'email'),
                'exp': datetime.utcnow().timestamp() + 3600  # 1 hour expiry
            }
            token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
            response_data['token'] = token
        
        return jsonify(response_data), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('provider', None)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/session/check', methods=['GET'])
def check_session():
    if 'role' in session:
        return jsonify({
            'logged_in': True, 
            'role': session['role'],
            'provider': session.get('provider', 'email'),
            'user_id': session.get('user_id')
        }), 200
    return jsonify({'logged_in': False}), 200

@app.route('/auth/refresh', methods=['POST'])
@login_required
def refresh_token():
    """Refresh JWT token"""
    current_user_id = session['user_id']
    user = db_service.get_user(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Generate new JWT token
    token_payload = {
        'user_id': current_user_id,
        'role': session['role'],
        'provider': session.get('provider', 'email'),
        'exp': datetime.utcnow().timestamp() + 3600  # 1 hour expiry
    }
    token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
    
    return jsonify({
        "message": "Token refreshed successfully",
        "token": token,
        "expires_in": 3600
    }), 200

# --- Google Authentication Endpoints ---

@app.route('/auth/google', methods=['POST'])
def google_auth():
    """Authenticate user with Google ID token"""
    try:
        data = request.get_json()
        print(f"Google auth request data: {data}")
        
        id_token = data.get('id_token')
        
        if not id_token:
            print("No ID token provided")
            return jsonify({"message": "Google ID token is required"}), 400
        
        print(f"Verifying Google token: {id_token[:50]}...")
        
        # Verify Google token
        user_info = firebase_auth_service.verify_google_token(id_token)
        print(f"User info from token: {user_info}")
        
        if not user_info:
            print("Token verification failed")
            return jsonify({"message": "Invalid Google token"}), 401
        
        email = user_info.get('email')
        if not email:
            print("No email found in token")
            return jsonify({"message": "Email not found in Google token"}), 400
        
        print(f"Looking up user with email: {email}")
        
        # Check if user exists in our database
        user = db_service.get_user_by_email(email)
        print(f"User found: {user}")
        
        if not user:
            # Create new user with Google info
            user_data = {
                "email": email,
                "name": user_info.get('name', ''),
                "contact": "",
                "role": "volunteer",  # Default role for Google sign-ups
                "provider": "google",
                "firebase_uid": user_info.get('uid'),
                "profile_picture": user_info.get('picture', ''),
                "email_verified": user_info.get('email_verified', False)
            }
            user_id = db_service.create_user(user_data)
            user = db_service.get_user(user_id)
        else:
            # Update existing user with Google info if needed
            update_data = {}
            if not user.get('firebase_uid'):
                update_data['firebase_uid'] = user_info.get('uid')
            if not user.get('provider'):
                update_data['provider'] = 'google'
            if user_info.get('picture') and not user.get('profile_picture'):
                update_data['profile_picture'] = user_info.get('picture')
            
            if update_data:
                db_service.update_user(user['user_id'], update_data)
                user.update(update_data)
        
        # Create session
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        session['provider'] = 'google'
        
        # Generate JWT token
        token_payload = {
            'user_id': user['user_id'],
            'role': user['role'],
            'provider': 'google',
            'exp': datetime.utcnow().timestamp() + 3600  # 1 hour expiry
        }
        token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
        
        print("Google authentication successful")
        return jsonify({
            "message": "Google authentication successful",
            "role": user['role'],
            "redirect_to": "/dashbords",
            "token": token,
            "user": {
                "user_id": user['user_id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role'],
                "profile_picture": user.get('profile_picture', '')
            }
        }), 200
        
    except Exception as e:
        print(f"Error in Google auth: {e}")
        return jsonify({"message": f"Authentication error: {str(e)}"}), 500

@app.route('/auth/google/register', methods=['POST'])
def google_register():
    """Register new user with Google (with role selection)"""
    try:
        data = request.get_json()
        print(f"Google register request data: {data}")
        
        id_token = data.get('id_token')
        role = data.get('role', 'volunteer')  # Allow role selection
        contact = data.get('contact', '')
        
        if not id_token:
            print("No ID token provided for registration")
            return jsonify({"message": "Google ID token is required"}), 400
        
        if role not in ['volunteer', 'coordinator']:
            return jsonify({"message": "Invalid role. Must be 'volunteer' or 'coordinator'"}), 400
        
        print(f"Verifying Google token for registration: {id_token[:50]}...")
        
        # Verify Google token
        user_info = firebase_auth_service.verify_google_token(id_token)
        print(f"User info from token: {user_info}")
        
        if not user_info:
            print("Token verification failed for registration")
            return jsonify({"message": "Invalid Google token"}), 401
        
        email = user_info.get('email')
        if not email:
            print("No email found in token for registration")
            return jsonify({"message": "Email not found in Google token"}), 400
        
        print(f"Looking up existing user with email: {email}")
        
        # Check if user already exists
        existing_user = db_service.get_user_by_email(email)
        if existing_user:
            print("User already exists")
            return jsonify({"message": "User with this email already exists"}), 409
        
        print("Creating new user")
        # Create new user
        user_data = {
            "email": email,
            "name": user_info.get('name', ''),
            "contact": contact,
            "role": role,
            "provider": "google",
            "firebase_uid": user_info.get('uid'),
            "profile_picture": user_info.get('picture', ''),
            "email_verified": user_info.get('email_verified', False)
        }
        
        user_id = db_service.create_user(user_data)
        user = db_service.get_user(user_id)
        
        # Create session
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        session['provider'] = 'google'
        
        # Generate JWT token
        token_payload = {
            'user_id': user['user_id'],
            'role': user['role'],
            'provider': 'google',
            'exp': datetime.utcnow().timestamp() + 3600  # 1 hour expiry
        }
        token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
        
        print("Google registration successful")
        return jsonify({
            "message": "Google registration successful",
            "role": user['role'],
            "redirect_to": "/dashbords",
            "token": token,
            "user": {
                "user_id": user['user_id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role'],
                "profile_picture": user.get('profile_picture', '')
            }
        }), 201
        
    except Exception as e:
        print(f"Error in Google registration: {e}")
        return jsonify({"message": f"Registration error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'firebase_connected': db_service.db is not None,
        'environment': 'production' if os.getenv('FIREBASE_PROJECT_ID') else 'development',
        'firebase_admin_initialized': len(firebase_admin._apps) > 0
    }), 200

@app.route('/test-firebase', methods=['GET'])
def test_firebase():
    """Test Firebase Admin SDK initialization"""
    try:
        from firebase_admin import auth
        # Try to list users (this will fail if not properly initialized)
        users = auth.list_users(max_results=1)
        return jsonify({
            'firebase_admin_initialized': True,
            'can_access_auth': True,
            'message': 'Firebase Admin SDK is working'
        }), 200
    except Exception as e:
        return jsonify({
            'firebase_admin_initialized': len(firebase_admin._apps) > 0,
            'can_access_auth': False,
            'error': str(e),
            'message': 'Firebase Admin SDK has issues'
        }), 500

# --- VOLUNTEER ROLE ENDPOINTS ---

@app.route('/tasks/assigned', methods=['GET'])
@role_required(['volunteer'])
def volunteer_assigned_tasks():
    current_user_id = session['user_id']
    assigned_tasks = db_service.get_tasks_by_assignee(current_user_id)
    # Filter out sensitive information if necessary before sending
    return jsonify(assigned_tasks), 200

@app.route('/tasks/<task_id>', methods=['GET'])
@role_required(['volunteer', 'coordinator', 'admin'])
def get_task_details(task_id):
    current_user_id = session['user_id']
    current_user_role = session.get('role')
    task = db_service.get_task(task_id)
    
    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    # Volunteers can only see tasks assigned to them
    if current_user_role == 'volunteer':
        assigned_volunteers = task.get('assigned_volunteers', [])
        if task.get('assigned_to') != current_user_id and current_user_id not in assigned_volunteers:
            return jsonify({"message": "Task not assigned to you"}), 403
    
    # Coordinators and admins can see any task
    return jsonify(task), 200

@app.route('/tasks/update_status/<task_id>', methods=['PUT'])
@role_required(['volunteer'])
def volunteer_mark_task_completed(task_id):
    current_user_id = session['user_id']
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    # Check if user is assigned to this task (either as single assignee or in multiple volunteers)
    assigned_volunteers = task.get('assigned_volunteers', [])
    if task.get('assigned_to') != current_user_id and current_user_id not in assigned_volunteers:
        return jsonify({"message": "Forbidden: Cannot update tasks not assigned to you"}), 403

    data = request.get_json()
    new_status = data.get('status')
    if new_status == "Completed":
        db_service.update_task(task_id, {"status": "Completed", "completion_percentage": 100})
        task['status'] = "Completed"
        task['completion_percentage'] = 100
        return jsonify({"message": f"Task {task_id} marked as Completed", "task": task}), 200
    return jsonify({"message": "Invalid status update"}), 400

@app.route('/tasks/update_completion/<task_id>', methods=['PUT'])
@role_required(['volunteer'])
def volunteer_update_task_completion(task_id):
    """Update task completion percentage (0-100%)"""
    current_user_id = session['user_id']
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    # Check if user is assigned to this task (either as single assignee or in multiple volunteers)
    assigned_volunteers = task.get('assigned_volunteers', [])
    if task.get('assigned_to') != current_user_id and current_user_id not in assigned_volunteers:
        return jsonify({"message": "Forbidden: Cannot update tasks not assigned to you"}), 403

    data = request.get_json()
    completion_percentage = data.get('completion_percentage')
    
    if completion_percentage is None:
        return jsonify({"message": "Completion percentage is required"}), 400
    
    try:
        completion_percentage = int(completion_percentage)
    except (ValueError, TypeError):
        return jsonify({"message": "Completion percentage must be a number"}), 400
    
    if not (0 <= completion_percentage <= 100):
        return jsonify({"message": "Completion percentage must be between 0 and 100"}), 400

    # Update task completion
    success = db_service.update_task_completion(task_id, completion_percentage)
    if not success:
        return jsonify({"message": "Failed to update task completion"}), 500
    
    # Get updated task
    updated_task = db_service.get_task(task_id)
    
    return jsonify({
        "message": f"Task completion updated to {completion_percentage}%", 
        "task": updated_task
    }), 200



@app.route('/ratings/my', methods=['GET'])
@role_required(['volunteer'])
def volunteer_my_ratings():
    current_user_id = session['user_id']
    my_ratings = db_service.get_ratings(volunteer_id=current_user_id)
    return jsonify(my_ratings), 200

@app.route('/attendance/my', methods=['GET'])
@role_required(['volunteer'])
def volunteer_my_attendance():
    """Get volunteer's personal attendance history"""
    current_user_id = session['user_id']
    
    # Get query parameters for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    event_id = request.args.get('event_id')
    
    try:
        # Get attendance logs
        attendance_logs = db_service.get_attendance_logs(
            user_id=current_user_id, 
            event_id=event_id
        )
        
        # Get absentee logs
        absentee_logs = db_service.get_absentee_logs(
            user_id=current_user_id,
            event_id=event_id
        )
        
        # Filter by date range if provided
        if start_date and end_date:
            attendance_logs = [
                log for log in attendance_logs 
                if start_date <= log.get('date', '') <= end_date
            ]
            absentee_logs = [
                log for log in absentee_logs 
                if start_date <= log.get('date', '') <= end_date
            ]
        
        # Get task information for each record
        all_tasks = db_service.get_all_tasks()
        tasks_dict = {task['task_id']: task for task in all_tasks}
        
        # Combine and format attendance records
        all_records = []
        
        # Add present records
        for log in attendance_logs:
            task = tasks_dict.get(log.get('task_id', ''), {})
            all_records.append({
                'record_id': log.get('log_id'),
                'date': log.get('date'),
                'status': 'Present',
                'task_title': task.get('title', 'N/A'),
                'task_id': log.get('task_id'),
                'event_id': log.get('event_id'),
                'remark': log.get('remark', ''),
                'marked_by': log.get('marked_by'),
                'created_at': log.get('created_at')
            })
        
        # Add absent records
        for log in absentee_logs:
            task = tasks_dict.get(log.get('task_id', ''), {})
            all_records.append({
                'record_id': log.get('log_id'),
                'date': log.get('date'),
                'status': 'Absent',
                'task_title': task.get('title', 'N/A'),
                'task_id': log.get('task_id'),
                'event_id': log.get('event_id'),
                'remark': log.get('remark', ''),
                'marked_by': log.get('marked_by'),
                'created_at': log.get('created_at')
            })
        
        # Sort by date (most recent first)
        all_records.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return jsonify({
            'attendance_records': all_records,
            'total_records': len(all_records),
            'present_count': len(attendance_logs),
            'absent_count': len(absentee_logs)
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching attendance history: {str(e)}"}), 500

@app.route('/profile', methods=['GET'])
@role_required(['volunteer', 'coordinator', 'admin'])
def view_personal_profile():
    current_user_id = session['user_id']
    user_data = db_service.get_user(current_user_id)
    if user_data:
        profile = {k: v for k, v in user_data.items() if k not in ['password']} # Exclude password
        return jsonify(profile), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/profile/update', methods=['PUT'])
@role_required(['volunteer', 'coordinator', 'admin'])
def update_personal_profile():
    current_user_id = session['user_id']
    user_data = db_service.get_user(current_user_id)
    if not user_data:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    update_data = {k: v for k, v in data.items() if k in ['name', 'contact', 'email']} # Allow specific fields to be updated

    # Optional: Password change functionality
    new_password = data.get('new_password')
    if new_password:
        update_data['password'] = new_password # In a real app, hash and salt this!

    db_service.update_user(current_user_id, update_data) # Update in Firebase
    user_data.update(update_data) # Update local copy for response
    return jsonify({"message": "Profile updated successfully", "profile": {k: v for k, v in user_data.items() if k not in ['password']}}), 200

# --- COORDINATOR ROLE ENDPOINTS ---

@app.route('/volunteers', methods=['GET'])
@role_required(['coordinator'])
def get_volunteers():
    volunteers = db_service.get_users_by_role('volunteer')
    volunteer_list = [{"user_id": u['user_id'], "name": u['name'], "email": u['email'], "contact": u.get('contact', '')} for u in volunteers]
    return jsonify(volunteer_list), 200

@app.route('/tasks/assign_volunteer', methods=['POST'])
@role_required(['coordinator'])
def assign_task_to_volunteer():
    data = request.get_json()
    task_id = data.get('task_id')
    volunteer_id = data.get('volunteer_id')
    priority = data.get('priority')
    deadline = data.get('deadline')

    if not all([task_id, volunteer_id]):
        return jsonify({"message": "Task ID and Volunteer ID are required"}), 400

    task = db_service.get_task(task_id)
    volunteer = db_service.get_user(volunteer_id)

    if not task or not volunteer:
        return jsonify({"message": "Invalid Task or Volunteer ID"}), 404
    if volunteer['role'] != 'volunteer':
        return jsonify({"message": "Cannot assign tasks to non-volunteers"}), 403

    update_data = {'assigned_to': volunteer_id}
    if priority:
        update_data['priority'] = priority
    if deadline:
        update_data['deadline'] = deadline

    db_service.update_task(task_id, update_data)
    task.update(update_data)

    return jsonify({"message": "Task assigned successfully", "task": task}), 200

@app.route('/tasks/assign_multiple', methods=['POST'])
@role_required(['coordinator', 'admin'])
def assign_multiple_volunteers():
    """Assign multiple volunteers to a task"""
    data = request.get_json()
    task_id = data.get('task_id')
    volunteer_ids = data.get('volunteer_ids', [])

    if not task_id or not volunteer_ids:
        return jsonify({"message": "Task ID and volunteer IDs are required"}), 400

    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    # Validate all volunteers exist and are volunteers
    for volunteer_id in volunteer_ids:
        volunteer = db_service.get_user(volunteer_id)
        if not volunteer or volunteer['role'] != 'volunteer':
            return jsonify({"message": f"Invalid volunteer ID: {volunteer_id}"}), 400

    success = db_service.assign_multiple_volunteers(task_id, volunteer_ids)
    if success:
        updated_task = db_service.get_task(task_id)
        return jsonify({
            "message": f"Task assigned to {len(volunteer_ids)} volunteers successfully", 
            "task": updated_task
        }), 200
    else:
        return jsonify({"message": "Failed to assign volunteers"}), 500

@app.route('/tasks/add_volunteer', methods=['POST'])
@role_required(['coordinator', 'admin'])
def add_volunteer_to_task():
    """Add a volunteer to an existing task"""
    data = request.get_json()
    task_id = data.get('task_id')
    volunteer_id = data.get('volunteer_id')

    if not task_id or not volunteer_id:
        return jsonify({"message": "Task ID and volunteer ID are required"}), 400

    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    volunteer = db_service.get_user(volunteer_id)
    if not volunteer or volunteer['role'] != 'volunteer':
        return jsonify({"message": "Invalid volunteer ID"}), 400

    success = db_service.add_volunteer_to_task(task_id, volunteer_id)
    if success:
        updated_task = db_service.get_task(task_id)
        return jsonify({
            "message": "Volunteer added to task successfully", 
            "task": updated_task
        }), 200
    else:
        return jsonify({"message": "Failed to add volunteer"}), 500

@app.route('/tasks/remove_volunteer', methods=['POST'])
@role_required(['coordinator', 'admin'])
def remove_volunteer_from_task():
    """Remove a volunteer from a task"""
    data = request.get_json()
    task_id = data.get('task_id')
    volunteer_id = data.get('volunteer_id')

    if not task_id or not volunteer_id:
        return jsonify({"message": "Task ID and volunteer ID are required"}), 400

    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    success = db_service.remove_volunteer_from_task(task_id, volunteer_id)
    if success:
        updated_task = db_service.get_task(task_id)
        return jsonify({
            "message": "Volunteer removed from task successfully", 
            "task": updated_task
        }), 200
    else:
        return jsonify({"message": "Failed to remove volunteer"}), 500

@app.route('/attendance', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_attendance_logs():
    volunteer_id = request.args.get('volunteer_id')
    date_filter = request.args.get('date') # Example: YYYY-MM-DD

    if volunteer_id:
        # Coordinators can only see attendance for volunteers. Admins see all.
        if session['role'] == 'coordinator':
            # In a real system, you'd check if the coordinator "supervises" this volunteer.
            # For this example, we'll assume a coordinator can view any volunteer's attendance.
            volunteer = db_service.get_user(volunteer_id)
            if volunteer and volunteer['role'] != 'volunteer':
                return jsonify({"message": "Coordinators can only view volunteer attendance"}), 403
        attendance_logs = db_service.get_attendance_logs(user_id=volunteer_id, date=date_filter)
        absentee_logs = db_service.get_absentee_logs(user_id=volunteer_id, date=date_filter)
    else:
        attendance_logs = db_service.get_attendance_logs(date=date_filter)
        absentee_logs = db_service.get_absentee_logs(date=date_filter)

    # Get all users for name lookup
    all_users = db_service.get_users_by_role('volunteer') + db_service.get_users_by_role('coordinator')
    user_lookup = {user['user_id']: user['name'] for user in all_users}
    
    # Combine attendance and absentee records
    all_records = []
    
    # Add present records
    for log in attendance_logs:
        user_id = log.get('user_id')
        all_records.append({
            'user_id': user_id,
            'name': user_lookup.get(user_id, user_id),
            'event_id': log.get('event_id'),
            'task_id': log.get('task_id'),
            'date': log.get('date'),
            'status': 'present',
            'remark': log.get('remark', ''),
            'created_at': log.get('created_at'),
            'marked_by': log.get('marked_by')
        })
    
    # Add absent records
    for log in absentee_logs:
        user_id = log.get('user_id')
        all_records.append({
            'user_id': user_id,
            'name': user_lookup.get(user_id, user_id),
            'event_id': log.get('event_id'),
            'task_id': log.get('task_id'),
            'date': log.get('date'),
            'status': 'absent',
            'remark': log.get('remark', ''),
            'created_at': log.get('created_at'),
            'marked_by': log.get('marked_by')
        })

    return jsonify(all_records), 200

@app.route('/ratings/add', methods=['POST'])
@role_required(['coordinator', 'admin'])
def add_rating():
    current_user_id = session['user_id']
    data = request.get_json()
    volunteer_id = data.get('volunteer_id')
    task_id = data.get('task_id')
    score = data.get('score')
    comments = data.get('comments')

    if not all([volunteer_id, task_id, score is not None, comments]):
        return jsonify({"message": "Missing required fields"}), 400
    if not isinstance(score, (int, float)) or not (1 <= score <= 5):
        return jsonify({"message": "Score must be between 1 and 5"}), 400

    volunteer = db_service.get_user(volunteer_id)
    task = db_service.get_task(task_id)

    if not volunteer or volunteer['role'] != 'volunteer':
        return jsonify({"message": "Invalid Volunteer ID"}), 400
    if not task:
        return jsonify({"message": "Invalid Task ID"}), 400

    # Coordinator specific restriction: Cannot rate volunteers not assigned to them
    if session['role'] == 'coordinator':
        # Check if the volunteer is assigned to this task
        if task.get('assigned_to') != volunteer_id:
            return jsonify({"message": "Forbidden: Cannot rate volunteers not assigned to this task"}), 403

    rating_data = {
        "rating_id": f"r{uuid.uuid4().hex[:8]}",
        "volunteer_id": volunteer_id,
        "coordinator_id": current_user_id if session['role'] == 'coordinator' else None, # Only coordinators log this
        "admin_id": current_user_id if session['role'] == 'admin' else None, # Only admins log this
        "task_id": task_id,
        "score": score,
        "comments": comments
    }
    new_rating_id = db_service.create_rating(rating_data)
    return jsonify({"message": "Rating added successfully", "rating_id": new_rating_id}), 201

@app.route('/ratings', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_ratings():
    submitted_by_me = request.args.get('submitted_by')
    volunteer_id_filter = request.args.get('volunteer_id')

    if session['role'] == 'coordinator':
        if submitted_by_me == 'me':
            filtered_ratings = db_service.get_ratings(coordinator_id=session['user_id'])
        elif volunteer_id_filter:
            # Coordinator can only see ratings for volunteers they manage (simple check based on task assignment)
            volunteer_tasks = db_service.get_tasks_by_assignee(volunteer_id_filter)
            valid_task_ids_for_coord = [task['task_id'] for task in volunteer_tasks]
            all_ratings = db_service.get_ratings(volunteer_id=volunteer_id_filter)
            filtered_ratings = [r for r in all_ratings if r.get('task_id') in valid_task_ids_for_coord]
        else:
            # Coordinators can only see ratings they submitted or for volunteers they oversee
            # For simplicity, let's say they can see all ratings, but cannot edit/delete others.
            filtered_ratings = db_service.get_ratings()
    elif session['role'] == 'admin':
        if volunteer_id_filter:
            filtered_ratings = db_service.get_ratings(volunteer_id=volunteer_id_filter)
        else:
            filtered_ratings = db_service.get_ratings()

    return jsonify(filtered_ratings), 200

@app.route('/ratings/<rating_id>', methods=['PUT'])
@role_required(['coordinator', 'admin'])
def update_rating(rating_id):
    current_user_id = session['user_id']
    rating = db_service.get_rating(rating_id)

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    if session['role'] == 'coordinator' and rating.get('coordinator_id') != current_user_id:
        return jsonify({"message": "Forbidden: Cannot edit ratings not submitted by you"}), 403

    data = request.get_json()
    update_data = {}
    if 'score' in data:
        if not isinstance(data['score'], (int, float)) or not (1 <= data['score'] <= 5):
            return jsonify({"message": "Score must be between 1 and 5"}), 400
        update_data['score'] = data['score']
    if 'comments' in data:
        update_data['comments'] = data['comments']

    db_service.update_rating(rating_id, update_data)
    rating.update(update_data)
    return jsonify({"message": "Rating updated successfully", "rating": rating}), 200

@app.route('/expenses', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_expenses():
    task_id = request.args.get('task_id')
    category = request.args.get('category')

    filtered_expenses = db_service.get_expenses(task_id=task_id, category=category)
    return jsonify(filtered_expenses), 200

@app.route('/reports/attendance', methods=['GET'])
@role_required(['coordinator', 'admin'])
def report_attendance():
    # [cite_start]Coordinator: Tabular view of attendance [cite: 8]
    # [cite_start]Admin: All attendance logs [cite: 8]
    if session['role'] == 'coordinator':
        # Coordinators can only see attendance logs, not modify.
        # This endpoint implicitly filters what they can see based on the attendance endpoint logic.
        return get_attendance_logs() # Reusing the attendance endpoint for basic logs
    elif session['role'] == 'admin':
        return get_attendance_logs()
    return jsonify({"message": "Forbidden"}), 403

@app.route('/reports/assignments', methods=['GET'])
@role_required(['coordinator', 'admin'])
def report_assignments():
    # [cite_start]Coordinator: Task assignment history [cite: 8]
    # [cite_start]Admin: Assignment logs per user [cite: 8]
    all_tasks = db_service.get_all_tasks()
    all_users = db_service.get_all_users()
    users_dict = {u['user_id']: u for u in all_users}
    
    assigned_tasks_data = []
    for task in all_tasks:
        if task.get('assigned_to'):
            assignee = users_dict.get(task['assigned_to'])
            assigned_tasks_data.append({
                "task_id": task['task_id'],
                "title": task['title'],
                "assigned_to_id": task['assigned_to'],
                "assigned_to_name": assignee['name'] if assignee else 'Unknown',
                "role": assignee['role'] if assignee else 'Unknown',
                "deadline": task.get('deadline'),
                "priority": task.get('priority'),
                "status": task.get('status')
            })
    return jsonify(assigned_tasks_data), 200

@app.route('/reports/expenses', methods=['GET'])
@role_required(['coordinator', 'admin'])
def report_expenses():
    # [cite_start]Coordinator: Expense list (no budget control) [cite: 8]
    # [cite_start]Admin: Expenses by task, category, budget vs spend list [cite: 8]
    return get_expenses() # Reusing the expenses endpoint for basic expense reports

# --- ADMIN ROLE ENDPOINTS ---

@app.route('/users', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_all_users():
    users_list = db_service.get_all_users()
    # Remove passwords from response
    for user in users_list:
        user.pop('password', None)
    return jsonify(users_list), 200

@app.route('/users/create', methods=['POST'])
@role_required(['admin'])
def create_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    name = data.get('name')
    contact = data.get('contact')

    if not all([email, password, role, name]):
        return jsonify({"message": "Missing required user fields"}), 400

    if role not in ['volunteer', 'coordinator', 'admin']:
        return jsonify({"message": "Invalid role"}), 400

    # Check if email already exists
    existing_user = db_service.get_user_by_email(email)
    if existing_user:
        return jsonify({"message": "User with this email already exists"}), 409

    user_data = {
        "email": email,
        "password": password, # In a real app, hash and salt this!
        "role": role,
        "name": name,
        "contact": contact
    }
    new_user_id = db_service.create_user(user_data)
    return jsonify({"message": "User created successfully", "user_id": new_user_id}), 201

@app.route('/users/<user_id>', methods=['PUT'])
@role_required(['admin'])
def update_user(user_id):
    user = db_service.get_user(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name']
    if 'email' in data:
        update_data['email'] = data['email']
    if 'role' in data:
        if data['role'] in ['volunteer', 'coordinator', 'admin']:
            update_data['role'] = data['role']
        else:
            return jsonify({"message": "Invalid role"}), 400
    if 'password' in data:
        update_data['password'] = data['password'] # Again, hash and salt this!
    if 'contact' in data:
        update_data['contact'] = data['contact']

    db_service.update_user(user_id, update_data)
    user.update(update_data)
    return jsonify({"message": "User updated successfully", "user": {k: v for k, v in user.items() if k not in ['password']}}), 200

@app.route('/users/<user_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_user(user_id):
    user = db_service.get_user(user_id)
    if user:
        db_service.delete_user(user_id)
        # In a real app, you'd also delete associated data (tasks, attendance, ratings, etc.)
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/tasks/create', methods=['POST'])
@role_required(['admin', 'coordinator'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline')
    priority = data.get('priority')
    assigned_to = data.get('assigned_to') # Optional, can be assigned later
    assigned_volunteers = data.get('assigned_volunteers', []) # Multiple volunteers

    if not all([title, description, deadline, priority]):
        return jsonify({"message": "Missing required task fields"}), 400

    # Validate assigned_to if provided
    if assigned_to:
        user = db_service.get_user(assigned_to)
        if not user or user['role'] not in ['volunteer', 'coordinator']:
            assigned_to = None

    # Validate assigned_volunteers if provided
    if assigned_volunteers:
        valid_volunteers = []
        for volunteer_id in assigned_volunteers:
            user = db_service.get_user(volunteer_id)
            if user and user['role'] == 'volunteer':
                valid_volunteers.append(volunteer_id)
        assigned_volunteers = valid_volunteers

    # Set assigned_to to first volunteer for backward compatibility
    if assigned_volunteers and not assigned_to:
        assigned_to = assigned_volunteers[0]

    task_data = {
        "title": title,
        "description": description,
        "deadline": deadline,
        "priority": priority,
        "status": "Pending",
        "assigned_to": assigned_to,
        "assigned_volunteers": assigned_volunteers
    }
    new_task_id = db_service.create_task(task_data)
    return jsonify({"message": "Task created successfully", "task_id": new_task_id}), 201

@app.route('/tasks/assign', methods=['POST'])
@role_required(['admin'])
def admin_assign_task():
    # Admin can assign tasks to both coordinators and volunteers
    data = request.get_json()
    task_id = data.get('task_id')
    assignee_id = data.get('assignee_id')

    task = db_service.get_task(task_id)
    assignee = db_service.get_user(assignee_id)

    if not task or not assignee:
        return jsonify({"message": "Invalid Task or Assignee ID"}), 404
    if assignee['role'] not in ['volunteer', 'coordinator']:
        return jsonify({"message": "Cannot assign tasks to this role"}), 400

    db_service.update_task(task_id, {'assigned_to': assignee_id})
    task['assigned_to'] = assignee_id
    return jsonify({"message": "Task assigned successfully by admin", "task": task}), 200

@app.route('/tasks', methods=['GET'])
@role_required(['coordinator', 'admin'])  # Add 'admin' if you want admins to see all tasks
def get_all_tasks():
    status_filter = request.args.get('status')
    if status_filter:
        all_tasks = db_service.get_tasks_by_status(status_filter)
    else:
        all_tasks = db_service.get_all_tasks()
    return jsonify(all_tasks), 200


@app.route('/tasks/<task_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_task(task_id):
    task = db_service.get_task(task_id)
    if task:
        db_service.delete_task(task_id)
        return jsonify({"message": "Task deleted successfully"}), 200
    return jsonify({"message": "Task not found"}), 404

# --- Absentees tracking ---

@app.route('/attendance/absentees', methods=['GET'])
@role_required(['admin'])
def get_absentees():
    today_date = datetime.now().strftime("%Y-%m-%d")
    # Get all users who are volunteers or coordinators and have an assigned task
    all_users = db_service.get_users_by_role('volunteer') + db_service.get_users_by_role('coordinator')
    all_tasks = db_service.get_all_tasks()
    assigned_users = {task['assigned_to'] for task in all_tasks if task.get('assigned_to')}
    relevant_users = [u for u in all_users if u['user_id'] in assigned_users]
    
    # Who logged attendance today?
    attendance_today = db_service.get_attendance_logs(date=today_date)
    users_who_logged_today = {log['user_id'] for log in attendance_today}
    
    # Who is marked absent today?
    absentees_today = db_service.get_absentee_logs(date=today_date)
    users_marked_absent_today = {log['user_id'] for log in absentees_today}
    
    # Absentees: assigned users who neither logged attendance nor were marked absent
    absentees = []
    for user in relevant_users:
        uid = user['user_id']
        if uid not in users_who_logged_today and uid not in users_marked_absent_today:
            absentees.append({
                "user_id": uid,
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            })
    return jsonify(absentees), 200

@app.route('/attendance/mark_absent', methods=['POST'])
@role_required(['admin', 'coordinator'])
def mark_user_absent():
    data = request.get_json()
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
    if not user_id or not task_id:
        return jsonify({"message": "User ID and Task ID are required."}), 400
    user = db_service.get_user(user_id)
    if not user:
        return jsonify({"message": "Invalid User ID."}), 400
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Invalid Task ID."}), 400
    # Prevent duplicate absent marking for same user, task, date
    if db_service.check_absentee_exists(user_id, task_id, date):
        return jsonify({"message": "User already marked absent for this task and date."}), 409
    new_log_id = db_service.create_absentee_log({"log_id": f"abs{uuid.uuid4().hex[:8]}", "user_id": user_id, "task_id": task_id, "date": date})
    return jsonify({"message": "User marked absent successfully", "log_id": new_log_id}), 201

@app.route('/ratings/<rating_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_rating(rating_id):
    rating = db_service.get_rating(rating_id)
    if rating:
        db_service.delete_rating(rating_id)
        return jsonify({"message": "Rating deleted successfully"}), 200
    return jsonify({"message": "Rating not found"}), 404

@app.route('/expenses/log', methods=['POST'])
@role_required(['admin', 'coordinator'])
def log_expense():
    data = request.get_json()
    task_id = data.get('task_id')
    amount = data.get('amount')
    category = data.get('category')

    if not all([task_id, amount, category]):
        return jsonify({"message": "Missing required expense fields"}), 400
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Invalid Task ID"}), 400

    expense_data = {
        "expense_id": f"e{uuid.uuid4().hex[:8]}",
        "task_id": task_id,
        "amount": amount,
        "category": category,
        "logged_by": session['user_id']
    }
    new_expense_id = db_service.create_expense(expense_data)
    return jsonify({"message": "Expense logged successfully", "expense_id": new_expense_id}), 201

@app.route('/expenses/<expense_id>', methods=['PUT'])
@role_required(['admin', 'coordinator'])  # Add 'coordinator' here
def update_expense(expense_id):
    # Optionally, add logic to restrict which expenses a coordinator can edit
    expense = db_service.get_expense(expense_id)
    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    data = request.get_json()
    update_data = {}
    if 'amount' in data:
        update_data['amount'] = data['amount']
    if 'category' in data:
        update_data['category'] = data['category']
    if 'task_id' in data:
        update_data['task_id'] = data['task_id']

    db_service.update_expense(expense_id, update_data)
    expense.update(update_data)
    return jsonify({"message": "Expense updated successfully", "expense": expense}), 200

@app.route('/expenses/<expense_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_expense(expense_id):
    expense = db_service.get_expense(expense_id)
    if expense:
        db_service.delete_expense(expense_id)
        return jsonify({"message": "Expense deleted successfully"}), 200
    return jsonify({"message": "Expense not found"}), 404

# --- ADMIN REPORTS ---

@app.route('/reports/tasks', methods=['GET'])
@role_required(['admin'])
def admin_report_tasks():
    # [cite_start]Task summary (assigned, completed, overdue) [cite: 8]
    all_tasks = db_service.get_all_tasks()
    summary = {
        "total_tasks": len(all_tasks),
        "pending": sum(1 for t in all_tasks if t['status'] == 'Pending'),
        "in_progress": sum(1 for t in all_tasks if t['status'] == 'In Progress'),
        "completed": sum(1 for t in all_tasks if t['status'] == 'Completed'),
        "overdue": sum(1 for t in all_tasks if t['status'] != 'Completed' and datetime.now().date() > datetime.strptime(t['deadline'], "%Y-%m-%d").date())
    }
    return jsonify(summary), 200

@app.route('/reports/ratings', methods=['GET'])
@role_required(['admin'])
def admin_report_ratings():
    # [cite_start]Ratings and feedback summary [cite: 8]
    all_ratings = db_service.get_ratings()
    all_users = db_service.get_all_users()
    users_dict = {u['user_id']: u for u in all_users}
    
    rating_summary = {}
    for r in all_ratings:
        vol_id = r['volunteer_id']
        if vol_id not in rating_summary:
            rating_summary[vol_id] = {"total_score": 0, "count": 0, "comments": []}
        rating_summary[vol_id]["total_score"] += r['score']
        rating_summary[vol_id]["count"] += 1
        rating_summary[vol_id]["comments"].append(r['comments'])

    for vol_id, data in rating_summary.items():
        data['average_score'] = data['total_score'] / data['count']
        data['volunteer_name'] = users_dict.get(vol_id, {}).get('name', 'Unknown')

    return jsonify(rating_summary), 200

@app.route('/register', methods=['POST'])
def register_volunteer():
    """Register user with email/password or Google Auth"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    contact = data.get('contact')
    role = data.get('role', 'volunteer')
    id_token = data.get('id_token')  # For Google Auth
    provider = data.get('provider', 'email')  # 'email' or 'google'

    # Validate role
    if role not in ['volunteer', 'coordinator']:
        return jsonify({"message": "Invalid role. Must be 'volunteer' or 'coordinator'"}), 400

    # Check if email already exists
    existing_user = db_service.get_user_by_email(email)
    if existing_user:
        return jsonify({"message": "User with this email already exists"}), 409

    if provider == 'google' and id_token:
        # Google Auth registration
        user_info = firebase_auth_service.verify_google_token(id_token)
        if not user_info:
            return jsonify({"message": "Invalid Google token"}), 401
        
        user_data = {
            "email": email,
            "name": user_info.get('name', name),
            "contact": contact,
            "role": role,
            "provider": "google",
            "firebase_uid": user_info.get('uid'),
            "profile_picture": user_info.get('picture', ''),
            "email_verified": user_info.get('email_verified', False)
        }
    else:
        # Email/password registration
        if not all([email, password, name]):
            return jsonify({"message": "Missing required fields for email registration"}), 400
        
        user_data = {
            "email": email,
            "password": password,  # In a real app, hash and salt this!
            "role": role,
            "name": name,
            "contact": contact,
            "provider": "email"
        }

    new_user_id = db_service.create_user(user_data)
    user = db_service.get_user(new_user_id)
    
    # Create session for immediate login
    session['user_id'] = new_user_id
    session['role'] = role
    session['provider'] = provider
    
    # Generate JWT token
    token_payload = {
        'user_id': new_user_id,
        'role': role,
        'provider': provider,
        'exp': datetime.utcnow().timestamp() + 3600  # 1 hour expiry
    }
    token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
    
    return jsonify({
        "message": f"{role.capitalize()} registered successfully", 
        "user_id": new_user_id,
        "role": role,
        "redirect_to": "/dashbords",
        "token": token,
        "user": {
            "user_id": new_user_id,
            "name": user['name'],
            "email": user['email'],
            "role": role,
            "profile_picture": user.get('profile_picture', '')
        }
    }), 201

@app.route('/dashboard/volunteer', methods=['GET'])
@role_required(['volunteer'])
def volunteer_dashboard_summary():
    current_user_id = session['user_id']
    user = db_service.get_user(current_user_id)
    # Attendance %
    my_tasks = db_service.get_tasks_by_assignee(current_user_id)
    total_tasks = len(my_tasks)
    attendance_logs = db_service.get_attendance_logs(user_id=current_user_id)
    attended = len(attendance_logs)
    attendance_percent = int((attended / total_tasks) * 100) if total_tasks else 0
    # Average rating
    my_ratings = db_service.get_ratings(volunteer_id=current_user_id)
    avg_rating = round(sum(r['score'] for r in my_ratings) / len(my_ratings), 2) if my_ratings else 0
    # Tasks with ratings
    for task in my_tasks:
        task_ratings = [r for r in my_ratings if r['task_id'] == task['task_id']]
        task['rating'] = task_ratings[0]['score'] if task_ratings else None
    # Team (other volunteers, fake for now)
    team = [
        {"name": "Jane Cooper", "email": "jgraham@example.com", "location": "Toledo", "amount": 10483},
        {"name": "Devon Lane", "email": "dat.roberts@example.com", "location": "New York", "amount": 11159},
        {"name": "curtis_d@example.com", "location": "Naperville", "amount": 9084}
    ]
    return jsonify({
        "name": user['name'],
        "attendance_percent": attendance_percent,
        "average_rating": avg_rating,
        "tasks": my_tasks,
        "team": team
    })

@app.route('/dashboard/coordinator', methods=['GET'])
@role_required(['coordinator'])
def coordinator_dashboard_summary():
    current_user_id = session['user_id']
    user = db_service.get_user(current_user_id)
    # Volunteers managed (all volunteers for now)
    volunteers = db_service.get_users_by_role('volunteer')
    volunteer_ids = [v['user_id'] for v in volunteers]
    # Attendance % (average of their volunteers)
    attendance_percents = []
    for volunteer in volunteers:
        vid = volunteer['user_id']
        total_tasks = len(db_service.get_tasks_by_assignee(vid))
        attended = len(db_service.get_attendance_logs(user_id=vid))
        percent = int((attended / total_tasks) * 100) if total_tasks else 0
        attendance_percents.append(percent)
    avg_attendance = int(sum(attendance_percents) / len(attendance_percents)) if attendance_percents else 0
    # Average rating (of their volunteers)
    volunteer_ratings = db_service.get_ratings()
    volunteer_ratings = [r for r in volunteer_ratings if r.get('volunteer_id') in volunteer_ids]
    avg_rating = round(sum(r['score'] for r in volunteer_ratings) / len(volunteer_ratings), 2) if volunteer_ratings else 0
    # Tasks assigned
    assigned_tasks = []
    all_tasks = db_service.get_all_tasks()
    for task in all_tasks:
        if task.get('assigned_to') in volunteer_ids:
            # Attach rating if exists
            task_ratings = [r for r in volunteer_ratings if r['volunteer_id'] == task['assigned_to'] and r['task_id'] == task['task_id']]
            task['rating'] = task_ratings[0]['score'] if task_ratings else None
            assigned_tasks.append(task)
    # Team (volunteers)
    team = [{"name": v['name'], "email": v['email'], "location": "", "amount": 0} for v in volunteers]
    return jsonify({
        "name": user['name'],
        "attendance_percent": avg_attendance,
        "average_rating": avg_rating,
        "tasks": assigned_tasks,
        "team": team
    })

@app.route('/dashboard/admin', methods=['GET'])
@role_required(['admin'])
def admin_dashboard_summary():
    user = db_service.get_user(session['user_id'])
    # Attendance % (average of all volunteers)
    volunteers = db_service.get_users_by_role('volunteer')
    volunteer_ids = [v['user_id'] for v in volunteers]
    attendance_percents = []
    for volunteer in volunteers:
        vid = volunteer['user_id']
        total_tasks = len(db_service.get_tasks_by_assignee(vid))
        attended = len(db_service.get_attendance_logs(user_id=vid))
        percent = int((attended / total_tasks) * 100) if total_tasks else 0
        attendance_percents.append(percent)
    avg_attendance = int(sum(attendance_percents) / len(attendance_percents)) if attendance_percents else 0
    # Average rating (all volunteers)
    volunteer_ratings = db_service.get_ratings()
    volunteer_ratings = [r for r in volunteer_ratings if r.get('volunteer_id') in volunteer_ids]
    avg_rating = round(sum(r['score'] for r in volunteer_ratings) / len(volunteer_ratings), 2) if volunteer_ratings else 0
    # All tasks
    all_tasks = db_service.get_all_tasks()
    for task in all_tasks:
        # Attach rating if exists
        task_ratings = [r for r in volunteer_ratings if r['volunteer_id'] == task.get('assigned_to') and r['task_id'] == task['task_id']]
        task['rating'] = task_ratings[0]['score'] if task_ratings else None
    # Team (all users)
    all_users = db_service.get_all_users()
    team = [{"name": u['name'], "email": u['email'], "location": "", "amount": 0} for u in all_users]
    return jsonify({
        "name": user['name'],
        "attendance_percent": avg_attendance,
        "average_rating": avg_rating,
        "tasks": all_tasks,
        "team": team
    })


# --- FILTER ENDPOINTS FOR UI ---

@app.route('/attendance/filter', methods=['GET'])
@role_required(['admin', 'coordinator'])
def filter_attendance():
    user_id = request.args.get('user_id')
    task_id = request.args.get('task_id')
    date = request.args.get('date')
    event_id = request.args.get('event_id')
    filtered = db_service.get_attendance_logs(user_id=user_id, task_id=task_id, date=date, event_id=event_id)
    return jsonify(filtered), 200

@app.route('/attendance/filter/simple', methods=['GET'])
@role_required(['admin', 'coordinator'])
def simple_attendance_filter():
    """Simple attendance filter for event and status"""
    try:
        event_id = request.args.get('event_id')
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        print(f"Filter request: event_id={event_id}, user_id={user_id}, status={status}")
        
        # For user-based filtering, we need user_id
        if not user_id and not event_id:
            return jsonify({"message": "Either user_id or event_id is required"}), 400
        
        # Get attendance logs
        if start_date and end_date:
            attendance_logs = db_service.get_attendance_by_date_range(start_date, end_date, event_id) or []
            # Filter by user_id if provided
            if user_id:
                attendance_logs = [log for log in attendance_logs if log.get('user_id') == user_id]
        else:
            attendance_logs = db_service.get_attendance_logs(event_id=event_id, user_id=user_id) or []
        
        # Get absentee logs (simplified for now)
        absentee_logs = db_service.get_absentee_logs(event_id=event_id, user_id=user_id) or []
        
        print(f"Found {len(attendance_logs)} attendance logs and {len(absentee_logs)} absentee logs")
        
        # Get all users for name lookup
        if user_id:
            # Get specific user
            user = db_service.get_user(user_id)
            users = [user] if user else []
        else:
            # Get all volunteers and coordinators
            volunteer_users = db_service.get_users_by_role('volunteer') or []
            coordinator_users = db_service.get_users_by_role('coordinator') or []
            users = volunteer_users + coordinator_users
        
        # Create user lookup
        user_lookup = {user['user_id']: user['name'] for user in users if user}
        
        # Process results
        results = []
        
        # Add present records
        for log in attendance_logs:
            user_id = log.get('user_id')
            if user_id in user_lookup:
                results.append({
                    'user_id': user_id,
                    'name': user_lookup[user_id],
                    'event_id': log.get('event_id'),
                    'task_id': log.get('task_id'),
                    'date': log.get('date'),
                    'status': 'present',
                    'remark': log.get('remark', ''),
                    'created_at': log.get('created_at'),
                    'submission_time': log.get('created_at'),
                    'marked_by': log.get('marked_by')
                })
        
        # Add absent records
        for log in absentee_logs:
            user_id = log.get('user_id')
            if user_id in user_lookup:
                results.append({
                    'user_id': user_id,
                    'name': user_lookup[user_id],
                    'event_id': log.get('event_id'),
                    'task_id': log.get('task_id'),
                    'date': log.get('date'),
                    'status': 'absent',
                    'remark': log.get('remark', ''),
                    'created_at': log.get('created_at'),
                    'submission_time': log.get('created_at'),
                    'marked_by': log.get('marked_by')
                })
        
        # Filter by status if provided
        if status:
            results = [r for r in results if r['status'] == status]
        
        print(f"Returning {len(results)} filtered results")
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Filter error: {str(e)}")
        return jsonify({"message": f"Filter error: {str(e)}"}), 500

@app.route('/expenses/filter', methods=['GET'])
@role_required(['admin', 'coordinator'])
def filter_expenses():
    task_id = request.args.get('task_id')
    category = request.args.get('category')
    date = request.args.get('date')
    filtered = db_service.get_expenses(task_id=task_id, category=category)
    # Note: date filtering would need to be added to the database service if needed
    return jsonify(filtered), 200

@app.route('/ratings/filter', methods=['GET'])
@role_required(['admin', 'coordinator'])
def filter_ratings():
    volunteer_id = request.args.get('volunteer_id')
    task_id = request.args.get('task_id')
    score = request.args.get('score')
    comments = request.args.get('comments')
    filtered = db_service.get_ratings(volunteer_id=volunteer_id, task_id=task_id)
    if score:
        try:
            score_val = int(score)
            filtered = [r for r in filtered if r['score'] == score_val]
        except:
            pass
    if comments:
        filtered = [r for r in filtered if comments.lower() in r.get('comments', '').lower()]
    return jsonify(filtered), 200

@app.route('/users/filter', methods=['GET'])
@role_required(['admin'])
def filter_users():
    role = request.args.get('role')
    name = request.args.get('name')
    if role:
        filtered = db_service.get_users_by_role(role)
    else:
        filtered = db_service.get_all_users()
    if name:
        filtered = [u for u in filtered if name.lower() in u['name'].lower()]
    # Remove password from output
    for u in filtered:
        u.pop('password', None)
    return jsonify(filtered), 200

@app.route('/tasks/filter', methods=['GET'])
@role_required(['admin', 'coordinator'])
def filter_tasks():
    status = request.args.get('status')
    priority = request.args.get('priority')
    assigned_to = request.args.get('assigned_to')
    
    if status:
        filtered = db_service.get_tasks_by_status(status)
    else:
        filtered = db_service.get_all_tasks()
    
    if priority:
        filtered = [t for t in filtered if t.get('priority') == priority]
    if assigned_to:
        filtered = [t for t in filtered if t.get('assigned_to') == assigned_to]
    
    return jsonify(filtered), 200

@app.route('/volunteers/filter', methods=['GET'])
@role_required(['admin', 'coordinator'])
def filter_volunteers():
    role = request.args.get('role')
    volunteers = db_service.get_users_by_role('volunteer')
    filtered = []
    for u in volunteers:
        if role and u['role'] != role:
            continue
        filtered.append({
            'user_id': u['user_id'],
            'name': u['name'],
            'email': u['email'],
            'contact': u.get('contact', ''),
            'role': u['role']
        })
    return jsonify(filtered), 200

# --- ENHANCED ATTENDANCE MANAGEMENT ENDPOINTS ---

# Event Management
@app.route('/events', methods=['GET'])
@role_required(['admin', 'coordinator', 'volunteer'])
def get_events():
    """Get all events"""
    try:
        print("DEBUG: Getting events...")
        events = db_service.get_all_events()
        print(f"DEBUG: Found {len(events)} events")
        return jsonify(events), 200
    except Exception as e:
        print(f"DEBUG: Error in get_events: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/events', methods=['POST'])
@role_required(['admin', 'coordinator'])
def create_event():
    """Create a new event"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    location = data.get('location', '')
    
    if not all([title, description, start_date, end_date]):
        return jsonify({"message": "Missing required event fields"}), 400
    
    event_data = {
        "title": title,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "location": location,
        "created_by": session['user_id']
    }
    
    event_id = db_service.create_event(event_data)
    return jsonify({"message": "Event created successfully", "event_id": event_id}), 201

@app.route('/events/<event_id>', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_event(event_id):
    """Get specific event"""
    event = db_service.get_event(event_id)
    if event:
        return jsonify(event), 200
    return jsonify({"message": "Event not found"}), 404

# Group Management
@app.route('/groups', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_groups():
    """Get all groups"""
    groups = db_service.get_all_groups()
    return jsonify(groups), 200

@app.route('/groups', methods=['POST'])
@role_required(['admin', 'coordinator'])
def create_group():
    """Create a new group"""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"message": "Group name is required"}), 400
    
    group_data = {
        "name": name,
        "description": description,
        "created_by": session['user_id']
    }
    
    group_id = db_service.create_group(group_data)
    return jsonify({"message": "Group created successfully", "group_id": group_id}), 201

# Enhanced Attendance Management
@app.route('/attendance/test', methods=['GET'])
@role_required(['admin', 'coordinator'])
def test_attendance_system():
    """Test endpoint to verify attendance system is working"""
    try:
        # Test database connection
        users = db_service.get_users_by_role('volunteer')
        tasks = db_service.get_all_tasks()
        
        return jsonify({
            "status": "working",
            "volunteers_count": len(users),
            "tasks_count": len(tasks),
            "message": "Attendance system is operational"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Attendance system error: {str(e)}"
        }), 500

@app.route('/attendance/users', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_users_for_attendance():
    """Get users for bulk attendance marking"""
    try:
        role_filter = request.args.get('role', 'volunteer')
        event_id = request.args.get('event_id')
        
        if role_filter not in ['volunteer', 'coordinator', 'all']:
            return jsonify({"message": "Invalid role filter"}), 400
        
        if role_filter == 'all':
            users = db_service.get_all_users()
        else:
            users = db_service.get_users_by_role(role_filter)
        
        # Filter out admin users for attendance
        users = [user for user in users if user.get('role') != 'admin']
        
        # Format for frontend
        formatted_users = []
        for user in users:
            formatted_users.append({
                "user_id": user['user_id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role'],
                "contact": user.get('contact', '')
            })
        
        return jsonify({
            "users": formatted_users,
            "total": len(formatted_users)
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching users: {str(e)}"}), 500

@app.route('/attendance/bulk', methods=['POST'])
@role_required(['admin', 'coordinator'])
def bulk_mark_attendance():
    """Bulk mark attendance for multiple users"""
    try:
        data = request.get_json()
        attendance_records = data.get('attendance_records', [])
        event_id = data.get('event_id')  # Can be None for daily attendance
        date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
        remark = data.get('remark', '')  # Optional remark/task description
        default_mode = data.get('default_mode', 'present')  # 'present' or 'absent'
        
        if not attendance_records:
            return jsonify({"message": "No attendance records provided"}), 400
        
        if not date:
            return jsonify({"message": "Date is required for bulk attendance marking"}), 400
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Process attendance records
        processed_records = []
        absentee_records = []
        invalid_records = []
        
        for i, record in enumerate(attendance_records):
            user_id = record.get('user_id')
            status = record.get('status', default_mode)
            task_id = record.get('task_id', '')
            
            if not user_id:
                invalid_records.append(f"Record {i+1}: Missing user_id")
                continue
            
            # Validate user exists
            user = db_service.get_user(user_id)
            if not user:
                invalid_records.append(f"Record {i+1}: Invalid user_id {user_id}")
                continue
            
            # Validate task if provided
            if task_id:
                task = db_service.get_task(task_id)
                if not task:
                    invalid_records.append(f"Record {i+1}: Invalid task_id {task_id}")
                    continue
            
            if status == 'present':
                attendance_data = {
                    "log_id": f"att{uuid.uuid4().hex[:8]}",
                    "user_id": user_id,
                    "task_id": task_id,
                    "event_id": event_id,
                    "date": date,
                    "status": status,
                    "remark": remark,
                    "marked_by": session['user_id'],
                    "created_at": datetime.now()
                }
                processed_records.append(attendance_data)
            elif status == 'absent':
                # Create absentee log instead
                absentee_data = {
                    "log_id": f"abs{uuid.uuid4().hex[:8]}",
                    "user_id": user_id,
                    "task_id": task_id,
                    "event_id": event_id,
                    "date": date,
                    "remark": remark,
                    "marked_by": session['user_id'],
                    "created_at": datetime.now()
                }
                absentee_records.append(absentee_data)
            else:
                invalid_records.append(f"Record {i+1}: Invalid status '{status}'. Must be 'present' or 'absent'")
        
        # Process present records
        created_ids = []
        if processed_records:
            created_ids = db_service.bulk_mark_attendance(processed_records)
        
        # Process absent records
        absent_ids = []
        for absentee_data in absentee_records:
            absent_id = db_service.create_absentee_log(absentee_data)
            if absent_id:
                absent_ids.append(absent_id)
        
        total_processed = len(created_ids) + len(absent_ids)
        
        response_data = {
            "message": f"Bulk attendance processed successfully. {len(created_ids)} present, {len(absent_ids)} absent records created.",
            "created_ids": created_ids,
            "absent_ids": absent_ids,
            "total_processed": total_processed,
            "total_records": len(attendance_records)
        }
        
        if invalid_records:
            response_data["invalid_records"] = invalid_records
            response_data["message"] += f" {len(invalid_records)} records had errors."
        
        if total_processed > 0:
            return jsonify(response_data), 201
        else:
            return jsonify({
                "message": "No valid attendance records to process",
                "invalid_records": invalid_records
            }), 400
            
    except Exception as e:
        return jsonify({"message": f"Error processing bulk attendance: {str(e)}"}), 500


@app.route('/attendance/insights', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_attendance_insights():
    """Get attendance insights and statistics"""
    try:
        event_id = request.args.get('event_id')
        date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
        group_id = request.args.get('group_id')
        
        print(f"Getting attendance insights: event_id={event_id}, date={date}, group_id={group_id}")
        
        insights = db_service.get_attendance_insights(event_id=event_id, date=date, group_id=group_id)
        
        print(f"Insights data: {insights}")
        
        return jsonify(insights), 200
    except Exception as e:
        print(f"Error getting attendance insights: {str(e)}")
        return jsonify({"message": f"Error getting insights: {str(e)}"}), 500

@app.route('/attendance/absentees', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_absentee_list():
    """Get list of absentees"""
    event_id = request.args.get('event_id')
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    group_id = request.args.get('group_id')
    
    absentees = db_service.get_absentee_list(event_id=event_id, date=date, group_id=group_id)
    return jsonify(absentees), 200

@app.route('/attendance/date-range', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_attendance_by_date_range():
    """Get attendance records within a date range"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    event_id = request.args.get('event_id')
    
    if not start_date or not end_date:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    attendance_records = db_service.get_attendance_by_date_range(start_date, end_date, event_id)
    return jsonify(attendance_records), 200

@app.route('/attendance/sessions', methods=['GET'])
@role_required(['admin', 'coordinator'])
def get_attendance_sessions():
    """Get attendance sessions"""
    event_id = request.args.get('event_id')
    date = request.args.get('date')
    
    sessions = db_service.get_attendance_sessions(event_id=event_id, date=date)
    return jsonify(sessions), 200

@app.route('/attendance/sessions', methods=['POST'])
@role_required(['admin', 'coordinator'])
def create_attendance_session():
    """Create an attendance session for bulk marking"""
    data = request.get_json()
    event_id = data.get('event_id')
    date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
    title = data.get('title', f"Attendance Session - {date}")
    description = data.get('description', '')
    
    if not event_id:
        return jsonify({"message": "Event ID is required"}), 400
    
    session_data = {
        "event_id": event_id,
        "date": date,
        "title": title,
        "description": description,
        "created_by": session['user_id'],
        "status": "active"
    }
    
    session_id = db_service.create_attendance_session(session_data)
    return jsonify({
        "message": "Attendance session created successfully",
        "session_id": session_id
    }), 201

# Enhanced filtering endpoints
@app.route('/attendance/filter/advanced', methods=['GET'])
@role_required(['admin', 'coordinator'])
def advanced_attendance_filter():
    """Advanced attendance filtering with multiple criteria"""
    try:
        event_id = request.args.get('event_id')
        group_id = request.args.get('group_id')
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')  # 'present', 'absent', 'unmarked'
        user_name = request.args.get('user_name')
        
        # Get base data
        if group_id:
            users = db_service.get_users_by_group(group_id) or []
        elif user_id:
            # Filter by specific user
            volunteer_users = db_service.get_users_by_role('volunteer') or []
            coordinator_users = db_service.get_users_by_role('coordinator') or []
            all_users = volunteer_users + coordinator_users
            users = [u for u in all_users if u['user_id'] == user_id]
        else:
            # Get all non-admin users for filtering
            volunteer_users = db_service.get_users_by_role('volunteer') or []
            coordinator_users = db_service.get_users_by_role('coordinator') or []
            users = volunteer_users + coordinator_users
        
        # Filter by user name if provided
        if user_name:
            users = [u for u in users if user_name.lower() in u['name'].lower()]
        
        # Get attendance data
        if start_date and end_date:
            attendance_logs = db_service.get_attendance_by_date_range(start_date, end_date, event_id) or []
        else:
            attendance_logs = db_service.get_attendance_logs(event_id=event_id) or []
        
        # Get absentee data
        if start_date and end_date:
            absentee_logs = []
            # Would need to implement date range filtering for absentees
        else:
            absentee_logs = db_service.get_absentee_logs(event_id=event_id) or []
        
        # Process results
        results = []
        for user in users:
            user_id = user['user_id']
            user_attendance = [log for log in attendance_logs if log['user_id'] == user_id]
            user_absent = [log for log in absentee_logs if log['user_id'] == user_id]
            
            if status == 'present' and not user_attendance:
                continue
            elif status == 'absent' and not user_absent:
                continue
            elif status == 'unmarked' and (user_attendance or user_absent):
                continue
            
            # Get the most recent date and submission time for this user
            latest_date = None
            submission_time = None
            if user_attendance:
                latest_log = max(user_attendance, key=lambda x: x.get('date', ''))
                latest_date = latest_log.get('date', '')
                created_at = latest_log.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        submission_time = created_at
                    else:
                        submission_time = created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif user_absent:
                latest_log = max(user_absent, key=lambda x: x.get('date', ''))
                latest_date = latest_log.get('date', '')
                created_at = latest_log.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        submission_time = created_at
                    else:
                        submission_time = created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get remark from the latest record
            latest_remark = None
            if user_attendance:
                latest_remark = latest_log.get('remark', '')
            elif user_absent:
                latest_remark = latest_log.get('remark', '')
            
            results.append({
                'user_id': user_id,
                'name': user['name'],
                'email': user['email'],
                'attendance_count': len(user_attendance),
                'absent_count': len(user_absent),
                'status': 'present' if user_attendance else ('absent' if user_absent else 'unmarked'),
                'date': latest_date,
                'submission_time': submission_time,
                'remark': latest_remark
            })
        
        print(f"Filter results: {len(results)} records found")
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Error in advanced_attendance_filter: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- ANNOUNCEMENT MANAGEMENT ENDPOINTS ---

@app.route('/announcements', methods=['GET'])
@role_required(['coordinator', 'admin', 'volunteer'])
def get_announcements():
    """Get all announcements"""
    try:
        print("DEBUG: Getting announcements...")
        event_id = request.args.get('event_id')
        creator_id = request.args.get('creator_id')
        
        if event_id:
            announcements = db_service.get_announcements_by_event(event_id)
        elif creator_id:
            announcements = db_service.get_announcements_by_creator(creator_id)
        else:
            announcements = db_service.get_all_announcements()
        
        print(f"DEBUG: Found {len(announcements)} announcements")
        
        # Sort by creation date (newest first)
        announcements.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify(announcements), 200
    except Exception as e:
        print(f"DEBUG: Error in get_announcements: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/announcements', methods=['POST'])
@role_required(['coordinator', 'admin'])
def create_announcement():
    """Create a new announcement"""
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    event_id = data.get('event_id')
    priority = data.get('priority', 'normal')  # low, normal, high, urgent
    target_audience = data.get('target_audience', 'all')  # all, volunteers, coordinators, specific
    selected_users = data.get('selected_users')  # List of user IDs for specific audience
    
    if not all([title, content]):
        return jsonify({"message": "Title and content are required"}), 400
    
    # Validate event_id if provided
    if event_id:
        event = db_service.get_event(event_id)
        if not event:
            return jsonify({"message": "Invalid event ID"}), 400
    
    # Validate priority
    if priority not in ['low', 'normal', 'high', 'urgent']:
        priority = 'normal'
    
    # Validate target audience
    if target_audience not in ['all', 'volunteers', 'coordinators', 'specific']:
        target_audience = 'all'
    
    # Validate selected users if specific audience
    if target_audience == 'specific':
        if not selected_users or len(selected_users) == 0:
            return jsonify({"message": "Please select at least one user for specific audience"}), 400
        
        # Validate that all selected users exist
        for user_id in selected_users:
            user = db_service.get_user(user_id)
            if not user:
                return jsonify({"message": f"User {user_id} not found"}), 400
    
    announcement_data = {
        "title": title,
        "content": content,
        "event_id": event_id,
        "priority": priority,
        "target_audience": target_audience,
        "selected_users": selected_users if target_audience == 'specific' else None,
        "created_by": session['user_id'],
        "status": "active"  # active, archived
    }
    
    announcement_id = db_service.create_announcement(announcement_data)
    return jsonify({
        "message": "Announcement created successfully", 
        "announcement_id": announcement_id
    }), 201

@app.route('/announcements/<announcement_id>', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_announcement(announcement_id):
    """Get specific announcement"""
    announcement = db_service.get_announcement(announcement_id)
    if announcement:
        return jsonify(announcement), 200
    return jsonify({"message": "Announcement not found"}), 404

@app.route('/announcements/<announcement_id>', methods=['PUT'])
@role_required(['coordinator', 'admin'])
def update_announcement(announcement_id):
    """Update announcement"""
    announcement = db_service.get_announcement(announcement_id)
    if not announcement:
        return jsonify({"message": "Announcement not found"}), 404
    
    # Check if user can edit this announcement
    if session['role'] == 'coordinator' and announcement.get('created_by') != session['user_id']:
        return jsonify({"message": "Forbidden: Cannot edit announcements not created by you"}), 403
    
    data = request.get_json()
    update_data = {}
    
    if 'title' in data:
        update_data['title'] = data['title']
    if 'content' in data:
        update_data['content'] = data['content']
    if 'priority' in data:
        if data['priority'] in ['low', 'normal', 'high', 'urgent']:
            update_data['priority'] = data['priority']
    if 'target_audience' in data:
        if data['target_audience'] in ['all', 'volunteers', 'coordinators', 'specific_group']:
            update_data['target_audience'] = data['target_audience']
    if 'status' in data:
        if data['status'] in ['active', 'archived']:
            update_data['status'] = data['status']
    
    if update_data:
        db_service.update_announcement(announcement_id, update_data)
        announcement.update(update_data)
        return jsonify({
            "message": "Announcement updated successfully", 
            "announcement": announcement
        }), 200
    
    return jsonify({"message": "No valid fields to update"}), 400

@app.route('/announcements/<announcement_id>', methods=['DELETE'])
@role_required(['coordinator', 'admin'])
def delete_announcement(announcement_id):
    """Delete announcement"""
    announcement = db_service.get_announcement(announcement_id)
    if not announcement:
        return jsonify({"message": "Announcement not found"}), 404
    
    # Check if user can delete this announcement
    if session['role'] == 'coordinator' and announcement.get('created_by') != session['user_id']:
        return jsonify({"message": "Forbidden: Cannot delete announcements not created by you"}), 403
    
    db_service.delete_announcement(announcement_id)
    return jsonify({"message": "Announcement deleted successfully"}), 200

@app.route('/announcements/event/<event_id>', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_event_announcements(event_id):
    """Get announcements for a specific event"""
    event = db_service.get_event(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    announcements = db_service.get_announcements_by_event(event_id)
    announcements.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify(announcements), 200

# --- AI-POWERED FEATURES ENDPOINTS ---

@app.route('/ai/task-guide/<task_id>', methods=['GET'])
@login_required
def get_task_completion_guide(task_id):
    """Get AI-generated task completion guide"""
    try:
        current_user_id = session['user_id']
        current_user_role = session.get('role')
        
        # Get task details
        task = db_service.get_task(task_id)
        if not task:
            return jsonify({"message": "Task not found"}), 404
        
        # Check if user has access to this task
        if current_user_role == 'volunteer':
            assigned_volunteers = task.get('assigned_volunteers', [])
            if task.get('assigned_to') != current_user_id and current_user_id not in assigned_volunteers:
                return jsonify({"message": "Task not assigned to you"}), 403
        
        # Generate AI completion guide
        guide_result = ai_service.generate_task_completion_guide(task)
        
        if guide_result['success']:
            return jsonify(guide_result), 200
        else:
            return jsonify(guide_result), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error generating task guide: {str(e)}"
        }), 500

@app.route('/ai/chatbot', methods=['POST'])
@login_required
def chatbot_query():
    """Handle chatbot queries"""
    try:
        current_user_id = session['user_id']
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"message": "Message is required"}), 400
        
        # Get user context
        user = db_service.get_user(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get user's assigned tasks for context
        assigned_tasks = db_service.get_tasks_by_assignee(current_user_id)
        
        context = {
            'role': user.get('role'),
            'assigned_tasks': assigned_tasks,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate AI response
        response = ai_service.generate_chatbot_response(user_message, context)
        
        if response['success']:
            return jsonify(response), 200
        else:
            return jsonify(response), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing chatbot query: {str(e)}"
        }), 500

@app.route('/ai/recommendations', methods=['GET'])
@login_required
def get_volunteer_recommendations():
    """Get AI-generated volunteer recommendations for coordinators"""
    try:
        current_user_id = session['user_id']
        
        # Get user data
        user = db_service.get_user(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Only allow coordinators and admins to access volunteer recommendations
        if user.get('role') not in ['coordinator', 'admin']:
            return jsonify({
                "success": False,
                "message": "Volunteer recommendations are only available to coordinators and administrators"
            }), 403
        
        # Get available tasks for context
        all_tasks = db_service.get_all_tasks()
        
        user_data = {
            'user_id': current_user_id,
            'role': user.get('role'),
            'skills': user.get('skills', []),
            'completed_tasks': []
        }
        
        # Generate volunteer recommendations
        recommendations = ai_service.generate_recommendations(user_data, all_tasks, [])
        
        if recommendations['success']:
            return jsonify(recommendations), 200
        else:
            return jsonify(recommendations), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error generating volunteer recommendations: {str(e)}"
        }), 500

@app.route('/ai/task-recommendations', methods=['POST'])
@login_required
def get_task_volunteer_recommendations():
    """Get AI recommendations for which volunteers should be assigned to a task"""
    try:
        current_user_id = session['user_id']
        task_data = request.get_json()
        
        # Get all volunteers
        volunteers = db_service.get_all_users()
        volunteer_list = [user for user in volunteers if user.get('role') == 'volunteer']
        
        # Get task details
        task_title = task_data.get('title', '')
        task_description = task_data.get('description', '')
        task_priority = task_data.get('priority', 'Medium')
        
        # Create volunteer data for AI analysis
        volunteer_data = []
        for vol in volunteer_list:
            # Get volunteer's completed tasks
            completed_tasks = db_service.get_tasks_by_assignee(vol['user_id'])
            completed_tasks = [task for task in completed_tasks if task.get('status') == 'Completed']
            
            volunteer_info = {
                'user_id': vol['user_id'],
                'name': vol['name'],
                'role': vol['role'],
                'skills': vol.get('skills', []),
                'completed_tasks': completed_tasks,
                'experience_level': 'expert' if len(completed_tasks) > 10 else 'intermediate' if len(completed_tasks) > 3 else 'beginner'
            }
            volunteer_data.append(volunteer_info)
        
        # Create task analysis prompt
        prompt = f"""
        You are an AI assistant helping coordinators assign the best volunteers to tasks.
        
        TASK DETAILS:
        - Title: {task_title}
        - Description: {task_description}
        - Priority: {task_priority}
        
        AVAILABLE VOLUNTEERS:
        {json.dumps(volunteer_data, indent=2)}
        
        Analyze each volunteer's suitability for this task based on:
        1. Their past task history and performance
        2. Skills and experience level
        3. Task complexity and requirements
        4. Volunteer availability and workload
        
        Return a JSON response with this structure:
        {{
            "recommendations": [
                {{
                    "volunteer_id": "user_id_here",
                    "volunteer_name": "Volunteer Name",
                    "match_score": 85,
                    "reason": "Why this volunteer is recommended for this task",
                    "confidence": "High/Medium/Low"
                }}
            ],
            "reasoning": "Overall recommendation strategy and analysis"
        }}
        
        Recommend 3-5 best volunteers for this task.
        """
        
        # Generate recommendations using AI
        response = ai_service.model.generate_content(prompt)
        
        try:
            recommendations = json.loads(response.text)
            return jsonify({
                "success": True,
                "recommendations": recommendations
            }), 200
        except json.JSONDecodeError:
            # Fallback recommendations
            return jsonify({
                "success": True,
                "recommendations": {
                    "recommendations": [
                        {
                            "volunteer_id": volunteer_data[0]['user_id'] if volunteer_data else "none",
                            "volunteer_name": volunteer_data[0]['name'] if volunteer_data else "No volunteers",
                            "match_score": 75,
                            "reason": "General recommendation based on availability",
                            "confidence": "Medium"
                        }
                    ],
                    "reasoning": "Fallback recommendation due to AI parsing error"
                }
            }), 200
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error generating volunteer recommendations: {str(e)}"
        }), 500

@app.route('/ai/health', methods=['GET'])
def ai_health_check():
    """Check AI service health"""
    try:
        # Test AI service with a simple query
        test_response = ai_service.generate_chatbot_response("Hello", {})
        return jsonify({
            "status": "healthy",
            "ai_service": "operational" if test_response['success'] else "error",
            "message": "AI service is working"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "ai_service": "error",
            "message": f"AI service error: {str(e)}"
        }), 500

# User profile endpoint for chatbot
@app.route('/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get current user profile for chatbot"""
    try:
        current_user_id = session['user_id']
        user = db_service.get_user(current_user_id)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "user_id": current_user_id,
            "role": user.get('role'),
            "name": user.get('name'),
            "email": user.get('email')
        }), 200
        
    except Exception as e:
        return jsonify({
            "message": f"Error getting user profile: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
