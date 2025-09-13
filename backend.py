from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS
import uuid
import os
from functools import wraps
from datetime import datetime
from database_service import db_service

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_super_secret_key') # Use environment variable in production
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# --- Firebase Database Service ---
# All data operations now go through the database service

# --- Helper Functions and Decorators for Authentication and Authorization ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized: Login required"}), 401
        return f(*args, **kwargs)
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

    user = db_service.get_user_by_email(email)
    
    if user and user.get('password') == password:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        return jsonify({"message": "Login successful", "role": user['role'], "redirect_to": "/dashbords"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/session/check', methods=['GET'])
def check_session():
    if 'role' in session:
        return jsonify({'logged_in': True, 'role': session['role']}), 200
    return jsonify({'logged_in': False}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'firebase_connected': db_service.db is not None,
        'environment': 'production' if os.getenv('FIREBASE_PROJECT_ID') else 'development'
    }), 200

# --- VOLUNTEER ROLE ENDPOINTS ---

@app.route('/tasks/assigned', methods=['GET'])
@role_required(['volunteer'])
def volunteer_assigned_tasks():
    current_user_id = session['user_id']
    assigned_tasks = db_service.get_tasks_by_assignee(current_user_id)
    # Filter out sensitive information if necessary before sending
    return jsonify(assigned_tasks), 200

@app.route('/tasks/<task_id>', methods=['GET'])
@role_required(['volunteer'])
def volunteer_view_specific_task(task_id):
    current_user_id = session['user_id']
    task = db_service.get_task(task_id)
    if task and task.get('assigned_to') == current_user_id:
        return jsonify(task), 200
    return jsonify({"message": "Task not found or not assigned to you"}), 404

@app.route('/tasks/update_status/<task_id>', methods=['PUT'])
@role_required(['volunteer'])
def volunteer_mark_task_completed(task_id):
    current_user_id = session['user_id']
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    if task.get('assigned_to') != current_user_id:
        return jsonify({"message": "Forbidden: Cannot update tasks not assigned to you"}), 403

    data = request.get_json()
    new_status = data.get('status')
    if new_status == "Completed":
        db_service.update_task(task_id, {"status": "Completed"})
        task['status'] = "Completed"
        return jsonify({"message": f"Task {task_id} marked as Completed", "task": task}), 200
    return jsonify({"message": "Invalid status update"}), 400

@app.route('/attendance/submit', methods=['POST'])
@role_required(['volunteer'])
def volunteer_submit_attendance():
    current_user_id = session['user_id']
    data = request.get_json()
    task_id = data.get('task_id')
    date = data.get('date', datetime.now().strftime("%Y-%m-%d"))

    if not task_id:
        return jsonify({"message": "Task ID is required"}), 400
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Invalid Task ID"}), 400
    if task.get('assigned_to') != current_user_id:
        return jsonify({"message": "You can only submit attendance for tasks assigned to you."}), 403

    # Prevent duplicate attendance for same user, task, date
    if db_service.check_attendance_exists(current_user_id, task_id, date):
        return jsonify({"message": "Attendance already submitted for this task and date."}), 409

    new_log_id = db_service.create_attendance_log({"log_id": f"att{uuid.uuid4().hex[:8]}", "user_id": current_user_id, "task_id": task_id, "date": date})
    return jsonify({"message": "Attendance submitted successfully", "log_id": new_log_id}), 201

@app.route('/attendance/my', methods=['GET'])
@role_required(['volunteer'])
def volunteer_my_attendance():
    current_user_id = session['user_id']
    my_attendance = db_service.get_attendance_logs(user_id=current_user_id)
    return jsonify(my_attendance), 200

@app.route('/ratings/my', methods=['GET'])
@role_required(['volunteer'])
def volunteer_my_ratings():
    current_user_id = session['user_id']
    my_ratings = db_service.get_ratings(volunteer_id=current_user_id)
    return jsonify(my_ratings), 200

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

@app.route('/tasks/reassign_volunteer/<task_id>', methods=['PUT'])
@role_required(['coordinator'])
def reassign_task_to_volunteer(task_id):
    data = request.get_json()
    new_volunteer_id = data.get('volunteer_id')

    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    new_volunteer = db_service.get_user(new_volunteer_id)
    if not new_volunteer or new_volunteer['role'] != 'volunteer':
        return jsonify({"message": "Invalid new Volunteer ID"}), 400

    db_service.update_task(task_id, {'assigned_to': new_volunteer_id})
    task['assigned_to'] = new_volunteer_id
    return jsonify({"message": "Task reassigned successfully", "task": task}), 200

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
        filtered_logs = db_service.get_attendance_logs(user_id=volunteer_id, date=date_filter)
    else:
        filtered_logs = db_service.get_attendance_logs(date=date_filter)

    return jsonify(filtered_logs), 200

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
@role_required(['admin'])
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

    if not all([title, description, deadline, priority]):
        return jsonify({"message": "Missing required task fields"}), 400

    # Validate assigned_to if provided
    if assigned_to:
        user = db_service.get_user(assigned_to)
        if not user or user['role'] not in ['volunteer', 'coordinator']:
            assigned_to = None

    task_data = {
        "title": title,
        "description": description,
        "deadline": deadline,
        "priority": priority,
        "status": "Pending",
        "assigned_to": assigned_to
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

@app.route('/tasks/<task_id>', methods=['PUT'])
@role_required(['admin'])
def admin_update_task(task_id):
    task = db_service.get_task(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()
    db_service.update_task(task_id, data) # Admin can update any field directly
    task.update(data)
    return jsonify({"message": "Task updated successfully", "task": task}), 200

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
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    contact = data.get('contact')

    if not all([email, password, name]):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if email already exists
    existing_user = db_service.get_user_by_email(email)
    if existing_user:
        return jsonify({"message": "User with this email already exists"}), 409

    user_data = {
        "email": email,
        "password": password,  # In a real app, hash and salt this!
        "role": "volunteer",
        "name": name,
        "contact": contact
    }
    new_user_id = db_service.create_user(user_data)
    return jsonify({"message": "Volunteer registered successfully", "user_id": new_user_id}), 201

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

@app.route('/attendance/mark', methods=['POST'])
@role_required(['coordinator', 'admin'])
def mark_attendance_for_user():
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

    # Prevent duplicate attendance for same user, task, date
    if db_service.check_attendance_exists(user_id, task_id, date):
        return jsonify({"message": "Attendance already submitted for this user, task, and date."}), 409

    new_log_id = db_service.create_attendance_log({"log_id": f"att{uuid.uuid4().hex[:8]}", "user_id": user_id, "task_id": task_id, "date": date})
    return jsonify({"message": "Attendance marked successfully", "log_id": new_log_id}), 201

# --- FILTER ENDPOINTS FOR UI ---

@app.route('/attendance/filter', methods=['GET'])
@role_required(['admin', 'coordinator'])
def filter_attendance():
    user_id = request.args.get('user_id')
    task_id = request.args.get('task_id')
    date = request.args.get('date')
    filtered = db_service.get_attendance_logs(user_id=user_id, task_id=task_id, date=date)
    return jsonify(filtered), 200

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# For Vercel deployment
app = app