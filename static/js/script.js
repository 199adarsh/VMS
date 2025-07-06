const API_BASE_URL = 'http://127.0.0.1:5000'; // Make sure this matches your Flask backend URL

// --- DOM Elements ---
const loginSection = document.getElementById('login-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const loginMessage = document.getElementById('login-message');
const userNameSpan = document.getElementById('user-name');
const userRoleSpan = document.getElementById('user-role');
const logoutButton = document.getElementById('logout-button');
const dashboardTabs = document.getElementById('dashboard-tabs');
const tabContents = document.querySelectorAll('.tab-content');

// Volunteer Specific Elements
const assignedTasksList = document.getElementById('assigned-tasks-list');
const submitAttendanceForm = document.getElementById('submit-attendance-form');
const attendanceTaskIdSelect = document.getElementById('attendance-task-id');
const attendanceDateInput = document.getElementById('attendance-date');
const attendanceMessage = document.getElementById('attendance-message');
const myAttendanceHistory = document.getElementById('my-attendance-history');
const myRatingsList = document.getElementById('my-ratings-list');
const updateProfileForm = document.getElementById('update-profile-form');
const profileNameInput = document.getElementById('profile-name');
const profileEmailInput = document.getElementById('profile-email');
const profileContactInput = document.getElementById('profile-contact');
const profileNewPasswordInput = document.getElementById('profile-new-password');
const profileMessage = document.getElementById('profile-message');

// Coordinator Specific Elements
const assignTaskForm = document.getElementById('assign-task-form');
const assignTaskIdSelect = document.getElementById('assign-task-id');
const assignVolunteerIdSelect = document.getElementById('assign-volunteer-id');
const assignPrioritySelect = document.getElementById('assign-priority');
const assignDeadlineInput = document.getElementById('assign-deadline');
const assignTaskMessage = document.getElementById('assign-task-message');
const reassignTaskForm = document.getElementById('reassign-task-form');
const reassignTaskSelect = document.getElementById('reassign-task-select');
const reassignVolunteerIdSelect = document.getElementById('reassign-volunteer-id');
const reassignTaskMessage = document.getElementById('reassign-task-message');
const coordAttendanceVolunteerFilter = document.getElementById('coord-attendance-volunteer-filter');
const coordAttendanceDateFilter = document.getElementById('coord-attendance-date-filter');
const coordAttendanceFilterBtn = document.getElementById('coord-attendance-filter-btn');
const coordAttendanceResetBtn = document.getElementById('coord-attendance-reset-btn');
const coordinatorAttendanceList = document.getElementById('coordinator-attendance-list');
const submitRatingForm = document.getElementById('submit-rating-form');
const ratingVolunteerIdSelect = document.getElementById('rating-volunteer-id');
const ratingTaskIdSelect = document.getElementById('rating-task-id');
const ratingScoreInput = document.getElementById('rating-score');
const ratingCommentsTextarea = document.getElementById('rating-comments');
const submitRatingMessage = document.getElementById('submit-rating-message');
const mySubmittedRatingsList = document.getElementById('my-submitted-ratings-list');
const coordExpenseTaskFilter = document.getElementById('coord-expense-task-filter');
const coordExpenseCategoryFilter = document.getElementById('coord-expense-category-filter');
const coordExpenseFilterBtn = document.getElementById('coord-expense-filter-btn');
const coordExpenseResetBtn = document.getElementById('coord-expense-reset-btn');
const coordinatorExpensesList = document.getElementById('coordinator-expenses-list');
const reportCoordAttendance = document.getElementById('report-coord-attendance');
const reportCoordAssignments = document.getElementById('report-coord-assignments');
const reportCoordExpenses = document.getElementById('report-coord-expenses');

// Admin Specific Elements
const createUserForm = document.getElementById('create-user-form');
const createUserNameInput = document.getElementById('new-user-name');
const createUserEmailInput = document.getElementById('new-user-email');
const createUserPasswordInput = document.getElementById('new-user-password');
const createUserRoleSelect = document.getElementById('new-user-role');
const createUserContactInput = document.getElementById('new-user-contact');
const createUserMessage = document.getElementById('create-user-message');
const allUsersList = document.getElementById('all-users-list');
const createTaskForm = document.getElementById('create-task-form');
const newTaskTitleInput = document.getElementById('new-task-title');
const newTaskDescriptionTextarea = document.getElementById('new-task-description');
const newTaskDeadlineInput = document.getElementById('new-task-deadline');
const newTaskPrioritySelect = document.getElementById('new-task-priority');
const newTaskAssignToSelect = document.getElementById('new-task-assign-to');
const createTaskMessage = document.getElementById('create-task-message');
const adminTaskStatusFilter = document.getElementById('admin-task-status-filter');
const adminTaskFilterBtn = document.getElementById('admin-task-filter-btn');
const adminTaskResetBtn = document.getElementById('admin-task-reset-btn');
const allTasksList = document.getElementById('all-tasks-list');
const adminAttendanceVolunteerFilter = document.getElementById('admin-attendance-volunteer-filter');
const adminAttendanceDateFilter = document.getElementById('admin-attendance-date-filter');
const adminAttendanceFilterBtn = document.getElementById('admin-attendance-filter-btn');
const adminAttendanceResetBtn = document.getElementById('admin-attendance-reset-btn');
const adminAllAttendanceList = document.getElementById('admin-all-attendance-list');
const getAbsenteesBtn = document.getElementById('get-absentees-btn');
const adminAbsenteesList = document.getElementById('admin-absentees-list');
const adminSubmitRatingForm = document.getElementById('admin-submit-rating-form');
const adminRatingVolunteerIdSelect = document.getElementById('admin-rating-volunteer-id');
const adminRatingTaskIdSelect = document.getElementById('admin-rating-task-id');
const adminRatingScoreInput = document.getElementById('admin-rating-score');
const adminRatingCommentsTextarea = document.getElementById('admin-rating-comments');
const adminSubmitRatingMessage = document.getElementById('admin-submit-rating-message');
const adminAllRatingsList = document.getElementById('admin-all-ratings-list');
const logExpenseForm = document.getElementById('log-expense-form');
const expenseTaskIdSelect = document.getElementById('expense-task-id');
const expenseAmountInput = document.getElementById('expense-amount');
const expenseCategoryInput = document.getElementById('expense-category');
const logExpenseMessage = document.getElementById('log-expense-message');
const adminExpenseTaskFilter = document.getElementById('admin-expense-task-filter');
const adminExpenseCategoryFilter = document.getElementById('admin-expense-category-filter');
const adminExpenseFilterBtn = document.getElementById('admin-expense-filter-btn');
const adminExpenseResetBtn = document.getElementById('admin-expense-reset-btn');
const adminAllExpensesList = document.getElementById('admin-all-expenses-list');
const reportAdminTasks = document.getElementById('report-admin-tasks');
const reportAdminAttendance = document.getElementById('report-admin-attendance');
const reportAdminRatings = document.getElementById('report-admin-ratings');
const reportAdminExpenses = document.getElementById('report-admin-expenses');
const reportAdminAssignments = document.getElementById('report-admin-assignments');

// --- Utility Functions ---

/**
 * Displays a message in a designated message box.
 * @param {HTMLElement} element The message box element.
 * @param {string} message The message to display.
 * @param {string} type The type of message ('success' or 'error').
 */
function showMessage(element, message, type = 'success') {
    if (!element) return;
    
    element.textContent = message;
    element.className = `message-box ${type}`;
    element.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        element.classList.add('hidden');
    }, 5000);
}

