from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import uuid
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Change this in a real application

# --- Conceptual Database (In-memory Dictionaries) ---
users = {
    "v1": {"email": "volunteer1@example.com", "password": "password123", "role": "volunteer", "user_id": "v1", "name": "Volunteer One", "contact": "111-222-3333"},
    "c1": {"email": "coordinator1@example.com", "password": "password123", "role": "coordinator", "user_id": "c1", "name": "Coordinator One", "contact": "444-555-6666"},
    "a1": {"email": "admin1@example.com", "password": "password123", "role": "admin", "user_id": "a1", "name": "Admin One", "contact": "777-888-9999"},
}

tasks = {
    "t1": {"title": "Cleanup Drive", "description": "Community park cleanup", "deadline": "2025-07-15", "priority": "High", "status": "Pending", "assigned_to": "v1"},
    "t2": {"title": "Food Distribution", "description": "Distribute food to needy families", "deadline": "2025-07-10", "priority": "Medium", "status": "In Progress", "assigned_to": "v1"},
    "t3": {"title": "Event Setup", "description": "Set up stage for charity event", "deadline": "2025-07-20", "priority": "High", "status": "Pending", "assigned_to": None},
    "t4": {"title": "Fundraising Call", "description": "Call potential donors", "deadline": "2025-07-25", "priority": "Medium", "status": "Pending", "assigned_to": None},
}

attendance_logs = [
    {"log_id": "att1", "user_id": "v1", "task_id": "t1", "date": "2025-07-05"},
    {"log_id": "att2", "user_id": "v1", "task_id": "t2", "date": "2025-07-06"},
]

ratings = [
    {"rating_id": "r1", "volunteer_id": "v1", "coordinator_id": "c1", "task_id": "t1", "score": 4, "comments": "Good effort on cleanup."},
]