/**
 * Makes an API request to the backend.
 * @param {string} endpoint The API endpoint.
 * @param {string} method The HTTP method.
 * @param {Object} data The data to send (optional).
 * @returns {Promise} The response data.
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include' // Include cookies for session management
    };

    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    const responseData = await response.json();

    if (!response.ok) {
        if (response.status === 401) {
            logout();
        }
        throw new Error(responseData.message || 'An API error occurred.');
    }
    return responseData;
}

/**
 * Checks if user is logged in and updates UI accordingly.
 */
async function checkSession() {
    try {
        const sessionData = await apiRequest('/session/check', 'GET');
        if (sessionData.logged_in) {
            loginSection.classList.add('hidden');
            dashboardSection.classList.remove('hidden');
            updateUIForRole(sessionData.role);
            await loadUserProfile();
        }
    } catch (error) {
        console.log('No active session');
    }
}

/**
 * Loads user profile data.
 */
async function loadUserProfile() {
    try {
        const profile = await apiRequest('/profile', 'GET');
        userNameSpan.textContent = profile.name || 'User';
        userRoleSpan.textContent = profile.role || 'Unknown';
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

/**
 * Logs out the user and resets the UI.
 */
function logout() {
    loginSection.classList.remove('hidden');
    dashboardSection.classList.add('hidden');
    tabContents.forEach(content => content.classList.add('hidden'));
    loginForm.reset();
    userNameSpan.textContent = '';
    userRoleSpan.textContent = '';
}

/**
 * Updates the UI based on user role.
 * @param {string} role The user's role.
 */
function updateUIForRole(role) {
    // Clear all tabs first
    dashboardTabs.innerHTML = '';
    tabContents.forEach(content => content.classList.add('hidden'));

    if (role === 'volunteer') {
        setupVolunteerTabs();
    } else if (role === 'coordinator') {
        setupCoordinatorTabs();
    } else if (role === 'admin') {
        setupAdminTabs();
    }
}

/**
 * Sets up tabs for volunteer role.
 */
function setupVolunteerTabs() {
    const tabs = [
        { id: 'volunteer-assigned-tasks', label: 'My Tasks' },
        { id: 'volunteer-attendance', label: 'Attendance' },
        { id: 'volunteer-ratings', label: 'My Ratings' },
        { id: 'volunteer-profile', label: 'Profile' }
    ];

    tabs.forEach(tab => {
        const tabButton = document.createElement('button');
        tabButton.className = 'tab-button';
        tabButton.textContent = tab.label;
        tabButton.onclick = () => showTab(tab.id);
        dashboardTabs.appendChild(tabButton);
    });

    // Show first tab by default
    if (tabs.length > 0) {
        showTab(tabs[0].id);
    }
}

/**
 * Sets up tabs for coordinator role.
 */
function setupCoordinatorTabs() {
    const tabs = [
        { id: 'coordinator-assign-tasks', label: 'Assign Tasks' },
        { id: 'coordinator-attendance', label: 'Attendance' },
        { id: 'coordinator-ratings', label: 'Ratings' },
        { id: 'coordinator-expenses', label: 'Expenses' },
        { id: 'coordinator-reports', label: 'Reports' }
    ];

    tabs.forEach(tab => {
        const tabButton = document.createElement('button');
        tabButton.className = 'tab-button';
        tabButton.textContent = tab.label;
        tabButton.onclick = () => showTab(tab.id);
        dashboardTabs.appendChild(tabButton);
    });

    // Show first tab by default
    if (tabs.length > 0) {
        showTab(tabs[0].id);
    }
}

/**
 * Sets up tabs for admin role.
 */
function setupAdminTabs() {
    const tabs = [
        { id: 'admin-users', label: 'Users' },
        { id: 'admin-tasks', label: 'Tasks' },
        { id: 'admin-attendance', label: 'Attendance' },
        { id: 'admin-ratings', label: 'Ratings' },
        { id: 'admin-expenses', label: 'Expenses' },
        { id: 'admin-reports', label: 'Reports' }
    ];

    tabs.forEach(tab => {
        const tabButton = document.createElement('button');
        tabButton.className = 'tab-button';
        tabButton.textContent = tab.label;
        tabButton.onclick = () => showTab(tab.id);
        dashboardTabs.appendChild(tabButton);
    });

    // Show first tab by default
    if (tabs.length > 0) {
        showTab(tabs[0].id);
    }
}

/**
 * Shows a specific tab and hides others.
 * @param {string} tabId The ID of the tab to show.
 */
function showTab(tabId) {
    // Update tab buttons
    const tabButtons = dashboardTabs.querySelectorAll('.tab-button');
    tabButtons.forEach(btn => btn.classList.remove('active'));

    // Hide all tab contents
    tabContents.forEach(content => content.classList.add('hidden'));

    // Show selected tab content
    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {
        selectedContent.classList.remove('hidden');
    }

    // Mark active tab button
    const activeButton = Array.from(tabButtons).find(btn => 
        btn.textContent.toLowerCase().includes(tabId.split('-')[1])
    );
    if (activeButton) {
        activeButton.classList.add('active');
    }

    // Load data for the selected tab
    loadTabData(tabId);
}

/**
 * Loads data for a specific tab.
 * @param {string} tabId The ID of the tab.
 */
async function loadTabData(tabId) {
    try {
        if (tabId === 'volunteer-assigned-tasks') {
            await fetchAssignedTasks();
        } else if (tabId === 'volunteer-attendance') {
            await fetchMyAttendance();
        } else if (tabId === 'volunteer-ratings') {
            await fetchMyRatings();
        } else if (tabId === 'volunteer-profile') {
            await fetchProfile();
        } else if (tabId === 'coordinator-assign-tasks') {
            await populateCoordinatorTaskSelects();
            await populateVolunteerSelects();
        } else if (tabId === 'coordinator-attendance') {
            await fetchCoordinatorAttendance();
        } else if (tabId === 'coordinator-ratings') {
            await populateCoordinatorRatingSelects();
            await fetchMySubmittedRatings();
        } else if (tabId === 'coordinator-expenses') {
            await fetchCoordinatorExpenses();
        } else if (tabId === 'coordinator-reports') {
            await fetchCoordinatorReports();
        } else if (tabId === 'admin-users') {
            await fetchAllUsers();
        } else if (tabId === 'admin-tasks') {
            await fetchAllTasks();
        } else if (tabId === 'admin-attendance') {
            await fetchAdminAttendance();
        } else if (tabId === 'admin-ratings') {
            await fetchAllRatings();
        } else if (tabId === 'admin-expenses') {
            await fetchAllExpenses();
        } else if (tabId === 'admin-reports') {
            await fetchAdminReports();
        }
    } catch (error) {
        console.error(`Error loading data for tab ${tabId}:`, error);
    }
}

// --- Event Listeners ---

// Login form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const data = await apiRequest('/login', 'POST', { email, password });
        showMessage(loginMessage, data.message, 'success');
        await checkSession();
    } catch (error) {
        showMessage(loginMessage, error.message, 'error');
    }
});

// Logout button
logoutButton.addEventListener('click', async () => {
    try {
        await apiRequest('/logout', 'POST');
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        logout();
    }
});

// --- Volunteer Functions ---

async function fetchAssignedTasks() {
    try {
        const tasks = await apiRequest('/tasks/assigned', 'GET');
        assignedTasksList.innerHTML = '';
        
        if (tasks.length === 0) {
            assignedTasksList.innerHTML = '<p class="text-gray-600">No tasks assigned to you yet.</p>';
            return;
        }

        tasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4';
            taskCard.innerHTML = `
                <h4 class="text-lg font-semibold text-gray-800">${task.title}</h4>
                <p class="text-gray-700 text-sm mb-2">${task.description}</p>
                <div class="flex justify-between items-center text-xs text-gray-500">
                    <span><strong>Priority:</strong> ${task.priority}</span>
                    <span><strong>Deadline:</strong> ${task.deadline}</span>
                    <span><strong>Status:</strong> ${task.status}</span>
                </div>
                ${task.status !== 'Completed' ? `
                    <button onclick="updateTaskStatus('${task.task_id || 'unknown'}', 'Completed')" 
                            class="mt-2 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Mark Complete
                    </button>
                ` : ''}
            `;
            assignedTasksList.appendChild(taskCard);
        });
    } catch (error) {
        assignedTasksList.innerHTML = `<p class="text-red-600">Error loading tasks: ${error.message}</p>`;
    }
}

async function updateTaskStatus(taskId, status) {
    try {
        await apiRequest(`/tasks/update_status/${taskId}`, 'PUT', { status });
        await fetchAssignedTasks(); // Refresh the list
    } catch (error) {
        console.error('Error updating task status:', error);
    }
}