expenses = [
    {"expense_id": "e1", "task_id": "t1", "amount": 100, "category": "decoration", "logged_by": "a1"},
    {"expense_id": "e2", "task_id": "t2", "amount": 50, "category": "food", "logged_by": "a1"},
]

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
                return jsonify({"message": "Unauthorized: Login required"}), 401
            current_user_id = session['user_id']
            user_data = next((u for u_id, u in users.items() if u_id == current_user_id), None)
            if not user_data or user_data['role'] not in allowed_roles:
                return jsonify({"message": "Forbidden: Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Blueprints ---
# from vol import vol_bp
# app.register_blueprint(vol_bp)

# --- UI Route ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/coordinator/dashboard')
@role_required(['coordinator'])
def coordinator_dashboard():
    return render_template('index.html')

# --- Authentication Endpoints ---

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = None
    for user_id, user_data in users.items():
        if user_data.get('email') == email and user_data.get('password') == password:
            user = user_data
            break

    if user:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        return jsonify({"message": "Login successful", "role": user['role'], "redirect_to": f"/{user['role']}/dashboard"}), 200
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

# --- VOLUNTEER ROLE ENDPOINTS ---

@app.route('/tasks/assigned', methods=['GET'])
@role_required(['volunteer'])
def volunteer_assigned_tasks():
    current_user_id = session['user_id']
    assigned_tasks = [{"task_id": task_id, **task} for task_id, task in tasks.items() if task.get('assigned_to') == current_user_id]
    # Filter out sensitive information if necessary before sending
    return jsonify(assigned_tasks), 200

@app.route('/tasks/<task_id>', methods=['GET'])
@role_required(['volunteer'])
def volunteer_view_specific_task(task_id):
    current_user_id = session['user_id']
    task = tasks.get(task_id)
    if task and task.get('assigned_to') == current_user_id:
        return jsonify(task), 200
    return jsonify({"message": "Task not found or not assigned to you"}), 404

@app.route('/tasks/update_status/<task_id>', methods=['PUT'])
@role_required(['volunteer'])
def volunteer_mark_task_completed(task_id):
    current_user_id = session['user_id']
    task = tasks.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404
    if task.get('assigned_to') != current_user_id:
        return jsonify({"message": "Forbidden: Cannot update tasks not assigned to you"}), 403

    data = request.get_json()
    new_status = data.get('status')
    if new_status == "Completed":
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
    if not tasks.get(task_id):
        return jsonify({"message": "Invalid Task ID"}), 400
    if tasks.get(task_id).get('assigned_to') != current_user_id:
        return jsonify({"message": "You can only submit attendance for tasks assigned to you."}), 403


    new_log_id = f"att{uuid.uuid4().hex[:8]}"
    attendance_logs.append({"log_id": new_log_id, "user_id": current_user_id, "task_id": task_id, "date": date})
    return jsonify({"message": "Attendance submitted successfully", "log_id": new_log_id}), 201

@app.route('/attendance/my', methods=['GET'])
@role_required(['volunteer'])
def volunteer_my_attendance():
    current_user_id = session['user_id']
    my_attendance = [log for log in attendance_logs if log.get('user_id') == current_user_id]
    return jsonify(my_attendance), 200

@app.route('/ratings/my', methods=['GET'])
@role_required(['volunteer'])
def volunteer_my_ratings():
    current_user_id = session['user_id']
    my_ratings = [rating for rating in ratings if rating.get('volunteer_id') == current_user_id]
    return jsonify(my_ratings), 200

@app.route('/profile', methods=['GET'])
@role_required(['volunteer', 'coordinator', 'admin'])
def view_personal_profile():
    current_user_id = session['user_id']
    user_data = users.get(current_user_id)
    if user_data:
        profile = {k: v for k, v in user_data.items() if k not in ['password']} # Exclude password
        return jsonify(profile), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/profile/update', methods=['PUT'])
@role_required(['volunteer', 'coordinator', 'admin'])
def update_personal_profile():
    current_user_id = session['user_id']
    user_data = users.get(current_user_id)
    if not user_data:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    user_data.update({k: v for k, v in data.items() if k in ['name', 'contact', 'email']}) # Allow specific fields to be updated

    # Optional: Password change functionality
    new_password = data.get('new_password')
    if new_password:
        user_data['password'] = new_password # In a real app, hash and salt this!

    users[current_user_id] = user_data # Update in our "database"
    return jsonify({"message": "Profile updated successfully", "profile": {k: v for k, v in user_data.items() if k not in ['password']}}), 200

# --- COORDINATOR ROLE ENDPOINTS ---

@app.route('/volunteers', methods=['GET'])
@role_required(['coordinator'])
def get_volunteers():
    volunteer_list = [{"user_id": uid, "name": u['name']} for uid, u in users.items() if u['role'] == 'volunteer']
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

    task = tasks.get(task_id)
    volunteer = users.get(volunteer_id)

    if not task or not volunteer:
        return jsonify({"message": "Invalid Task or Volunteer ID"}), 404
    if volunteer['role'] != 'volunteer':
        return jsonify({"message": "Cannot assign tasks to non-volunteers"}), 403

    task['assigned_to'] = volunteer_id
    if priority:
        task['priority'] = priority
    if deadline:
        task['deadline'] = deadline

    return jsonify({"message": "Task assigned successfully", "task": task}), 200

@app.route('/tasks/reassign_volunteer/<task_id>', methods=['PUT'])
@role_required(['coordinator'])
def reassign_task_to_volunteer(task_id):
    data = request.get_json()
    new_volunteer_id = data.get('volunteer_id')

    task = tasks.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    new_volunteer = users.get(new_volunteer_id)
    if not new_volunteer or new_volunteer['role'] != 'volunteer':
        return jsonify({"message": "Invalid new Volunteer ID"}), 400

    task['assigned_to'] = new_volunteer_id
    return jsonify({"message": "Task reassigned successfully", "task": task}), 200

@app.route('/attendance', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_attendance_logs():
    volunteer_id = request.args.get('volunteer_id')
    date_filter = request.args.get('date') # Example: YYYY-MM-DD

    filtered_logs = attendance_logs
    if volunteer_id:
        # Coordinators can only see attendance for volunteers. Admins see all.
        if session['role'] == 'coordinator':
            # In a real system, you'd check if the coordinator "supervises" this volunteer.
            # For this example, we'll assume a coordinator can view any volunteer's attendance.
            if users.get(volunteer_id) and users.get(volunteer_id)['role'] != 'volunteer':
                return jsonify({"message": "Coordinators can only view volunteer attendance"}), 403
        filtered_logs = [log for log in filtered_logs if log.get('user_id') == volunteer_id]
    if date_filter:
        filtered_logs = [log for log in filtered_logs if log.get('date') == date_filter]

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

    volunteer = users.get(volunteer_id)
    task = tasks.get(task_id)

    if not volunteer or volunteer['role'] != 'volunteer':
        return jsonify({"message": "Invalid Volunteer ID"}), 400
    if not task:
        return jsonify({"message": "Invalid Task ID"}), 400

    # Coordinator specific restriction: Cannot rate volunteers not assigned to them
    if session['role'] == 'coordinator':
        # Check if the volunteer is assigned to this task
        if task.get('assigned_to') != volunteer_id:
            return jsonify({"message": "Forbidden: Cannot rate volunteers not assigned to this task"}), 403

    new_rating_id = f"r{uuid.uuid4().hex[:8]}"
    ratings.append({
        "rating_id": new_rating_id,
        "volunteer_id": volunteer_id,
        "coordinator_id": current_user_id if session['role'] == 'coordinator' else None, # Only coordinators log this
        "admin_id": current_user_id if session['role'] == 'admin' else None, # Only admins log this
        "task_id": task_id,
        "score": score,
        "comments": comments
    })
    return jsonify({"message": "Rating added successfully", "rating_id": new_rating_id}), 201

@app.route('/ratings', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_ratings():
    submitted_by_me = request.args.get('submitted_by')
    volunteer_id_filter = request.args.get('volunteer_id')

    filtered_ratings = ratings

    if session['role'] == 'coordinator':
        if submitted_by_me == 'me':
            filtered_ratings = [r for r in filtered_ratings if r.get('coordinator_id') == session['user_id']]
        elif volunteer_id_filter:
            # Coordinator can only see ratings for volunteers they manage (simple check based on task assignment)
            valid_task_ids_for_coord = [tid for tid, task in tasks.items() if task.get('assigned_to') == volunteer_id_filter]
            filtered_ratings = [r for r in filtered_ratings if r.get('volunteer_id') == volunteer_id_filter and r.get('task_id') in valid_task_ids_for_coord]
        else:
            # Coordinators can only see ratings they submitted or for volunteers they oversee
            # For simplicity, let's say they can see all ratings, but cannot edit/delete others.
            pass # More granular control would be needed here for a complex system
    elif session['role'] == 'admin':
        if volunteer_id_filter:
            filtered_ratings = [r for r in filtered_ratings if r.get('volunteer_id') == volunteer_id_filter]

    return jsonify(filtered_ratings), 200

@app.route('/ratings/<rating_id>', methods=['PUT'])
@role_required(['coordinator', 'admin'])
def update_rating(rating_id):
    current_user_id = session['user_id']
    rating = next((r for r in ratings if r.get('rating_id') == rating_id), None)

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    if session['role'] == 'coordinator' and rating.get('coordinator_id') != current_user_id:
        return jsonify({"message": "Forbidden: Cannot edit ratings not submitted by you"}), 403

    data = request.get_json()
    if 'score' in data:
        if not isinstance(data['score'], (int, float)) or not (1 <= data['score'] <= 5):
            return jsonify({"message": "Score must be between 1 and 5"}), 400
        rating['score'] = data['score']
    if 'comments' in data:
        rating['comments'] = data['comments']

    return jsonify({"message": "Rating updated successfully", "rating": rating}), 200

@app.route('/expenses', methods=['GET'])
@role_required(['coordinator', 'admin'])
def get_expenses():
    task_id = request.args.get('task_id')
    category = request.args.get('category')

    filtered_expenses = expenses
    if task_id:
        filtered_expenses = [exp for exp in filtered_expenses if exp.get('task_id') == task_id]
    if category:
        filtered_expenses = [exp for exp in filtered_expenses if exp.get('category') == category]

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
    assigned_tasks_data = []
    for task_id, task in tasks.items():
        if task.get('assigned_to'):
            assignee = users.get(task['assigned_to'])
            assigned_tasks_data.append({
                "task_id": task_id,
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
    users_list = []
    for user_id, user_data in users.items():
        user_info = {k: v for k, v in user_data.items() if k not in ['password']}
        users_list.append(user_info)
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
    if any(u['email'] == email for u_id, u in users.items()):
        return jsonify({"message": "User with this email already exists"}), 409

    new_user_id = f"{role[0]}{uuid.uuid4().hex[:8]}"
    users[new_user_id] = {
        "email": email,
        "password": password, # In a real app, hash and salt this!
        "role": role,
        "user_id": new_user_id,
        "name": name,
        "contact": contact
    }
    return jsonify({"message": "User created successfully", "user_id": new_user_id}), 201

@app.route('/users/<user_id>', methods=['PUT'])
@role_required(['admin'])
def update_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    if 'role' in data:
        if data['role'] in ['volunteer', 'coordinator', 'admin']:
            user['role'] = data['role']
        else:
            return jsonify({"message": "Invalid role"}), 400
    if 'password' in data:
        user['password'] = data['password'] # Again, hash and salt this!
    if 'contact' in data:
        user['contact'] = data['contact']

    return jsonify({"message": "User updated successfully", "user": {k: v for k, v in user.items() if k not in ['password']}}), 200

@app.route('/users/<user_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        # In a real app, you'd also delete associated data (tasks, attendance, ratings, etc.)
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/tasks/create', methods=['POST'])
@role_required(['admin'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline')
    priority = data.get('priority')
    assigned_to = data.get('assigned_to') # Optional, can be assigned later

    if not all([title, description, deadline, priority]):
        return jsonify({"message": "Missing required task fields"}), 400

    new_task_id = f"t{uuid.uuid4().hex[:8]}"
    tasks[new_task_id] = {
        "title": title,
        "description": description,
        "deadline": deadline,
        "priority": priority,
        "status": "Pending",
        "assigned_to": assigned_to if assigned_to in users and users[assigned_to]['role'] in ['volunteer', 'coordinator'] else None
    }
    return jsonify({"message": "Task created successfully", "task_id": new_task_id}), 201

@app.route('/tasks/assign', methods=['POST'])
@role_required(['admin'])
def admin_assign_task():
    # Admin can assign tasks to both coordinators and volunteers
    data = request.get_json()
    task_id = data.get('task_id')
    assignee_id = data.get('assignee_id')

    task = tasks.get(task_id)
    assignee = users.get(assignee_id)

    if not task or not assignee:
        return jsonify({"message": "Invalid Task or Assignee ID"}), 404
    if assignee['role'] not in ['volunteer', 'coordinator']:
        return jsonify({"message": "Cannot assign tasks to this role"}), 400

    task['assigned_to'] = assignee_id
    return jsonify({"message": "Task assigned successfully by admin", "task": task}), 200

@app.route('/tasks', methods=['GET'])
@role_required(['coordinator'])
def coordinator_get_all_tasks():
    status_filter = request.args.get('status')
    all_tasks = []
    for task_id, task in tasks.items():
        task_info = {"task_id": task_id, **task}
        all_tasks.append(task_info)
    if status_filter:
        all_tasks = [task for task in all_tasks if task.get('status', '').lower() == status_filter.lower()]
    return jsonify(all_tasks), 200

@app.route('/tasks/<task_id>', methods=['PUT'])
@role_required(['admin'])
def admin_update_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()
    task.update(data) # Admin can update any field directly
    return jsonify({"message": "Task updated successfully", "task": task}), 200

@app.route('/tasks/<task_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_task(task_id):
    if task_id in tasks:
        del tasks[task_id]
        return jsonify({"message": "Task deleted successfully"}), 200
    return jsonify({"message": "Task not found"}), 404

@app.route('/attendance/absentees', methods=['GET'])
@role_required(['admin'])
def get_absentees():
    # For simplicity, absentees are volunteers who haven't logged attendance today for any assigned task
    today_date = datetime.now().strftime("%Y-%m-%d")
    volunteers_who_logged_today = {log['user_id'] for log in attendance_logs if log['date'] == today_date}

    all_volunteers = {uid for uid, u in users.items() if u['role'] == 'volunteer'}
    absent_volunteers_ids = all_volunteers - volunteers_who_logged_today

    absent_volunteers_details = []
    for vol_id in absent_volunteers_ids:
        absent_volunteers_details.append({
            "user_id": vol_id,
            "name": users[vol_id]['name'],
            "email": users[vol_id]['email']
        })
    return jsonify(absent_volunteers_details), 200

@app.route('/ratings/<rating_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_rating(rating_id):
    global ratings # Declare global to modify the list
    initial_len = len(ratings)
    ratings = [r for r in ratings if r.get('rating_id') != rating_id]
    if len(ratings) < initial_len:
        return jsonify({"message": "Rating deleted successfully"}), 200
    return jsonify({"message": "Rating not found"}), 404

@app.route('/expenses/log', methods=['POST'])
@role_required(['admin'])
def log_expense():
    data = request.get_json()
    task_id = data.get('task_id')
    amount = data.get('amount')
    category = data.get('category')

    if not all([task_id, amount, category]):
        return jsonify({"message": "Missing required expense fields"}), 400
    if not tasks.get(task_id):
        return jsonify({"message": "Invalid Task ID"}), 400

    new_expense_id = f"e{uuid.uuid4().hex[:8]}"
    expenses.append({
        "expense_id": new_expense_id,
        "task_id": task_id,
        "amount": amount,
        "category": category,
        "logged_by": session['user_id']
    })
    return jsonify({"message": "Expense logged successfully", "expense_id": new_expense_id}), 201

@app.route('/expenses/<expense_id>', methods=['PUT'])
@role_required(['admin'])
def update_expense(expense_id):
    expense = next((e for e in expenses if e.get('expense_id') == expense_id), None)
    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    data = request.get_json()
    if 'amount' in data:
        expense['amount'] = data['amount']
    if 'category' in data:
        expense['category'] = data['category']
    if 'task_id' in data:
        expense['task_id'] = data['task_id']

    return jsonify({"message": "Expense updated successfully", "expense": expense}), 200

@app.route('/expenses/<expense_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_expense(expense_id):
    global expenses
    initial_len = len(expenses)
    expenses = [e for e in expenses if e.get('expense_id') != expense_id]
    if len(expenses) < initial_len:
        return jsonify({"message": "Expense deleted successfully"}), 200
    return jsonify({"message": "Expense not found"}), 404

# --- ADMIN REPORTS ---

@app.route('/reports/tasks', methods=['GET'])
@role_required(['admin'])
def admin_report_tasks():
    # [cite_start]Task summary (assigned, completed, overdue) [cite: 8]
    summary = {
        "total_tasks": len(tasks),
        "pending": sum(1 for t in tasks.values() if t['status'] == 'Pending'),
        "in_progress": sum(1 for t in tasks.values() if t['status'] == 'In Progress'),
        "completed": sum(1 for t in tasks.values() if t['status'] == 'Completed'),
        "overdue": sum(1 for t in tasks.values() if t['status'] != 'Completed' and datetime.now().date() > datetime.strptime(t['deadline'], "%Y-%m-%d").date())
    }
    return jsonify(summary), 200

@app.route('/reports/ratings', methods=['GET'])
@role_required(['admin'])
def admin_report_ratings():
    # [cite_start]Ratings and feedback summary [cite: 8]
    rating_summary = {}
    for r in ratings:
        vol_id = r['volunteer_id']
        if vol_id not in rating_summary:
            rating_summary[vol_id] = {"total_score": 0, "count": 0, "comments": []}
        rating_summary[vol_id]["total_score"] += r['score']
        rating_summary[vol_id]["count"] += 1
        rating_summary[vol_id]["comments"].append(r['comments'])

    for vol_id, data in rating_summary.items():
        data['average_score'] = data['total_score'] / data['count']
        data['volunteer_name'] = users.get(vol_id, {}).get('name', 'Unknown')

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
    if any(u['email'] == email for u in users.values()):
        return jsonify({"message": "User with this email already exists"}), 409

    new_user_id = f"v{uuid.uuid4().hex[:8]}"
    users[new_user_id] = {
        "email": email,
        "password": password,  # In a real app, hash and salt this!
        "role": "volunteer",
        "user_id": new_user_id,
        "name": name,
        "contact": contact
    }
    return jsonify({"message": "Volunteer registered successfully", "user_id": new_user_id}), 201

@app.route('/dashboard/volunteer', methods=['GET'])
@role_required(['volunteer'])
def volunteer_dashboard_summary():
    current_user_id = session['user_id']
    user = users.get(current_user_id)
    # Attendance %
    total_tasks = len([t for t in tasks.values() if t.get('assigned_to') == current_user_id])
    attended = len([log for log in attendance_logs if log.get('user_id') == current_user_id])
    attendance_percent = int((attended / total_tasks) * 100) if total_tasks else 0
    # Average rating
    my_ratings = [r for r in ratings if r.get('volunteer_id') == current_user_id]
    avg_rating = round(sum(r['score'] for r in my_ratings) / len(my_ratings), 2) if my_ratings else 0
    # Tasks
    my_tasks = []
    for task_id, t in tasks.items():
        if t.get('assigned_to') == current_user_id:
            task_info = {"task_id": task_id, **t}
            # Attach rating if exists
            task_ratings = [r for r in my_ratings if r['task_id'] == task_id]
            task_info['rating'] = task_ratings[0]['score'] if task_ratings else None
            my_tasks.append(task_info)
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
    user = users.get(current_user_id)
    # Volunteers managed (all volunteers for now)
    volunteer_ids = [uid for uid, u in users.items() if u['role'] == 'volunteer']
    # Attendance % (average of their volunteers)
    attendance_percents = []
    for vid in volunteer_ids:
        total_tasks = len([t for t in tasks.values() if t.get('assigned_to') == vid])
        attended = len([log for log in attendance_logs if log.get('user_id') == vid])
        percent = int((attended / total_tasks) * 100) if total_tasks else 0
        attendance_percents.append(percent)
    avg_attendance = int(sum(attendance_percents) / len(attendance_percents)) if attendance_percents else 0
    # Average rating (of their volunteers)
    volunteer_ratings = [r for r in ratings if r.get('volunteer_id') in volunteer_ids]
    avg_rating = round(sum(r['score'] for r in volunteer_ratings) / len(volunteer_ratings), 2) if volunteer_ratings else 0
    # Tasks assigned
    assigned_tasks = []
    for task_id, t in tasks.items():
        if t.get('assigned_to') in volunteer_ids:
            task_info = {"task_id": task_id, **t}
            # Attach rating if exists
            task_ratings = [r for r in ratings if r['volunteer_id'] == t['assigned_to'] and r['task_id'] == task_id]
            task_info['rating'] = task_ratings[0]['score'] if task_ratings else None
            assigned_tasks.append(task_info)
    # Team (volunteers)
    team = [{"name": users[vid]['name'], "email": users[vid]['email'], "location": "", "amount": 0} for vid in volunteer_ids]
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
    user = users.get(session['user_id'])
    # Attendance % (average of all volunteers)
    volunteer_ids = [uid for uid, u in users.items() if u['role'] == 'volunteer']
    attendance_percents = []
    for vid in volunteer_ids:
        total_tasks = len([t for t in tasks.values() if t.get('assigned_to') == vid])
        attended = len([log for log in attendance_logs if log.get('user_id') == vid])
        percent = int((attended / total_tasks) * 100) if total_tasks else 0
        attendance_percents.append(percent)
    avg_attendance = int(sum(attendance_percents) / len(attendance_percents)) if attendance_percents else 0
    # Average rating (all volunteers)
    volunteer_ratings = [r for r in ratings if r.get('volunteer_id') in volunteer_ids]
    avg_rating = round(sum(r['score'] for r in volunteer_ratings) / len(volunteer_ratings), 2) if volunteer_ratings else 0
    # All tasks
    all_tasks = []
    for task_id, t in tasks.items():
        task_info = {"task_id": task_id, **t}
        # Attach rating if exists
        task_ratings = [r for r in ratings if r['volunteer_id'] == t.get('assigned_to') and r['task_id'] == task_id]
        task_info['rating'] = task_ratings[0]['score'] if task_ratings else None
        all_tasks.append(task_info)
    # Team (all users)
    team = [{"name": u['name'], "email": u['email'], "location": "", "amount": 0} for uid, u in users.items()]
    return jsonify({
        "name": user['name'],
        "attendance_percent": avg_attendance,
        "average_rating": avg_rating,
        "tasks": all_tasks,
        "team": team
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)