async function fetchMyAttendance() {
    try {
        const attendance = await apiRequest('/attendance/my', 'GET');
        myAttendanceHistory.innerHTML = '';
        
        if (attendance.length === 0) {
            myAttendanceHistory.innerHTML = '<p class="text-gray-600">No attendance records found.</p>';
            return;
        }

        const table = document.createElement('table');
        table.className = 'w-full border-collapse border border-gray-300';
        table.innerHTML = `
            <thead>
                <tr class="bg-gray-100">
                    <th class="border border-gray-300 px-4 py-2 text-left">Date</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">Task ID</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        
        const tbody = table.querySelector('tbody');
        attendance.forEach(log => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = log.date;
            row.insertCell().textContent = log.task_id;
        });
        myAttendanceHistory.appendChild(table);
    } catch (error) {
        myAttendanceHistory.innerHTML = `<p class="text-red-600">Error loading attendance history: ${error.message}</p>`;
    }
}

async function fetchMyRatings() {
    try {
        const ratings = await apiRequest('/ratings/my', 'GET');
        myRatingsList.innerHTML = '';
        if (ratings.length === 0) {
            myRatingsList.innerHTML = '<p class="text-gray-600">No ratings or feedback received yet.</p>';
            return;
        }
        ratings.forEach(rating => {
            const ratingCard = document.createElement('div');
            ratingCard.className = 'bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4';
            ratingCard.innerHTML = `
                <h4 class="text-lg font-semibold text-gray-800">Rating for Task: ${rating.task_id}</h4>
                <p class="text-gray-700 text-sm"><strong>Score:</strong> ${rating.score}/5</p>
                <p class="text-gray-700 text-sm"><strong>Comments:</strong> ${rating.comments}</p>
                <p class="text-gray-500 text-xs mt-2">Submitted by: ${rating.coordinator_id || rating.admin_id}</p>
            `;
            myRatingsList.appendChild(ratingCard);
        });
    } catch (error) {
        myRatingsList.innerHTML = `<p class="text-red-600">Error loading ratings: ${error.message}</p>`;
    }
}

async function fetchProfile() {
    try {
        const profile = await apiRequest('/profile', 'GET');
        profileNameInput.value = profile.name || '';
        profileEmailInput.value = profile.email || '';
        profileContactInput.value = profile.contact || '';
        profileNewPasswordInput.value = ''; // Clear password field
    } catch (error) {
        showMessage(profileMessage, `Error loading profile: ${error.message}`, 'error');
    }
}

updateProfileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = profileNameInput.value;
    const email = profileEmailInput.value;
    const contact = profileContactInput.value;
    const newPassword = profileNewPasswordInput.value;

    const updateData = { name, email, contact };
    if (newPassword) {
        updateData.new_password = newPassword;
    }

    try {
        const result = await apiRequest('/profile/update', 'PUT', updateData);
        showMessage(profileMessage, result.message, 'success');
        profileNewPasswordInput.value = ''; // Clear password field after update
        // Re-fetch profile to ensure UI is consistent with backend
        fetchProfile();
    } catch (error) {
        showMessage(profileMessage, error.message, 'error');
    }
});

// --- Coordinator Functions ---

// Submit attendance form
submitAttendanceForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskId = attendanceTaskIdSelect.value;
    const date = attendanceDateInput.value;

    try {
        await apiRequest('/attendance/submit', 'POST', { task_id: taskId, date });
        showMessage(attendanceMessage, 'Attendance submitted successfully!', 'success');
        submitAttendanceForm.reset();
        await fetchMyAttendance(); // Refresh attendance history
    } catch (error) {
        showMessage(attendanceMessage, error.message, 'error');
    }
});

// Assign task form
assignTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskId = assignTaskIdSelect.value;
    const volunteerId = assignVolunteerIdSelect.value;
    const priority = assignPrioritySelect.value;
    const deadline = assignDeadlineInput.value;

    try {
        await apiRequest('/tasks/assign_volunteer', 'POST', {
            task_id: taskId,
            volunteer_id: volunteerId,
            priority,
            deadline
        });
        showMessage(assignTaskMessage, 'Task assigned successfully!', 'success');
        assignTaskForm.reset();
    } catch (error) {
        showMessage(assignTaskMessage, error.message, 'error');
    }
});

// Reassign task form
reassignTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskId = reassignTaskSelect.value;
    const volunteerId = reassignVolunteerIdSelect.value;

    try {
        await apiRequest(`/tasks/reassign_volunteer/${taskId}`, 'PUT', {
            volunteer_id: volunteerId
        });
        showMessage(reassignTaskMessage, 'Task reassigned successfully!', 'success');
        reassignTaskForm.reset();
    } catch (error) {
        showMessage(reassignTaskMessage, error.message, 'error');
    }
});

async function populateVolunteerSelects() {
    try {
        const volunteers = await apiRequest('/volunteers', 'GET');
        assignVolunteerIdSelect.innerHTML = '<option value="">Select a Volunteer</option>';
        reassignVolunteerIdSelect.innerHTML = '<option value="">Select a Volunteer</option>';
        ratingVolunteerIdSelect.innerHTML = '<option value="">Select a Volunteer</option>'; // For rating form
        adminRatingVolunteerIdSelect.innerHTML = '<option value="">Select a Volunteer</option>'; // For admin rating form

        volunteers.forEach(vol => {
            const option1 = document.createElement('option');
            option1.value = vol.user_id;
            option1.textContent = vol.name;
            assignVolunteerIdSelect.appendChild(option1);

            const option2 = document.createElement('option');
            option2.value = vol.user_id;
            option2.textContent = vol.name;
            reassignVolunteerIdSelect.appendChild(option2);

            const option3 = document.createElement('option');
            option3.value = vol.user_id;
            option3.textContent = vol.name;
            ratingVolunteerIdSelect.appendChild(option3);

            const option4 = document.createElement('option');
            option4.value = vol.user_id;
            option4.textContent = vol.name;
            adminRatingVolunteerIdSelect.appendChild(option4);
        });
    } catch (error) {
        console.error('Error populating volunteer selects:', error);
    }
}

async function populateCoordinatorTaskSelects() {
    try {
        // Coordinators can assign tasks that are not yet assigned
        const allTasks = await apiRequest('/tasks', 'GET');
        const unassignedTasks = allTasks.filter(task => !task.assigned_to);

        assignTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
        unassignedTasks.forEach(task => {
            const option = document.createElement('option');
            option.value = task.task_id;
            option.textContent = task.title;
            assignTaskIdSelect.appendChild(option);
        });

        // For reassign, they can reassign any task (though backend might restrict to their supervised tasks)
        reassignTaskSelect.innerHTML = '<option value="">Select a Task</option>';
        allTasks.forEach(task => {
            const option = document.createElement('option');
            option.value = task.task_id;
            option.textContent = `${task.title} (Assigned to: ${task.assigned_to || 'None'})`;
            reassignTaskSelect.appendChild(option);
        });

        // For rating tasks, they can rate tasks assigned to volunteers
        ratingTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
        allTasks.forEach(task => {
            const option = document.createElement('option');
            option.value = task.task_id;
            option.textContent = `${task.title} (Status: ${task.status})`;
            ratingTaskIdSelect.appendChild(option);
        });

         // For admin rating tasks
         adminRatingTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
         allTasks.forEach(task => {
             const option = document.createElement('option');
             option.value = task.task_id;
             option.textContent = `${task.title} (Status: ${task.status})`;
             adminRatingTaskIdSelect.appendChild(option);
         });

         // For expense logging
         expenseTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
         allTasks.forEach(task => {
             const option = document.createElement('option');
             option.value = task.task_id;
             option.textContent = `${task.title}`;
             expenseTaskIdSelect.appendChild(option);
         });


    } catch (error) {
        console.error('Error populating coordinator task selects:', error);
    }
}

assignTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskId = assignTaskIdSelect.value;
    const volunteerId = assignVolunteerIdSelect.value;
    const priority = assignPrioritySelect.value;
    const deadline = assignDeadlineInput.value;

    try {
        const result = await apiRequest('/tasks/assign_volunteer', 'POST', { task_id: taskId, volunteer_id: volunteerId, priority, deadline });
        showMessage(assignTaskMessage, result.message, 'success');
        assignTaskForm.reset();
        populateCoordinatorTaskSelects(); // Refresh tasks
    } catch (error) {
        showMessage(assignTaskMessage, error.message, 'error');
    }
});

reassignTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskId = reassignTaskSelect.value;
    const newVolunteerId = reassignVolunteerIdSelect.value;

    try {
        const result = await apiRequest(`/tasks/reassign_volunteer/${taskId}`, 'PUT', { volunteer_id: newVolunteerId });
        showMessage(reassignTaskMessage, result.message, 'success');
        reassignTaskForm.reset();
        populateCoordinatorTaskSelects(); // Refresh tasks
    } catch (error) {
        showMessage(reassignTaskMessage, error.message, 'error');
    }
});

async function fetchCoordinatorAttendance() {
    try {
        const volunteerId = coordAttendanceVolunteerFilter.value;
        const dateFilter = coordAttendanceDateFilter.value;
        const queryParams = new URLSearchParams();
        if (volunteerId) queryParams.append('volunteer_id', volunteerId);
        if (dateFilter) queryParams.append('date', dateFilter);

        const attendance = await apiRequest(`/attendance?${queryParams.toString()}`, 'GET');
        coordinatorAttendanceList.innerHTML = '';
        if (attendance.length === 0) {
            coordinatorAttendanceList.innerHTML = '<p class="text-gray-600">No attendance logs found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>Date</th>
                    <th>User ID</th>
                    <th>Task ID</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        attendance.forEach(log => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = log.date;
            row.insertCell().textContent = log.user_id;
            row.insertCell().textContent = log.task_id;
        });
        coordinatorAttendanceList.appendChild(table);
    } catch (error) {
        coordinatorAttendanceList.innerHTML = `<p class="text-red-600">Error loading attendance logs: ${error.message}</p>`;
    }
}

coordAttendanceFilterBtn.addEventListener('click', fetchCoordinatorAttendance);
coordAttendanceResetBtn.addEventListener('click', () => {
    coordAttendanceVolunteerFilter.value = '';
    coordAttendanceDateFilter.value = '';
    fetchCoordinatorAttendance();
});

async function populateCoordinatorRatingSelects() {
    await populateVolunteerSelects(); // Reuse for volunteer select
    await populateCoordinatorTaskSelects(); // Reuse for task select
}

submitRatingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const volunteerId = ratingVolunteerIdSelect.value;
    const taskId = ratingTaskIdSelect.value;
    const score = parseInt(ratingScoreInput.value);
    const comments = ratingCommentsTextarea.value;

    try {
        const result = await apiRequest('/ratings/add', 'POST', { volunteer_id: volunteerId, task_id: taskId, score, comments });
        showMessage(submitRatingMessage, result.message, 'success');
        submitRatingForm.reset();
        fetchMySubmittedRatings(); // Refresh list
    } catch (error) {
        showMessage(submitRatingMessage, error.message, 'error');
    }
});

async function fetchMySubmittedRatings() {
    try {
        const ratings = await apiRequest('/ratings?submitted_by=me', 'GET');
        mySubmittedRatingsList.innerHTML = '';
        if (ratings.length === 0) {
            mySubmittedRatingsList.innerHTML = '<p class="text-gray-600">No ratings submitted by you.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>Rating ID</th>
                    <th>Volunteer ID</th>
                    <th>Task ID</th>
                    <th>Score</th>
                    <th>Comments</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        ratings.forEach(rating => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = rating.rating_id;
            row.insertCell().textContent = rating.volunteer_id;
            row.insertCell().textContent = rating.task_id;
            row.insertCell().textContent = rating.score;
            row.insertCell().textContent = rating.comments;
            const actionsCell = row.insertCell();
            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.className = 'btn-secondary text-xs mr-2';
            editButton.onclick = () => openEditRatingModal(rating);
            actionsCell.appendChild(editButton);
        });
        mySubmittedRatingsList.appendChild(table);
    } catch (error) {
        mySubmittedRatingsList.innerHTML = `<p class="text-red-600">Error loading submitted ratings: ${error.message}</p>`;
    }
}

// Placeholder for edit rating modal (simple prompt for now)
function openEditRatingModal(rating) {
    const newScore = prompt(`Edit score for rating ${rating.rating_id} (current: ${rating.score}):`);
    const newComments = prompt(`Edit comments for rating ${rating.rating_id} (current: ${rating.comments}):`);

    if (newScore !== null || newComments !== null) {
        updateRating(rating.rating_id, newScore, newComments);
    }
}

async function updateRating(ratingId, newScore, newComments) {
    const updateData = {};
    if (newScore !== null && !isNaN(parseInt(newScore))) {
        updateData.score = parseInt(newScore);
    }
    if (newComments !== null) {
        updateData.comments = newComments;
    }

    if (Object.keys(updateData).length === 0) {
        showMessage(mySubmittedRatingsList.parentElement.querySelector('.message-box') || mySubmittedRatingsList, 'No changes to update.', 'error');
        return;
    }

    try {
        const result = await apiRequest(`/ratings/${ratingId}`, 'PUT', updateData);
        showMessage(mySubmittedRatingsList.parentElement.querySelector('.message-box') || mySubmittedRatingsList, result.message, 'success');
        fetchMySubmittedRatings(); // Refresh list
    } catch (error) {
        showMessage(mySubmittedRatingsList.parentElement.querySelector('.message-box') || mySubmittedRatingsList, error.message, 'error');
    }
}


async function fetchCoordinatorExpenses() {
    try {
        const taskId = coordExpenseTaskFilter.value;
        const category = coordExpenseCategoryFilter.value;
        const queryParams = new URLSearchParams();
        if (taskId) queryParams.append('task_id', taskId);
        if (category) queryParams.append('category', category);

        const expenses = await apiRequest(`/expenses?${queryParams.toString()}`, 'GET');
        coordinatorExpensesList.innerHTML = '';
        if (expenses.length === 0) {
            coordinatorExpensesList.innerHTML = '<p class="text-gray-600">No expense logs found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>Expense ID</th>
                    <th>Task ID</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Logged By</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        expenses.forEach(exp => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = exp.expense_id;
            row.insertCell().textContent = exp.task_id;
            row.insertCell().textContent = `$${exp.amount.toFixed(2)}`;
            row.insertCell().textContent = exp.category;
            row.insertCell().textContent = exp.logged_by;
        });
        coordinatorExpensesList.appendChild(table);
    } catch (error) {
        coordinatorExpensesList.innerHTML = `<p class="text-red-600">Error loading expenses: ${error.message}</p>`;
    }
}

coordExpenseFilterBtn.addEventListener('click', fetchCoordinatorExpenses);
coordExpenseResetBtn.addEventListener('click', () => {
    coordExpenseTaskFilter.value = '';
    coordExpenseCategoryFilter.value = '';
    fetchCoordinatorExpenses();
});

async function fetchCoordinatorReports() {
    try {
        // Attendance Report
        const attendanceReport = await apiRequest('/reports/attendance', 'GET');
        reportCoordAttendance.innerHTML = '<h5 class="font-semibold mb-2">Attendance Report:</h5>';
        if (attendanceReport.length === 0) {
            reportCoordAttendance.innerHTML += '<p class="text-gray-600">No attendance data.</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
            table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Date</th><th>User ID</th><th>Task ID</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
            const tbody = table.querySelector('tbody');
            attendanceReport.forEach(log => {
                const row = tbody.insertRow();
                row.className = 'table-row';
                row.insertCell().textContent = log.date;
                row.insertCell().textContent = log.user_id;
                row.insertCell().textContent = log.task_id;
            });
            reportCoordAttendance.appendChild(table);
        }

        // Assignment Report
        const assignmentReport = await apiRequest('/reports/assignments', 'GET');
        reportCoordAssignments.innerHTML = '<h5 class="font-semibold mb-2">Assignment Report:</h5>';
        if (assignmentReport.length === 0) {
            reportCoordAssignments.innerHTML += '<p class="text-gray-600">No assignment data.</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
            table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task</th><th>Assigned To</th><th>Role</th><th>Deadline</th><th>Status</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
            const tbody = table.querySelector('tbody');
            assignmentReport.forEach(item => {
                const row = tbody.insertRow();
                row.className = 'table-row';
                row.insertCell().textContent = item.title;
                row.insertCell().textContent = `${item.assigned_to_name} (${item.assigned_to_id})`;
                row.insertCell().textContent = item.role;
                row.insertCell().textContent = item.deadline;
                row.insertCell().textContent = item.status;
            });
            reportCoordAssignments.appendChild(table);
        }

        // Expense Report
        const expenseReport = await apiRequest('/reports/expenses', 'GET');
        reportCoordExpenses.innerHTML = '<h5 class="font-semibold mb-2">Expense Report:</h5>';
        if (expenseReport.length === 0) {
            reportCoordExpenses.innerHTML += '<p class="text-gray-600">No expense data.</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
            table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task ID</th><th>Amount</th><th>Category</th><th>Logged By</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
            const tbody = table.querySelector('tbody');
            expenseReport.forEach(item => {
                const row = tbody.insertRow();
                row.className = 'table-row';
                row.insertCell().textContent = item.task_id;
                row.insertCell().textContent = `$${item.amount.toFixed(2)}`;
                row.insertCell().textContent = item.category;
                row.insertCell().textContent = item.logged_by;
            });
            reportCoordExpenses.appendChild(table);
        }

    } catch (error) {
        console.error('Error fetching coordinator reports:', error);
        reportCoordAttendance.innerHTML = `<p class="text-red-600">Error loading attendance report: ${error.message}</p>`;
        reportCoordAssignments.innerHTML = `<p class="text-red-600">Error loading assignment report: ${error.message}</p>`;
        reportCoordExpenses.innerHTML = `<p class="text-red-600">Error loading expense report: ${error.message}</p>`;
    }
}


// --- Admin Functions ---

createUserForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = createUserNameInput.value;
    const email = createUserEmailInput.value;
    const password = createUserPasswordInput.value;
    const role = createUserRoleSelect.value;
    const contact = createUserContactInput.value;

    try {
        const result = await apiRequest('/users/create', 'POST', { name, email, password, role, contact });
        showMessage(createUserMessage, result.message, 'success');
        createUserForm.reset();
        fetchAllUsers(); // Refresh user list
    } catch (error) {
        showMessage(createUserMessage, error.message, 'error');
    }
});

async function fetchAllUsers() {
    try {
        const users = await apiRequest('/users', 'GET');
        allUsersList.innerHTML = '';
        if (users.length === 0) {
            allUsersList.innerHTML = '<p class="text-gray-600">No users found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Contact</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        users.forEach(user => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = user.user_id;
            row.insertCell().textContent = user.name;
            row.insertCell().textContent = user.email;
            row.insertCell().textContent = user.role;
            row.insertCell().textContent = user.contact || 'N/A';
            const actionsCell = row.insertCell();

            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.className = 'btn-secondary text-xs mr-2';
            editButton.onclick = () => openEditUserModal(user);
            actionsCell.appendChild(editButton);

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.className = 'bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs';
            deleteButton.onclick = () => deleteUser(user.user_id);
            actionsCell.appendChild(deleteButton);
        });
        allUsersList.appendChild(table);
    } catch (error) {
        allUsersList.innerHTML = `<p class="text-red-600">Error loading users: ${error.message}</p>`;
    }
}

function openEditUserModal(user) {
    const newName = prompt(`Edit name for ${user.name} (current: ${user.name}):`, user.name);
    const newEmail = prompt(`Edit email for ${user.name} (current: ${user.email}):`, user.email);
    const newRole = prompt(`Edit role for ${user.name} (current: ${user.role}). Options: volunteer, coordinator, admin:`, user.role);
    const newContact = prompt(`Edit contact for ${user.name} (current: ${user.contact}):`, user.contact);
    const newPassword = prompt(`Enter new password for ${user.name} (leave blank to keep current):`);

    const updateData = {};
    if (newName !== null && newName !== user.name) updateData.name = newName;
    if (newEmail !== null && newEmail !== user.email) updateData.email = newEmail;
    if (newRole !== null && newRole !== user.role) updateData.role = newRole;
    if (newContact !== null && newContact !== user.contact) updateData.contact = newContact;
    if (newPassword !== null && newPassword !== '') updateData.password = newPassword;

    if (Object.keys(updateData).length > 0) {
        updateUser(user.user_id, updateData);
    } else {
        showMessage(allUsersList.parentElement.querySelector('.message-box') || allUsersList, 'No changes detected.', 'error');
    }
}

async function updateUser(userId, updateData) {
    try {
        const result = await apiRequest(`/users/${userId}`, 'PUT', updateData);
        showMessage(allUsersList.parentElement.querySelector('.message-box') || allUsersList, result.message, 'success');
        fetchAllUsers(); // Refresh list
    } catch (error) {
        showMessage(allUsersList.parentElement.querySelector('.message-box') || allUsersList, error.message, 'error');
    }
}

async function deleteUser(userId) {
    if (confirm(`Are you sure you want to delete user ${userId}?`)) { // Using confirm for simplicity, replace with custom modal
        try {
            const result = await apiRequest(`/users/${userId}`, 'DELETE');
            showMessage(allUsersList.parentElement.querySelector('.message-box') || allUsersList, result.message, 'success');
            fetchAllUsers(); // Refresh list
        } catch (error) {
            showMessage(allUsersList.parentElement.querySelector('.message-box') || allUsersList, error.message, 'error');
        }
    }
}

async function populateAdminTaskAssignToSelect() {
    try {
        const users = await apiRequest('/users', 'GET');
        newTaskAssignToSelect.innerHTML = '<option value="">None</option>';
        users.forEach(user => {
            if (user.role === 'volunteer' || user.role === 'coordinator') {
                const option = document.createElement('option');
                option.value = user.user_id;
                option.textContent = `${user.name} (${user.role})`;
                newTaskAssignToSelect.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Error populating admin task assign-to select:', error);
    }
}

createTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = newTaskTitleInput.value;
    const description = newTaskDescriptionTextarea.value;
    const deadline = newTaskDeadlineInput.value;
    const priority = newTaskPrioritySelect.value;
    const assignedTo = newTaskAssignToSelect.value || null;

    try {
        const result = await apiRequest('/tasks/create', 'POST', { title, description, deadline, priority, assigned_to: assignedTo });
        showMessage(createTaskMessage, result.message, 'success');
        createTaskForm.reset();
        fetchAllTasks(); // Refresh list
        populateCoordinatorTaskSelects(); // Refresh for coordinator
    } catch (error) {
        showMessage(createTaskMessage, error.message, 'error');
    }
});

async function fetchAllTasks() {
    try {
        const statusFilter = adminTaskStatusFilter.value;
        const queryParams = new URLSearchParams();
        if (statusFilter) queryParams.append('status', statusFilter);

        const tasks = await apiRequest(`/tasks?${queryParams.toString()}`, 'GET');
        allTasksList.innerHTML = '';
        if (tasks.length === 0) {
            allTasksList.innerHTML = '<p class="text-gray-600">No tasks found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Deadline</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Assigned To</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        tasks.forEach(task => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = task.task_id;
            row.insertCell().textContent = task.title;
            row.insertCell().textContent = task.description;
            row.insertCell().textContent = task.deadline;
            row.insertCell().textContent = task.priority;
            row.insertCell().textContent = task.status;
            row.insertCell().textContent = task.assigned_to || 'None';
            const actionsCell = row.insertCell();

            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.className = 'btn-secondary text-xs mr-2';
            editButton.onclick = () => openEditTaskModal(task);
            actionsCell.appendChild(editButton);

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.className = 'bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs';
            deleteButton.onclick = () => deleteTask(task.task_id);
            actionsCell.appendChild(deleteButton);
        });
        allTasksList.appendChild(table);
    } catch (error) {
        allTasksList.innerHTML = `<p class="text-red-600">Error loading tasks: ${error.message}</p>`;
    }
}

adminTaskFilterBtn.addEventListener('click', fetchAllTasks);
adminTaskResetBtn.addEventListener('click', () => {
    adminTaskStatusFilter.value = '';
    fetchAllTasks();
});

function openEditTaskModal(task) {
    const newTitle = prompt(`Edit title for ${task.title} (current: ${task.title}):`, task.title);
    const newDescription = prompt(`Edit description (current: ${task.description}):`, task.description);
    const newDeadline = prompt(`Edit deadline (current: ${task.deadline}):`, task.deadline);
    const newPriority = prompt(`Edit priority (current: ${task.priority}):`, task.priority);
    const newStatus = prompt(`Edit status (current: ${task.status}). Options: Pending, In Progress, Completed:`, task.status);
    const newAssignedTo = prompt(`Edit assigned to (current: ${task.assigned_to || 'None'}). Enter User ID or leave blank:`, task.assigned_to || '');

    const updateData = {};
    if (newTitle !== null && newTitle !== task.title) updateData.title = newTitle;
    if (newDescription !== null && newDescription !== task.description) updateData.description = newDescription;
    if (newDeadline !== null && newDeadline !== task.deadline) updateData.deadline = newDeadline;
    if (newPriority !== null && newPriority !== task.priority) updateData.priority = newPriority;
    if (newStatus !== null && newStatus !== task.status) updateData.status = newStatus;
    if (newAssignedTo !== null) updateData.assigned_to = newAssignedTo || null;

    if (Object.keys(updateData).length > 0) {
        updateTask(task.task_id, updateData);
    } else {
        showMessage(allTasksList.parentElement.querySelector('.message-box') || allTasksList, 'No changes detected.', 'error');
    }
}

async function updateTask(taskId, updateData) {
    try {
        const result = await apiRequest(`/tasks/${taskId}`, 'PUT', updateData);
        showMessage(allTasksList.parentElement.querySelector('.message-box') || allTasksList, result.message, 'success');
        fetchAllTasks(); // Refresh list
        fetchAssignedTasks(); // Refresh volunteer's view
    } catch (error) {
        showMessage(allTasksList.parentElement.querySelector('.message-box') || allTasksList, error.message, 'error');
    }
}

async function deleteTask(taskId) {
    if (confirm(`Are you sure you want to delete task ${taskId}?`)) { // Using confirm for simplicity, replace with custom modal
        try {
            const result = await apiRequest(`/tasks/${taskId}`, 'DELETE');
            showMessage(allTasksList.parentElement.querySelector('.message-box') || allTasksList, result.message, 'success');
            fetchAllTasks(); // Refresh list
        } catch (error) {
            showMessage(allTasksList.parentElement.querySelector('.message-box') || allTasksList, error.message, 'error');
        }
    }
}

async function fetchAdminAttendance() {
    try {
        const volunteerId = adminAttendanceVolunteerFilter.value;
        const dateFilter = adminAttendanceDateFilter.value;
        const queryParams = new URLSearchParams();
        if (volunteerId) queryParams.append('volunteer_id', volunteerId);
        if (dateFilter) queryParams.append('date', dateFilter);

        const attendance = await apiRequest(`/attendance?${queryParams.toString()}`, 'GET');
        adminAllAttendanceList.innerHTML = '';
        if (attendance.length === 0) {
            adminAllAttendanceList.innerHTML = '<p class="text-gray-600">No attendance logs found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>Date</th>
                    <th>User ID</th>
                    <th>Task ID</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        attendance.forEach(log => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = log.date;
            row.insertCell().textContent = log.user_id;
            row.insertCell().textContent = log.task_id;
        });
        adminAllAttendanceList.appendChild(table);
    } catch (error) {
        adminAllAttendanceList.innerHTML = `<p class="text-red-600">Error loading attendance logs: ${error.message}</p>`;
    }
}

adminAttendanceFilterBtn.addEventListener('click', fetchAdminAttendance);
adminAttendanceResetBtn.addEventListener('click', () => {
    adminAttendanceVolunteerFilter.value = '';
    adminAttendanceDateFilter.value = '';
    fetchAdminAttendance();
});

getAbsenteesBtn.addEventListener('click', fetchAbsentees);
async function fetchAbsentees() {
    try {
        const absentees = await apiRequest('/attendance/absentees', 'GET');
        adminAbsenteesList.innerHTML = '';
        if (absentees.length === 0) {
            adminAbsenteesList.innerHTML = '<p class="text-gray-600">No absentees found for today.</p>';
            return;
        }
        const ul = document.createElement('ul');
        ul.className = 'list-disc list-inside space-y-1 text-gray-700';
        absentees.forEach(absentee => {
            const li = document.createElement('li');
            li.textContent = `${absentee.name} (${absentee.user_id}, ${absentee.email})`;
            ul.appendChild(li);
        });
        adminAbsenteesList.appendChild(ul);
    } catch (error) {
        adminAbsenteesList.innerHTML = `<p class="text-red-600">Error loading absentees: ${error.message}</p>`;
    }
}

adminSubmitRatingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const volunteerId = adminRatingVolunteerIdSelect.value;
    const taskId = adminRatingTaskIdSelect.value;
    const score = parseInt(adminRatingScoreInput.value);
    const comments = adminRatingCommentsTextarea.value;

    try {
        const result = await apiRequest('/ratings/add', 'POST', { volunteer_id: volunteerId, task_id: taskId, score, comments });
        showMessage(adminSubmitRatingMessage, result.message, 'success');
        adminSubmitRatingForm.reset();
        fetchAllRatings(); // Refresh list
    } catch (error) {
        showMessage(adminSubmitRatingMessage, error.message, 'error');
    }
});

async function fetchAllRatings() {
    try {
        const ratings = await apiRequest('/ratings', 'GET');
        adminAllRatingsList.innerHTML = '';
        if (ratings.length === 0) {
            adminAllRatingsList.innerHTML = '<p class="text-gray-600">No ratings found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>Rating ID</th>
                    <th>Volunteer ID</th>
                    <th>Task ID</th>
                    <th>Score</th>
                    <th>Comments</th>
                    <th>Submitted By</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        ratings.forEach(rating => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = rating.rating_id;
            row.insertCell().textContent = rating.volunteer_id;
            row.insertCell().textContent = rating.task_id;
            row.insertCell().textContent = rating.score;
            row.insertCell().textContent = rating.comments;
            row.insertCell().textContent = rating.coordinator_id || rating.admin_id || 'N/A';
            const actionsCell = row.insertCell();

            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.className = 'btn-secondary text-xs mr-2';
            editButton.onclick = () => openEditRatingModal(rating); // Reusing coordinator's modal
            actionsCell.appendChild(editButton);

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.className = 'bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs';
            deleteButton.onclick = () => deleteRating(rating.rating_id);
            actionsCell.appendChild(deleteButton);
        });
        adminAllRatingsList.appendChild(table);
    } catch (error) {
        adminAllRatingsList.innerHTML = `<p class="text-red-600">Error loading ratings: ${error.message}</p>`;
    }
}

async function deleteRating(ratingId) {
    if (confirm(`Are you sure you want to delete rating ${ratingId}?`)) {
        try {
            const result = await apiRequest(`/ratings/${ratingId}`, 'DELETE');
            showMessage(adminAllRatingsList.parentElement.querySelector('.message-box') || adminAllRatingsList, result.message, 'success');
            fetchAllRatings(); // Refresh list
        } catch (error) {
            showMessage(adminAllRatingsList.parentElement.querySelector('.message-box') || adminAllRatingsList, error.message, 'error');
        }
    }
}

logExpenseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskId = expenseTaskIdSelect.value;
    const amount = parseFloat(expenseAmountInput.value);
    const category = expenseCategoryInput.value;

    try {
        const result = await apiRequest('/expenses/log', 'POST', { task_id: taskId, amount, category });
        showMessage(logExpenseMessage, result.message, 'success');
        logExpenseForm.reset();
        fetchAllExpenses(); // Refresh list
    } catch (error) {
        showMessage(logExpenseMessage, error.message, 'error');
    }
});

async function fetchAllExpenses() {
    try {
        const taskId = adminExpenseTaskFilter.value;
        const category = adminExpenseCategoryFilter.value;
        const queryParams = new URLSearchParams();
        if (taskId) queryParams.append('task_id', taskId);
        if (category) queryParams.append('category', category);

        const expenses = await apiRequest(`/expenses?${queryParams.toString()}`, 'GET');
        adminAllExpensesList.innerHTML = '';
        if (expenses.length === 0) {
            adminAllExpensesList.innerHTML = '<p class="text-gray-600">No expenses found.</p>';
            return;
        }
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
        table.innerHTML = `
            <thead class="bg-gray-100">
                <tr class="table-header">
                    <th>Expense ID</th>
                    <th>Task ID</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Logged By</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            </tbody>
        `;
        const tbody = table.querySelector('tbody');
        expenses.forEach(exp => {
            const row = tbody.insertRow();
            row.className = 'table-row';
            row.insertCell().textContent = exp.expense_id;
            row.insertCell().textContent = exp.task_id;
            row.insertCell().textContent = `$${exp.amount.toFixed(2)}`;
            row.insertCell().textContent = exp.category;
            row.insertCell().textContent = exp.logged_by;
            const actionsCell = row.insertCell();

            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.className = 'btn-secondary text-xs mr-2';
            editButton.onclick = () => openEditExpenseModal(exp);
            actionsCell.appendChild(editButton);

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.className = 'bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs';
            deleteButton.onclick = () => deleteExpense(exp.expense_id);
            actionsCell.appendChild(deleteButton);
        });
        adminAllExpensesList.appendChild(table);
    } catch (error) {
        adminAllExpensesList.innerHTML = `<p class="text-red-600">Error loading expenses: ${error.message}</p>`;
    }
}

adminExpenseFilterBtn.addEventListener('click', fetchAllExpenses);
adminExpenseResetBtn.addEventListener('click', () => {
    adminExpenseTaskFilter.value = '';
    adminExpenseCategoryFilter.value = '';
    fetchAllExpenses();
});

function openEditExpenseModal(expense) {
    const newAmount = prompt(`Edit amount for expense ${expense.expense_id} (current: ${expense.amount}):`, expense.amount);
    const newCategory = prompt(`Edit category (current: ${expense.category}):`, expense.category);
    const newTaskID = prompt(`Edit Task ID (current: ${expense.task_id}):`, expense.task_id);

    const updateData = {};
    if (newAmount !== null && !isNaN(parseFloat(newAmount))) updateData.amount = parseFloat(newAmount);
    if (newCategory !== null && newCategory !== expense.category) updateData.category = newCategory;
    if (newTaskID !== null && newTaskID !== expense.task_id) updateData.task_id = newTaskID;

    if (Object.keys(updateData).length > 0) {
        updateExpense(expense.expense_id, updateData);
    } else {
        showMessage(adminAllExpensesList.parentElement.querySelector('.message-box') || adminAllExpensesList, 'No changes detected.', 'error');
    }
}

async function updateExpense(expenseId, updateData) {
    try {
        const result = await apiRequest(`/expenses/${expenseId}`, 'PUT', updateData);
        showMessage(adminAllExpensesList.parentElement.querySelector('.message-box') || adminAllExpensesList, result.message, 'success');
        fetchAllExpenses(); // Refresh list
    } catch (error) {
        showMessage(adminAllExpensesList.parentElement.querySelector('.message-box') || adminAllExpensesList, error.message, 'error');
    }
}

async function deleteExpense(expenseId) {
    if (confirm(`Are you sure you want to delete expense ${expenseId}?`)) {
        try {
            const result = await apiRequest(`/expenses/${expenseId}`, 'DELETE');
            showMessage(adminAllExpensesList.parentElement.querySelector('.message-box') || adminAllExpensesList, result.message, 'success');
            fetchAllExpenses(); // Refresh list
        } catch (error) {
            showMessage(adminAllExpensesList.parentElement.querySelector('.message-box') || adminAllExpensesList, error.message, 'error');
        }
    }
}

async function fetchAdminReports() {
    try {
        // Task Summary
        const taskSummary = await apiRequest('/reports/tasks', 'GET');
        reportAdminTasks.innerHTML = `
            <h5 class="font-semibold mb-2">Task Summary:</h5>
            <ul class="list-disc list-inside text-gray-700">
                <li>Total Tasks: ${taskSummary.total_tasks}</li>
                <li>Pending: ${taskSummary.pending}</li>
                <li>In Progress: ${taskSummary.in_progress}</li>
                <li>Completed: ${taskSummary.completed}</li>
                <li>Overdue: ${taskSummary.overdue}</li>
            </ul>
        `;

        // Attendance Report (reusing general attendance fetch)
        const attendanceReport = await apiRequest('/reports/attendance', 'GET');
        reportAdminAttendance.innerHTML = '<h5 class="font-semibold mb-2">Attendance Report:</h5>';
        if (attendanceReport.length === 0) {
            reportAdminAttendance.innerHTML += '<p class="text-gray-600">No attendance data.</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
            table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Date</th><th>User ID</th><th>Task ID</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
            const tbody = table.querySelector('tbody');
            attendanceReport.forEach(log => {
                const row = tbody.insertRow();
                row.className = 'table-row';
                row.insertCell().textContent = log.date;
                row.insertCell().textContent = log.user_id;
                row.insertCell().textContent = log.task_id;
            });
            reportAdminAttendance.appendChild(table);
        }

        // Ratings Summary
        const ratingsSummary = await apiRequest('/reports/ratings', 'GET');
        reportAdminRatings.innerHTML = '<h5 class="font-semibold mb-2">Ratings Summary:</h5>';
        if (Object.keys(ratingsSummary).length === 0) {
            reportAdminRatings.innerHTML += '<p class="text-gray-600">No ratings data.</p>';
        } else {
            const ul = document.createElement('ul');
            ul.className = 'list-disc list-inside text-gray-700 space-y-2';
            for (const volId in ratingsSummary) {
                const data = ratingsSummary[volId];
                const li = document.createElement('li');
                li.innerHTML = `<strong>${data.volunteer_name} (${volId}):</strong> Avg Score: ${data.average_score.toFixed(2)}/5, Comments: "${data.comments.join('", "')}"`;
                ul.appendChild(li);
            }
            reportAdminRatings.appendChild(ul);
        }

        // Expenses Report (reusing general expenses fetch)
        const expensesReport = await apiRequest('/reports/expenses', 'GET');
        reportAdminExpenses.innerHTML = '<h5 class="font-semibold mb-2">Expenses Report:</h5>';
        if (expensesReport.length === 0) {
            reportAdminExpenses.innerHTML += '<p class="text-gray-600">No expense data.</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
            table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task ID</th><th>Amount</th><th>Category</th><th>Logged By</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
            const tbody = table.querySelector('tbody');
            expensesReport.forEach(item => {
                const row = tbody.insertRow();
                row.className = 'table-row';
                row.insertCell().textContent = item.task_id;
                row.insertCell().textContent = `$${item.amount.toFixed(2)}`;
                row.insertCell().textContent = item.category;
                row.insertCell().textContent = item.logged_by;
            });
            reportAdminExpenses.appendChild(table);
        }

        // Assignment Logs (reusing general assignments fetch)
        const assignmentLogs = await apiRequest('/reports/assignments', 'GET');
        reportAdminAssignments.innerHTML = '<h5 class="font-semibold mb-2">Assignment Logs:</h5>';
        if (assignmentLogs.length === 0) {
            reportAdminAssignments.innerHTML += '<p class="text-gray-600">No assignment logs.</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm';
            table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task</th><th>Assigned To</th><th>Role</th><th>Deadline</th><th>Status</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
            const tbody = table.querySelector('tbody');
            assignmentLogs.forEach(item => {
                const row = tbody.insertRow();
                row.className = 'table-row';
                row.insertCell().textContent = item.title;
                row.insertCell().textContent = `${item.assigned_to_name} (${item.assigned_to_id})`;
                row.insertCell().textContent = item.role;
                row.insertCell().textContent = item.deadline;
                row.insertCell().textContent = item.status;
            });
            reportAdminAssignments.appendChild(table);
        }

    } catch (error) {
        console.error('Error fetching admin reports:', error);
        reportAdminTasks.innerHTML = `<p class="text-red-600">Error loading task summary: ${error.message}</p>`;
        reportAdminAttendance.innerHTML = `<p class="text-red-600">Error loading attendance report: ${error.message}</p>`;
        reportAdminRatings.innerHTML = `<p class="text-red-600">Error loading ratings summary: ${error.message}</p>`;
        reportAdminExpenses.innerHTML = `<p class="text-red-600">Error loading expenses report: ${error.message}</p>`;
        reportAdminAssignments.innerHTML = `<p class="text-red-600">Error loading assignment logs: ${error.message}</p>`;
    }
}


// --- Initial Load ---
document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is already logged in
    await checkSession();
    
    // Set today's date as default for attendance form
    const today = new Date().toISOString().split('T')[0];
    if (attendanceDateInput) {
        attendanceDateInput.value = today;
    }
});

// Make functions globally available for onclick handlers
window.updateTaskStatus = updateTaskStatus;
window.openEditUserModal = openEditUserModal;
window.updateUser = updateUser;
window.deleteUser = deleteUser;
window.openEditTaskModal = openEditTaskModal;
window.updateTask = updateTask;
window.deleteTask = deleteTask;
window.openEditRatingModal = openEditRatingModal;
window.updateRating = updateRating;
window.deleteRating = deleteRating;
window.openEditExpenseModal = openEditExpenseModal;
window.updateExpense = updateExpense;
window.deleteExpense = deleteExpense;

