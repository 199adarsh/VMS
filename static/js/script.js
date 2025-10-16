// Wrap in IIFE to prevent global conflicts
(function () {
  console.log("script.js loaded");
  const API_BASE_URL = window.location.origin; // Use current domain for API calls
  console.log("API_BASE_URL:", API_BASE_URL);

  // --- DOM Elements ---
  const loginSection = document.getElementById("login-section");
  const dashboardSection = document.getElementById("dashboard-section");
  const loginForm = document.getElementById("login-form");
  const loginMessage = document.getElementById("login-message");
  const userNameSpan = document.getElementById("user-name");
  const userRoleSpan = document.getElementById("user-role");
  const logoutButton = document.getElementById("logout-button");
  const dashboardTabs = document.getElementById("dashboard-tabs");
  const tabContents = document.querySelectorAll(".tab-content");

  // Volunteer Specific Elements
  const assignedTasksList = document.getElementById("assigned-tasks-list");
  const myAttendanceHistory = document.getElementById("my-attendance-history");
  const myRatingsList = document.getElementById("my-ratings-list");
  const updateProfileForm = document.getElementById("update-profile-form");
  const profileNameInput = document.getElementById("profile-name");
  const profileEmailInput = document.getElementById("profile-email");
  const profileContactInput = document.getElementById("profile-contact");
  const profileNewPasswordInput = document.getElementById(
    "profile-new-password"
  );
  const profileMessage = document.getElementById("profile-message");

  // Coordinator Specific Elements
  const assignTaskForm = document.getElementById("assign-task-form");
  const assignTaskIdSelect = document.getElementById("assign-task-id");
  const assignVolunteerIdSelect = document.getElementById(
    "assign-volunteer-id"
  );
  const assignPrioritySelect = document.getElementById("assign-priority");
  const assignDeadlineInput = document.getElementById("assign-deadline");
  const assignTaskMessage = document.getElementById("assign-task-message");
  const reassignTaskForm = document.getElementById("reassign-task-form");
  const reassignTaskSelect = document.getElementById("reassign-task-select");
  const reassignVolunteerIdSelect = document.getElementById(
    "reassign-volunteer-id"
  );
  const reassignTaskMessage = document.getElementById("reassign-task-message");
  const coordAttendanceVolunteerFilter = document.getElementById(
    "coord-attendance-volunteer-filter"
  );
  const coordAttendanceDateFilter = document.getElementById(
    "coord-attendance-date-filter"
  );
  const coordAttendanceFilterBtn = document.getElementById(
    "coord-attendance-filter-btn"
  );
  const coordAttendanceResetBtn = document.getElementById(
    "coord-attendance-reset-btn"
  );
  const coordinatorAttendanceList = document.getElementById(
    "coordinator-attendance-list"
  );
  const submitRatingForm = document.getElementById("submit-rating-form");
  const ratingVolunteerIdSelect = document.getElementById(
    "rating-volunteer-id"
  );
  const ratingTaskIdSelect = document.getElementById("rating-task-id");
  const ratingScoreInput = document.getElementById("rating-score");
  const ratingCommentsTextarea = document.getElementById("rating-comments");
  const submitRatingMessage = document.getElementById("submit-rating-message");
  const mySubmittedRatingsList = document.getElementById(
    "my-submitted-ratings-list"
  );
  const coordExpenseTaskFilter = document.getElementById(
    "coord-expense-task-filter"
  );
  const coordExpenseCategoryFilter = document.getElementById(
    "coord-expense-category-filter"
  );
  const coordExpenseFilterBtn = document.getElementById(
    "coord-expense-filter-btn"
  );
  const coordExpenseResetBtn = document.getElementById(
    "coord-expense-reset-btn"
  );
  const coordinatorExpensesList = document.getElementById(
    "coordinator-expenses-list"
  );
  const reportCoordAttendance = document.getElementById(
    "report-coord-attendance"
  );
  const reportCoordAssignments = document.getElementById(
    "report-coord-assignments"
  );
  const reportCoordExpenses = document.getElementById("report-coord-expenses");

  // Admin Specific Elements
  const createUserForm = document.getElementById("create-user-form");
  const createUserNameInput = document.getElementById("new-user-name");
  const createUserEmailInput = document.getElementById("new-user-email");
  const createUserPasswordInput = document.getElementById("new-user-password");
  const createUserRoleSelect = document.getElementById("new-user-role");
  const createUserContactInput = document.getElementById("new-user-contact");
  const createUserMessage = document.getElementById("create-user-message");
  const allUsersList = document.getElementById("all-users-list");
  const createTaskForm = document.getElementById("create-task-form");
  const newTaskTitleInput = document.getElementById("new-task-title");
  const newTaskDescriptionTextarea = document.getElementById(
    "new-task-description"
  );
  const newTaskDeadlineInput = document.getElementById("new-task-deadline");
  const newTaskPrioritySelect = document.getElementById("new-task-priority");
  const newTaskAssignToSelect = document.getElementById("new-task-assign-to");
  const createTaskMessage = document.getElementById("create-task-message");
  const adminTaskStatusFilter = document.getElementById(
    "admin-task-status-filter"
  );
  const adminTaskFilterBtn = document.getElementById("admin-task-filter-btn");
  const adminTaskResetBtn = document.getElementById("admin-task-reset-btn");
  const allTasksList = document.getElementById("all-tasks-list");
  const adminAttendanceVolunteerFilter = document.getElementById(
    "admin-attendance-volunteer-filter"
  );
  const adminAttendanceDateFilter = document.getElementById(
    "admin-attendance-date-filter"
  );
  const adminAttendanceFilterBtn = document.getElementById(
    "admin-attendance-filter-btn"
  );
  const adminAttendanceResetBtn = document.getElementById(
    "admin-attendance-reset-btn"
  );
  const adminAllAttendanceList = document.getElementById(
    "admin-all-attendance-list"
  );
  const getAbsenteesBtn = document.getElementById("get-absentees-btn");
  const adminAbsenteesList = document.getElementById("admin-absentees-list");
  const adminSubmitRatingForm = document.getElementById(
    "admin-submit-rating-form"
  );
  const adminRatingVolunteerIdSelect = document.getElementById(
    "admin-rating-volunteer-id"
  );
  const adminRatingTaskIdSelect = document.getElementById(
    "admin-rating-task-id"
  );
  const adminRatingScoreInput = document.getElementById("admin-rating-score");
  const adminRatingCommentsTextarea = document.getElementById(
    "admin-rating-comments"
  );
  const adminSubmitRatingMessage = document.getElementById(
    "admin-submit-rating-message"
  );
  const adminAllRatingsList = document.getElementById("admin-all-ratings-list");
  const logExpenseForm = document.getElementById("log-expense-form");
  const expenseTaskIdSelect = document.getElementById("expense-task-id");
  const expenseAmountInput = document.getElementById("expense-amount");
  const expenseCategoryInput = document.getElementById("expense-category");
  const logExpenseMessage = document.getElementById("log-expense-message");
  const adminExpenseTaskFilter = document.getElementById(
    "admin-expense-task-filter"
  );
  const adminExpenseCategoryFilter = document.getElementById(
    "admin-expense-category-filter"
  );
  const adminExpenseFilterBtn = document.getElementById(
    "admin-expense-filter-btn"
  );
  const adminExpenseResetBtn = document.getElementById(
    "admin-expense-reset-btn"
  );
  const adminAllExpensesList = document.getElementById(
    "admin-all-expenses-list"
  );
  const reportAdminTasks = document.getElementById("report-admin-tasks");
  const reportAdminAttendance = document.getElementById(
    "report-admin-attendance"
  );
  const reportAdminRatings = document.getElementById("report-admin-ratings");
  const reportAdminExpenses = document.getElementById("report-admin-expenses");
  const reportAdminAssignments = document.getElementById(
    "report-admin-assignments"
  );

  // --- Utility Functions ---

  /**
   * Displays a message in a designated message box.
   * @param {HTMLElement} element The message box element.
   * @param {string} message The message to display.
   * @param {string} type The type of message ('success' or 'error').
   */
  function showMessage(element, message, type = "success") {
    if (!element) return;

    element.textContent = message;
    element.className = `message-box ${type}`;
    element.classList.remove("hidden");

    // Auto-hide after 5 seconds
    setTimeout(() => {
      element.classList.add("hidden");
    }, 5000);
  }

  /**
   * Makes an API request to the backend.
   * @param {string} endpoint The API endpoint.
   * @param {string} method The HTTP method.
   * @param {Object} data The data to send (optional).
   * @returns {Promise} The response data.
   */
  async function apiRequest(endpoint, method = "GET", data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Include cookies for session management
    };

    if (data && (method === "POST" || method === "PUT")) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

    // Check if response is JSON before parsing
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error("Non-JSON response received:", text);
      throw new Error(
        `Server returned non-JSON response: ${response.status} ${response.statusText}`
      );
    }

    const responseData = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        logout();
      }
      throw new Error(responseData.message || "An API error occurred.");
    }
    return responseData;
  }

  async function checkSession() {
    try {
      const sessionData = await apiRequest("/session/check", "GET");
      if (sessionData.logged_in) {
        if (loginSection) loginSection.classList.add("hidden");
        if (dashboardSection) dashboardSection.classList.remove("hidden");
        updateUIForRole(sessionData.role);
        await loadUserProfile();
      }
    } catch (error) {
      console.log("No active session");
    }
  }

  /**
   * Loads user profile data.
   */
  async function loadUserProfile() {
    try {
      const profile = await apiRequest("/profile", "GET");
      userNameSpan.textContent = profile.name || "User";
      userRoleSpan.textContent = profile.role || "Unknown";
    } catch (error) {
      console.error("Error loading profile:", error);
    }
  }

  /**
   * Logs out the user and resets the UI.
   */
  function logout() {
    // Stop dashboard auto-refresh when logging out
    if (dashboardAutoRefreshInterval) {
      clearInterval(dashboardAutoRefreshInterval);
      dashboardAutoRefreshInterval = null;
    }
    if (loginSection) loginSection.classList.remove("hidden");
    if (dashboardSection) dashboardSection.classList.add("hidden");
  }

  /**
   * Updates the UI based on user role.
   * @param {string} role The user's role.
   */
  function updateUIForRole(role) {
    // Hide all tab buttons and tab-content by default
    document
      .querySelectorAll(".tab-button")
      .forEach((btn) => (btn.style.display = "none"));
    document
      .querySelectorAll(".tab-content")
      .forEach((tab) => (tab.style.display = "none"));

    // Show tabs/content based on role
    if (role === "admin") {
      showTabs([
        "tasks-tab",
        "attendance-tab",
        "ratings-tab",
        "expenses-tab",
        "reports-tab",
        "profile-tab",
        "logout-tab",
      ]);
    } else if (role === "coordinator") {
      showTabs([
        "tasks-tab",
        "attendance-tab",
        "ratings-tab",
        "profile-tab",
        "logout-tab",
      ]);
    } else if (role === "volunteer") {
      showTabs(["tasks-tab", "attendance-tab", "profile-tab", "logout-tab"]);
    }

    // Always show the first visible tab by default
    const firstVisibleTabBtn = Array.from(
      document.querySelectorAll(".tab-button")
    ).find((btn) => btn.style.display !== "none");
    if (firstVisibleTabBtn) {
      firstVisibleTabBtn.classList.add("active");
      const tabId = firstVisibleTabBtn.getAttribute("data-tab");
      if (tabId) {
        document.getElementById(tabId).style.display = "";
      }
    }
  }

  // Helper to show tab buttons and content by id
  function showTabs(tabIds) {
    tabIds.forEach((tabId) => {
      const btn = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
      const tab = document.getElementById(tabId);
      if (btn) btn.style.display = "";
      if (tab) tab.style.display = "";
    });
  }

  let dashboardAutoRefreshInterval = null;
  let currentDashboardTab = null;

  function showTab(tabId) {
    // Update tab buttons
    const tabButtons = dashboardTabs.querySelectorAll(".tab-button");
    tabButtons.forEach((btn) => btn.classList.remove("active"));

    // Hide all tab contents
    tabContents.forEach((content) => content.classList.add("hidden"));

    // Show selected tab content
    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {
      selectedContent.classList.remove("hidden");
    }

    // Mark active tab button
    const activeButton = Array.from(tabButtons).find((btn) =>
      btn.textContent.toLowerCase().includes(tabId.split("-")[1])
    );
    if (activeButton) {
      activeButton.classList.add("active");
    }

    // Clear previous interval if switching tabs
    if (dashboardAutoRefreshInterval) {
      clearInterval(dashboardAutoRefreshInterval);
      dashboardAutoRefreshInterval = null;
    }
    currentDashboardTab = tabId;
    // Load data for the selected tab
    loadTabData(tabId);
    // Set up auto-refresh for all dashboard tabs
    // dashboardAutoRefreshInterval = setInterval(() => {
    //     loadTabData(tabId);
    // }, 5000); // 5 seconds
  }

  /**
   * Loads data for a specific tab.
   * @param {string} tabId The ID of the tab.
   */
  async function loadTabData(tabId) {
    try {
      if (tabId === "volunteer-assigned-tasks") {
        await fetchAssignedTasks();
      } else if (tabId === "volunteer-attendance") {
        await fetchMyAttendance();
      } else if (tabId === "volunteer-ratings") {
        await fetchMyRatings();
      } else if (tabId === "volunteer-profile") {
        await fetchProfile();
      } else if (tabId === "coordinator-assign-tasks") {
        await populateCoordinatorTaskSelects();
        await populateVolunteerSelects();
      } else if (tabId === "coordinator-attendance") {
        await fetchCoordinatorAttendance();
      } else if (tabId === "coordinator-ratings") {
        await populateCoordinatorRatingSelects();
        await fetchMySubmittedRatings();
      } else if (tabId === "coordinator-expenses") {
        await fetchCoordinatorExpenses();
      } else if (tabId === "coordinator-reports") {
        await fetchCoordinatorReports();
      } else if (tabId === "tasks-tab") {
        await fetchAllTasks();
      } else if (tabId === "admin-users") {
        await fetchAllUsers();
      } else if (tabId === "admin-attendance") {
        await fetchAdminAttendance();
      } else if (tabId === "admin-ratings") {
        await fetchAllRatings();
      } else if (tabId === "admin-expenses") {
        await fetchAllExpenses();
      } else if (tabId === "admin-reports") {
        await fetchAdminReports();
      }
    } catch (error) {
      console.error(`Error loading data for tab ${tabId}:`, error);
    }
  }

  // --- Event Listeners ---

  // Login form submission
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = loginForm.email.value;
      const password = loginForm.password.value;
      try {
        const response = await apiRequest("/login", "POST", {
          email,
          password,
        });
        if (response && response.redirect_to) {
          window.location.href = response.redirect_to;
        }
      } catch (error) {
        showMessage(loginMessage, error.message, "error");
      }
    });
  }

  // Logout button
  if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
      try {
        await apiRequest("/logout", "POST");
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        logout();
      }
    });
  }

  // --- Volunteer Functions ---

  async function fetchAssignedTasks() {
    try {
      const tasks = await apiRequest("/tasks/assigned", "GET");
      assignedTasksList.innerHTML = "";

      if (tasks.length === 0) {
        assignedTasksList.innerHTML =
          '<p class="text-gray-600">No tasks assigned to you yet.</p>';
        return;
      }

      tasks.forEach((task) => {
        const taskCard = document.createElement("div");
        taskCard.className =
          "bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4";
        taskCard.innerHTML = `
                <h4 class="text-lg font-semibold text-gray-800">${
                  task.title
                }</h4>
                <p class="text-gray-700 text-sm mb-2">${task.description}</p>
                <div class="flex justify-between items-center text-xs text-gray-500">
                    <span><strong>Priority:</strong> ${task.priority}</span>
                    <span><strong>Deadline:</strong> ${task.deadline}</span>
                    <span><strong>Status:</strong> ${task.status}</span>
                </div>
                ${
                  task.status !== "Completed"
                    ? `
                    <button onclick="updateTaskStatus('${
                      task.task_id || "unknown"
                    }', 'Completed')" 
                            class="mt-2 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Mark Complete
                    </button>
                `
                    : ""
                }
            `;
        assignedTasksList.appendChild(taskCard);
      });
    } catch (error) {
      assignedTasksList.innerHTML = `<p class="text-red-600">Error loading tasks: ${error.message}</p>`;
    }
  }

  async function updateTaskStatus(taskId, status) {
    try {
      await apiRequest(`/tasks/update_status/${taskId}`, "PUT", { status });
      await fetchAssignedTasks(); // Refresh the list
    } catch (error) {
      console.error("Error updating task status:", error);
    }
  }

  async function fetchMyAttendance() {
    try {
      const attendance = await apiRequest("/attendance/my", "GET");
      myAttendanceHistory.innerHTML = "";

      if (attendance.length === 0) {
        myAttendanceHistory.innerHTML =
          '<p class="text-gray-600">No attendance records found.</p>';
        return;
      }

      const table = document.createElement("table");
      table.className = "w-full border-collapse border border-gray-300";
      table.innerHTML = `
            <thead>
                <tr class="bg-gray-100">
                    <th class="border border-gray-300 px-4 py-2 text-left">Date</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">Task ID</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;

      const tbody = table.querySelector("tbody");
      attendance.forEach((log) => {
        const row = tbody.insertRow();
        row.className = "table-row";
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
      const ratings = await apiRequest("/ratings/my", "GET");
      myRatingsList.innerHTML = "";
      if (ratings.length === 0) {
        myRatingsList.innerHTML =
          '<p class="text-gray-600">No ratings or feedback received yet.</p>';
        return;
      }
      ratings.forEach((rating) => {
        const ratingCard = document.createElement("div");
        ratingCard.className =
          "bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4";
        ratingCard.innerHTML = `
                <h4 class="text-lg font-semibold text-gray-800">Rating for Task: ${
                  rating.task_id
                }</h4>
                <p class="text-gray-700 text-sm"><strong>Score:</strong> ${
                  rating.score
                }/5</p>
                <p class="text-gray-700 text-sm"><strong>Comments:</strong> ${
                  rating.comments
                }</p>
                <p class="text-gray-500 text-xs mt-2">Submitted by: ${
                  rating.coordinator_id || rating.admin_id
                }</p>
            `;
        myRatingsList.appendChild(ratingCard);
      });
    } catch (error) {
      myRatingsList.innerHTML = `<p class="text-red-600">Error loading ratings: ${error.message}</p>`;
    }
  }

  async function fetchProfile() {
    try {
      const profile = await apiRequest("/profile", "GET");
      profileNameInput.value = profile.name || "";
      profileEmailInput.value = profile.email || "";
      profileContactInput.value = profile.contact || "";
      profileNewPasswordInput.value = ""; // Clear password field
    } catch (error) {
      showMessage(
        profileMessage,
        `Error loading profile: ${error.message}`,
        "error"
      );
    }
  }

  if (updateProfileForm) {
    updateProfileForm.addEventListener("submit", async (e) => {
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
        const result = await apiRequest("/profile/update", "PUT", updateData);
        showMessage(profileMessage, result.message, "success");
        profileNewPasswordInput.value = ""; // Clear password field after update
        // Re-fetch profile to ensure UI is consistent with backend
        fetchProfile();
      } catch (error) {
        showMessage(profileMessage, error.message, "error");
      }
    });
  }

  // --- Coordinator Functions ---

  // Assign task form
  if (assignTaskForm) {
    assignTaskForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const taskId = assignTaskIdSelect.value;
      const volunteerId = assignVolunteerIdSelect.value;
      const priority = assignPrioritySelect.value;
      const deadline = assignDeadlineInput.value;

      try {
        const result = await apiRequest("/tasks/assign_volunteer", "POST", {
          task_id: taskId,
          volunteer_id: volunteerId,
          priority,
          deadline,
        });
        showMessage(assignTaskMessage, result.message, "success");
        assignTaskForm.reset();
        populateCoordinatorTaskSelects(); // Refresh tasks
      } catch (error) {
        showMessage(assignTaskMessage, error.message, "error");
      }
    });
  }

  // Reassign task form
  if (reassignTaskForm) {
    reassignTaskForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const taskId = reassignTaskSelect.value;
      const newVolunteerId = reassignVolunteerIdSelect.value;

      try {
        const result = await apiRequest(
          `/tasks/reassign_volunteer/${taskId}`,
          "PUT",
          { volunteer_id: newVolunteerId }
        );
        showMessage(reassignTaskMessage, result.message, "success");
        reassignTaskForm.reset();
        populateCoordinatorTaskSelects(); // Refresh tasks
      } catch (error) {
        showMessage(reassignTaskMessage, error.message, "error");
      }
    });
  }

  async function populateVolunteerSelects() {
    try {
      const volunteers = await apiRequest("/volunteers", "GET");
      assignVolunteerIdSelect.innerHTML =
        '<option value="">Select a Volunteer</option>';
      reassignVolunteerIdSelect.innerHTML =
        '<option value="">Select a Volunteer</option>';
      ratingVolunteerIdSelect.innerHTML =
        '<option value="">Select a Volunteer</option>'; // For rating form
      adminRatingVolunteerIdSelect.innerHTML =
        '<option value="">Select a Volunteer</option>'; // For admin rating form

      volunteers.forEach((vol) => {
        const option1 = document.createElement("option");
        option1.value = vol.user_id;
        option1.textContent = vol.name;
        assignVolunteerIdSelect.appendChild(option1);

        const option2 = document.createElement("option");
        option2.value = vol.user_id;
        option2.textContent = vol.name;
        reassignVolunteerIdSelect.appendChild(option2);

        const option3 = document.createElement("option");
        option3.value = vol.user_id;
        option3.textContent = vol.name;
        ratingVolunteerIdSelect.appendChild(option3);

        const option4 = document.createElement("option");
        option4.value = vol.user_id;
        option4.textContent = vol.name;
        adminRatingVolunteerIdSelect.appendChild(option4);
      });
    } catch (error) {
      console.error("Error populating volunteer selects:", error);
    }
  }

  async function populateCoordinatorTaskSelects() {
    try {
      // Coordinators can assign tasks that are not yet assigned
      const allTasks = await apiRequest("/tasks", "GET");
      const unassignedTasks = allTasks.filter((task) => !task.assigned_to);

      assignTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
      unassignedTasks.forEach((task) => {
        const option = document.createElement("option");
        option.value = task.task_id;
        option.textContent = task.title;
        assignTaskIdSelect.appendChild(option);
      });

      // For reassign, they can reassign any task (though backend might restrict to their supervised tasks)
      reassignTaskSelect.innerHTML = '<option value="">Select a Task</option>';
      allTasks.forEach((task) => {
        const option = document.createElement("option");
        option.value = task.task_id;
        option.textContent = `${task.title} (Assigned to: ${
          task.assigned_to || "None"
        })`;
        reassignTaskSelect.appendChild(option);
      });

      // For rating tasks, they can rate tasks assigned to volunteers
      ratingTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
      allTasks.forEach((task) => {
        const option = document.createElement("option");
        option.value = task.task_id;
        option.textContent = `${task.title} (Status: ${task.status})`;
        ratingTaskIdSelect.appendChild(option);
      });

      // For admin rating tasks
      adminRatingTaskIdSelect.innerHTML =
        '<option value="">Select a Task</option>';
      allTasks.forEach((task) => {
        const option = document.createElement("option");
        option.value = task.task_id;
        option.textContent = `${task.title} (Status: ${task.status})`;
        adminRatingTaskIdSelect.appendChild(option);
      });

      // For expense logging
      expenseTaskIdSelect.innerHTML = '<option value="">Select a Task</option>';
      allTasks.forEach((task) => {
        const option = document.createElement("option");
        option.value = task.task_id;
        option.textContent = `${task.title}`;
        expenseTaskIdSelect.appendChild(option);
      });
    } catch (error) {
      console.error("Error populating coordinator task selects:", error);
    }
  }

  assignTaskForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const taskId = assignTaskIdSelect.value;
    const volunteerId = assignVolunteerIdSelect.value;
    const priority = assignPrioritySelect.value;
    const deadline = assignDeadlineInput.value;

    try {
      const result = await apiRequest("/tasks/assign_volunteer", "POST", {
        task_id: taskId,
        volunteer_id: volunteerId,
        priority,
        deadline,
      });
      showMessage(assignTaskMessage, result.message, "success");
      assignTaskForm.reset();
      populateCoordinatorTaskSelects(); // Refresh tasks
    } catch (error) {
      showMessage(assignTaskMessage, error.message, "error");
    }
  });

  reassignTaskForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const taskId = reassignTaskSelect.value;
    const newVolunteerId = reassignVolunteerIdSelect.value;

    try {
      const result = await apiRequest(
        `/tasks/reassign_volunteer/${taskId}`,
        "PUT",
        { volunteer_id: newVolunteerId }
      );
      showMessage(reassignTaskMessage, result.message, "success");
      reassignTaskForm.reset();
      populateCoordinatorTaskSelects(); // Refresh tasks
    } catch (error) {
      showMessage(reassignTaskMessage, error.message, "error");
    }
  });

  async function fetchCoordinatorAttendance() {
    try {
      const volunteerId = coordAttendanceVolunteerFilter.value;
      const dateFilter = coordAttendanceDateFilter.value;
      const queryParams = new URLSearchParams();
      if (volunteerId) queryParams.append("volunteer_id", volunteerId);
      if (dateFilter) queryParams.append("date", dateFilter);

      const attendance = await apiRequest(
        `/attendance?${queryParams.toString()}`,
        "GET"
      );
      coordinatorAttendanceList.innerHTML = "";
      if (attendance.length === 0) {
        coordinatorAttendanceList.innerHTML =
          '<p class="text-gray-600">No attendance logs found.</p>';
        return;
      }
      const table = document.createElement("table");
      table.className =
        "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
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
      const tbody = table.querySelector("tbody");
      attendance.forEach((log) => {
        const row = tbody.insertRow();
        row.className = "table-row";
        row.insertCell().textContent = log.date;
        row.insertCell().textContent = log.user_id;
        row.insertCell().textContent = log.task_id;
      });
      coordinatorAttendanceList.appendChild(table);
    } catch (error) {
      coordinatorAttendanceList.innerHTML = `<p class="text-red-600">Error loading attendance logs: ${error.message}</p>`;
    }
  }

  if (coordAttendanceFilterBtn) {
    coordAttendanceFilterBtn.addEventListener(
      "click",
      fetchCoordinatorAttendance
    );
  }
  if (coordAttendanceResetBtn) {
    coordAttendanceResetBtn.addEventListener("click", () => {
      coordAttendanceVolunteerFilter.value = "";
      coordAttendanceDateFilter.value = "";
      fetchCoordinatorAttendance();
    });
  }

  async function populateCoordinatorRatingSelects() {
    await populateVolunteerSelects(); // Reuse for volunteer select
    await populateCoordinatorTaskSelects(); // Reuse for task select
  }

  if (submitRatingForm) {
    submitRatingForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const volunteerId = ratingVolunteerIdSelect.value;
      const taskId = ratingTaskIdSelect.value;
      const score = parseInt(ratingScoreInput.value);
      const comments = ratingCommentsTextarea.value;

      try {
        const result = await apiRequest("/ratings/add", "POST", {
          volunteer_id: volunteerId,
          task_id: taskId,
          score,
          comments,
        });
        showMessage(submitRatingMessage, result.message, "success");
        submitRatingForm.reset();
        fetchMySubmittedRatings(); // Refresh list
      } catch (error) {
        showMessage(submitRatingMessage, error.message, "error");
      }
    });
  }

  async function fetchMySubmittedRatings() {
    try {
      const ratings = await apiRequest("/ratings?submitted_by=me", "GET");
      mySubmittedRatingsList.innerHTML = "";
      if (ratings.length === 0) {
        mySubmittedRatingsList.innerHTML =
          '<p class="text-gray-600">No ratings submitted by you.</p>';
        return;
      }
      const table = document.createElement("table");
      table.className =
        "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
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
      const tbody = table.querySelector("tbody");
      ratings.forEach((rating) => {
        const row = tbody.insertRow();
        row.className = "table-row";
        row.insertCell().textContent = rating.rating_id;
        row.insertCell().textContent = rating.volunteer_id;
        row.insertCell().textContent = rating.task_id;
        row.insertCell().textContent = rating.score;
        row.insertCell().textContent = rating.comments;
        const actionsCell = row.insertCell();
        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.className = "btn-secondary text-xs mr-2";
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
    const newScore = prompt(
      `Edit score for rating ${rating.rating_id} (current: ${rating.score}):`
    );
    const newComments = prompt(
      `Edit comments for rating ${rating.rating_id} (current: ${rating.comments}):`
    );

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
      showMessage(
        mySubmittedRatingsList.parentElement.querySelector(".message-box") ||
          mySubmittedRatingsList,
        "No changes to update.",
        "error"
      );
      return;
    }

    try {
      const result = await apiRequest(
        `/ratings/${ratingId}`,
        "PUT",
        updateData
      );
      showMessage(
        mySubmittedRatingsList.parentElement.querySelector(".message-box") ||
          mySubmittedRatingsList,
        result.message,
        "success"
      );
      fetchMySubmittedRatings(); // Refresh list
    } catch (error) {
      showMessage(
        mySubmittedRatingsList.parentElement.querySelector(".message-box") ||
          mySubmittedRatingsList,
        error.message,
        "error"
      );
    }
  }

  async function fetchCoordinatorExpenses() {
    try {
      const taskId = coordExpenseTaskFilter.value;
      const category = coordExpenseCategoryFilter.value;
      const queryParams = new URLSearchParams();
      if (taskId) queryParams.append("task_id", taskId);
      if (category) queryParams.append("category", category);

      const expenses = await apiRequest(
        `/expenses?${queryParams.toString()}`,
        "GET"
      );
      coordinatorExpensesList.innerHTML = "";
      if (expenses.length === 0) {
        coordinatorExpensesList.innerHTML =
          '<p class="text-gray-600">No expense logs found.</p>';
        return;
      }
      const table = document.createElement("table");
      table.className =
        "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
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
      const tbody = table.querySelector("tbody");
      expenses.forEach((exp) => {
        const row = tbody.insertRow();
        row.className = "table-row";
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

  if (coordExpenseFilterBtn) {
    coordExpenseFilterBtn.addEventListener("click", fetchCoordinatorExpenses);
  }
  if (coordExpenseResetBtn) {
    coordExpenseResetBtn.addEventListener("click", () => {
      coordExpenseTaskFilter.value = "";
      coordExpenseCategoryFilter.value = "";
      fetchCoordinatorExpenses();
    });
  }

  async function fetchCoordinatorReports() {
    try {
      // Attendance Report
      const attendanceReport = await apiRequest("/reports/attendance", "GET");
      reportCoordAttendance.innerHTML =
        '<h5 class="font-semibold mb-2">Attendance Report:</h5>';
      if (attendanceReport.length === 0) {
        reportCoordAttendance.innerHTML +=
          '<p class="text-gray-600">No attendance data.</p>';
      } else {
        const table = document.createElement("table");
        table.className =
          "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
        table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Date</th><th>User ID</th><th>Task ID</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
        const tbody = table.querySelector("tbody");
        attendanceReport.forEach((log) => {
          const row = tbody.insertRow();
          row.className = "table-row";
          row.insertCell().textContent = log.date;
          row.insertCell().textContent = log.user_id;
          row.insertCell().textContent = log.task_id;
        });
        reportCoordAttendance.appendChild(table);
      }

      // Assignment Report
      const assignmentReport = await apiRequest("/reports/assignments", "GET");
      reportCoordAssignments.innerHTML =
        '<h5 class="font-semibold mb-2">Assignment Report:</h5>';
      if (assignmentReport.length === 0) {
        reportCoordAssignments.innerHTML +=
          '<p class="text-gray-600">No assignment data.</p>';
      } else {
        const table = document.createElement("table");
        table.className =
          "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
        table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task</th><th>Assigned To</th><th>Role</th><th>Deadline</th><th>Status</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
        const tbody = table.querySelector("tbody");
        assignmentReport.forEach((item) => {
          const row = tbody.insertRow();
          row.className = "table-row";
          row.insertCell().textContent = item.title;
          row.insertCell().textContent = `${item.assigned_to_name} (${item.assigned_to_id})`;
          row.insertCell().textContent = item.role;
          row.insertCell().textContent = item.deadline;
          row.insertCell().textContent = item.status;
        });
        reportCoordAssignments.appendChild(table);
      }

      // Expense Report
      const expenseReport = await apiRequest("/reports/expenses", "GET");
      reportCoordExpenses.innerHTML =
        '<h5 class="font-semibold mb-2">Expense Report:</h5>';
      if (expenseReport.length === 0) {
        reportCoordExpenses.innerHTML +=
          '<p class="text-gray-600">No expense data.</p>';
      } else {
        const table = document.createElement("table");
        table.className =
          "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
        table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task ID</th><th>Amount</th><th>Category</th><th>Logged By</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
        const tbody = table.querySelector("tbody");
        expenseReport.forEach((item) => {
          const row = tbody.insertRow();
          row.className = "table-row";
          row.insertCell().textContent = item.task_id;
          row.insertCell().textContent = `$${item.amount.toFixed(2)}`;
          row.insertCell().textContent = item.category;
          row.insertCell().textContent = item.logged_by;
        });
        reportCoordExpenses.appendChild(table);
      }
    } catch (error) {
      console.error("Error fetching coordinator reports:", error);
      reportCoordAttendance.innerHTML = `<p class="text-red-600">Error loading attendance report: ${error.message}</p>`;
      reportCoordAssignments.innerHTML = `<p class="text-red-600">Error loading assignment report: ${error.message}</p>`;
      reportCoordExpenses.innerHTML = `<p class="text-red-600">Error loading expense report: ${error.message}</p>`;
    }
  }

  // --- Admin Functions ---

  createUserForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = createUserNameInput.value;
    const email = createUserEmailInput.value;
    const password = createUserPasswordInput.value;
    const role = createUserRoleSelect.value;
    const contact = createUserContactInput.value;

    try {
      const result = await apiRequest("/users/create", "POST", {
        name,
        email,
        password,
        role,
        contact,
      });
      showMessage(createUserMessage, result.message, "success");
      createUserForm.reset();
      fetchAllUsers(); // Refresh user list
    } catch (error) {
      showMessage(createUserMessage, error.message, "error");
    }
  });

  async function fetchAllUsers() {
    try {
      const users = await apiRequest("/users", "GET");
      allUsersList.innerHTML = "";
      if (users.length === 0) {
        allUsersList.innerHTML = '<p class="text-gray-600">No users found.</p>';
        return;
      }
      users.forEach((user) => {
        let roleIcon = "";
        let roleColor = "";
        if (user.role === "admin") {
          roleIcon =
            '<i class="fa-solid fa-shield-halved text-purple-600"></i>';
          roleColor = "bg-purple-50 border-purple-300";
        } else if (user.role === "coordinator") {
          roleIcon = '<i class="fa-solid fa-briefcase text-blue-600"></i>';
          roleColor = "bg-blue-50 border-blue-300";
        } else {
          roleIcon = '<i class="fa-solid fa-user-group text-green-600"></i>';
          roleColor = "bg-green-50 border-green-300";
        }
        const card = document.createElement("div");
        card.className = `transition-transform duration-200 hover:scale-105 shadow-md border rounded-xl p-5 mb-4 flex flex-col gap-2 ${roleColor}`;
        card.innerHTML = `
                <div class="flex items-center gap-2 mb-2">
                    ${roleIcon}
                    <span class="text-lg font-bold text-gray-800">${
                      user.name
                    }</span>
                    <span class="ml-auto inline-block px-2 py-1 text-xs font-semibold rounded ${
                      user.role === "admin"
                        ? "bg-purple-100 text-purple-700"
                        : user.role === "coordinator"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-green-100 text-green-700"
                    }">${
          user.role.charAt(0).toUpperCase() + user.role.slice(1)
        }</span>
                </div>
                <div class="text-gray-600 text-sm mb-2"><i class="fa-solid fa-envelope"></i> ${
                  user.email
                }</div>
                <div class="flex items-center gap-4 text-xs text-gray-500">
                    <span><i class="fa-solid fa-phone"></i> ${
                      user.contact || "N/A"
                    }</span>
                    <span><i class="fa-solid fa-id-badge"></i> ID: ${
                      user.user_id
                    }</span>
                </div>
                <div class="flex gap-2 mt-2">
                    <button class="btn-dashboard-secondary text-xs" onclick="openEditUserModal(${JSON.stringify(
                      user
                    ).replace(
                      /"/g,
                      "&quot;"
                    )})"><i class="fa-solid fa-pen"></i> Edit</button>
                    <button class="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs" onclick="deleteUser('${
                      user.user_id
                    }')"><i class="fa-solid fa-trash"></i> Delete</button>
                </div>
            `;
        allUsersList.appendChild(card);
      });
    } catch (error) {
      allUsersList.innerHTML = `<p class="text-red-600">Error loading users: ${error.message}</p>`;
    }
  }

  function openEditUserModal(user) {
    const newName = prompt(
      `Edit name for ${user.name} (current: ${user.name}):`,
      user.name
    );
    const newEmail = prompt(
      `Edit email for ${user.name} (current: ${user.email}):`,
      user.email
    );
    const newRole = prompt(
      `Edit role for ${user.name} (current: ${user.role}). Options: volunteer, coordinator, admin:`,
      user.role
    );
    const newContact = prompt(
      `Edit contact for ${user.name} (current: ${user.contact}):`,
      user.contact
    );
    const newPassword = prompt(
      `Enter new password for ${user.name} (leave blank to keep current):`
    );

    const updateData = {};
    if (newName !== null && newName !== user.name) updateData.name = newName;
    if (newEmail !== null && newEmail !== user.email)
      updateData.email = newEmail;
    if (newRole !== null && newRole !== user.role) updateData.role = newRole;
    if (newContact !== null && newContact !== user.contact)
      updateData.contact = newContact;
    if (newPassword !== null && newPassword !== "")
      updateData.password = newPassword;

    if (Object.keys(updateData).length > 0) {
      updateUser(user.user_id, updateData);
    } else {
      showMessage(
        allUsersList.parentElement.querySelector(".message-box") ||
          allUsersList,
        "No changes detected.",
        "error"
      );
    }
  }

  async function updateUser(userId, updateData) {
    try {
      const result = await apiRequest(`/users/${userId}`, "PUT", updateData);
      showMessage(
        allUsersList.parentElement.querySelector(".message-box") ||
          allUsersList,
        result.message,
        "success"
      );
      fetchAllUsers(); // Refresh list
    } catch (error) {
      showMessage(
        allUsersList.parentElement.querySelector(".message-box") ||
          allUsersList,
        error.message,
        "error"
      );
    }
  }

  async function deleteUser(userId) {
    if (confirm(`Are you sure you want to delete user ${userId}?`)) {
      // Using confirm for simplicity, replace with custom modal
      try {
        const result = await apiRequest(`/users/${userId}`, "DELETE");
        showMessage(
          allUsersList.parentElement.querySelector(".message-box") ||
            allUsersList,
          result.message,
          "success"
        );
        fetchAllUsers(); // Refresh list
      } catch (error) {
        showMessage(
          allUsersList.parentElement.querySelector(".message-box") ||
            allUsersList,
          error.message,
          "error"
        );
      }
    }
  }

  async function populateAdminTaskAssignToSelect() {
    try {
      const users = await apiRequest("/users", "GET");
      newTaskAssignToSelect.innerHTML = '<option value="">None</option>';
      users.forEach((user) => {
        if (user.role === "volunteer" || user.role === "coordinator") {
          const option = document.createElement("option");
          option.value = user.user_id;
          option.textContent = `${user.name} (${user.role})`;
          newTaskAssignToSelect.appendChild(option);
        }
      });
    } catch (error) {
      console.error("Error populating admin task assign-to select:", error);
    }
  }

  createTaskForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = newTaskTitleInput.value;
    const description = newTaskDescriptionTextarea.value;
    const deadline = newTaskDeadlineInput.value;
    const priority = newTaskPrioritySelect.value;
    const assignedTo = newTaskAssignToSelect.value || null;

    try {
      const result = await apiRequest("/tasks/create", "POST", {
        title,
        description,
        deadline,
        priority,
        assigned_to: assignedTo,
      });
      showMessage(createTaskMessage, result.message, "success");
      createTaskForm.reset();
      fetchAllTasks(); // Refresh list
      populateCoordinatorTaskSelects(); // Refresh for coordinator
    } catch (error) {
      showMessage(createTaskMessage, error.message, "error");
    }
  });

  async function fetchAllTasks() {
    try {
      const statusFilter = adminTaskStatusFilter.value;
      const queryParams = new URLSearchParams();
      if (statusFilter) queryParams.append("status", statusFilter);

      const tasks = await apiRequest(`/tasks?${queryParams.toString()}`, "GET");
      allTasksList.innerHTML = "";
      if (tasks.length === 0) {
        allTasksList.innerHTML = '<p class="text-gray-600">No tasks found.</p>';
        return;
      }
      // Card-based rendering
      tasks.forEach((task) => {
        let priorityIcon = "";
        let priorityColor = "";
        if (task.priority === "High") {
          priorityIcon = '<i class="fa-solid fa-bolt text-red-500"></i>';
          priorityColor = "bg-red-50 border-red-300";
        } else if (task.priority === "Medium") {
          priorityIcon = '<i class="fa-solid fa-arrow-up text-yellow-500"></i>';
          priorityColor = "bg-yellow-50 border-yellow-300";
        } else {
          priorityIcon =
            '<i class="fa-solid fa-arrow-down text-green-500"></i>';
          priorityColor = "bg-green-50 border-green-300";
        }
        let statusBadge = "";
        if (task.status === "Completed") {
          statusBadge =
            '<span class="inline-block px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-700">Completed</span>';
        } else if (task.status === "In Progress") {
          statusBadge =
            '<span class="inline-block px-2 py-1 text-xs font-semibold rounded bg-yellow-100 text-yellow-700">In Progress</span>';
        } else {
          statusBadge =
            '<span class="inline-block px-2 py-1 text-xs font-semibold rounded bg-gray-200 text-gray-700">Pending</span>';
        }
        const card = document.createElement("div");
        card.className = `transition-transform duration-200 hover:scale-105 shadow-md border rounded-xl p-5 mb-4 flex flex-col gap-2 ${priorityColor}`;
        card.innerHTML = `
                <div class="flex items-center gap-2 mb-2">
                    ${priorityIcon}
                    <span class="text-lg font-bold text-gray-800">${
                      task.title
                    }</span>
                    <span class="ml-auto">${statusBadge}</span>
                </div>
                <div class="text-gray-600 text-sm mb-2">${
                  task.description
                }</div>
                <div class="flex items-center gap-4 text-xs text-gray-500">
                    <span><i class="fa-regular fa-calendar"></i> <b>Deadline:</b> ${
                      task.deadline
                    }</span>
                    <span><i class="fa-solid fa-user"></i> <b>Assigned:</b> ${
                      task.assigned_to || "None"
                    }</span>
                    <span><i class="fa-solid fa-layer-group"></i> <b>Priority:</b> ${
                      task.priority
                    }</span>
                </div>
                <div class="flex gap-2 mt-2">
                    <button class="btn-dashboard-secondary text-xs" onclick="openEditTaskModal(${JSON.stringify(
                      task
                    ).replace(
                      /"/g,
                      "&quot;"
                    )})"><i class="fa-solid fa-pen"></i> Edit</button>
                    <button class="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs" onclick="deleteTask('${
                      task.task_id
                    }')"><i class="fa-solid fa-trash"></i> Delete</button>
                </div>
            `;
        allTasksList.appendChild(card);
      });
    } catch (error) {
      allTasksList.innerHTML = `<p class="text-red-600">Error loading tasks: ${error.message}</p>`;
    }
  }

  if (adminTaskFilterBtn) {
    adminTaskFilterBtn.addEventListener("click", fetchAllTasks);
  }
  if (adminTaskResetBtn) {
    adminTaskResetBtn.addEventListener("click", () => {
      adminTaskStatusFilter.value = "";
      fetchAllTasks();
    });
  }

  function openEditTaskModal(task) {
    const newTitle = prompt(
      `Edit title for ${task.title} (current: ${task.title}):`,
      task.title
    );
    const newDescription = prompt(
      `Edit description (current: ${task.description}):`,
      task.description
    );
    const newDeadline = prompt(
      `Edit deadline (current: ${task.deadline}):`,
      task.deadline
    );
    const newPriority = prompt(
      `Edit priority (current: ${task.priority}):`,
      task.priority
    );
    const newStatus = prompt(
      `Edit status (current: ${task.status}). Options: Pending, In Progress, Completed:`,
      task.status
    );
    const newAssignedTo = prompt(
      `Edit assigned to (current: ${
        task.assigned_to || "None"
      }). Enter User ID or leave blank:`,
      task.assigned_to || ""
    );

    const updateData = {};
    if (newTitle !== null && newTitle !== task.title)
      updateData.title = newTitle;
    if (newDescription !== null && newDescription !== task.description)
      updateData.description = newDescription;
    if (newDeadline !== null && newDeadline !== task.deadline)
      updateData.deadline = newDeadline;
    if (newPriority !== null && newPriority !== task.priority)
      updateData.priority = newPriority;
    if (newStatus !== null && newStatus !== task.status)
      updateData.status = newStatus;
    if (newAssignedTo !== null) updateData.assigned_to = newAssignedTo || null;

    if (Object.keys(updateData).length > 0) {
      updateTask(task.task_id, updateData);
    } else {
      showMessage(
        allTasksList.parentElement.querySelector(".message-box") ||
          allTasksList,
        "No changes detected.",
        "error"
      );
    }
  }

  async function updateTask(taskId, updateData) {
    try {
      const result = await apiRequest(`/tasks/${taskId}`, "PUT", updateData);
      showMessage(
        allTasksList.parentElement.querySelector(".message-box") ||
          allTasksList,
        result.message,
        "success"
      );
      fetchAllTasks(); // Refresh list
      fetchAssignedTasks(); // Refresh volunteer's view
    } catch (error) {
      showMessage(
        allTasksList.parentElement.querySelector(".message-box") ||
          allTasksList,
        error.message,
        "error"
      );
    }
  }

  async function deleteTask(taskId) {
    if (confirm(`Are you sure you want to delete task ${taskId}?`)) {
      // Using confirm for simplicity, replace with custom modal
      try {
        const result = await apiRequest(`/tasks/${taskId}`, "DELETE");
        showMessage(
          allTasksList.parentElement.querySelector(".message-box") ||
            allTasksList,
          result.message,
          "success"
        );
        fetchAllTasks(); // Refresh list
      } catch (error) {
        showMessage(
          allTasksList.parentElement.querySelector(".message-box") ||
            allTasksList,
          error.message,
          "error"
        );
      }
    }
  }

  async function fetchAdminAttendance() {
    try {
      const volunteerId = adminAttendanceVolunteerFilter.value;
      const dateFilter = adminAttendanceDateFilter.value;
      const queryParams = new URLSearchParams();
      if (volunteerId) queryParams.append("volunteer_id", volunteerId);
      if (dateFilter) queryParams.append("date", dateFilter);

      const attendance = await apiRequest(
        `/attendance?${queryParams.toString()}`,
        "GET"
      );
      adminAllAttendanceList.innerHTML = "";
      if (attendance.length === 0) {
        adminAllAttendanceList.innerHTML =
          '<p class="text-gray-600">No attendance logs found.</p>';
        return;
      }
      const table = document.createElement("table");
      table.className =
        "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
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
      const tbody = table.querySelector("tbody");
      attendance.forEach((log) => {
        const row = tbody.insertRow();
        row.className = "table-row";
        row.insertCell().textContent = log.date;
        row.insertCell().textContent = log.user_id;
        row.insertCell().textContent = log.task_id;
      });
      adminAllAttendanceList.appendChild(table);
    } catch (error) {
      adminAllAttendanceList.innerHTML = `<p class="text-red-600">Error loading attendance logs: ${error.message}</p>`;
    }
  }

  if (adminAttendanceFilterBtn) {
    adminAttendanceFilterBtn.addEventListener("click", fetchAdminAttendance);
  }
  if (adminAttendanceResetBtn) {
    adminAttendanceResetBtn.addEventListener("click", () => {
      adminAttendanceVolunteerFilter.value = "";
      adminAttendanceDateFilter.value = "";
      fetchAdminAttendance();
    });
  }

  getAbsenteesBtn.addEventListener("click", fetchAbsentees);
  async function fetchAbsentees() {
    try {
      const absentees = await apiRequest("/attendance/absentees", "GET");
      adminAbsenteesList.innerHTML = "";
      if (absentees.length === 0) {
        adminAbsenteesList.innerHTML =
          '<p class="text-gray-600">No absentees found for today.</p>';
        return;
      }
      const ul = document.createElement("ul");
      ul.className = "list-disc list-inside space-y-1 text-gray-700";
      absentees.forEach((absentee) => {
        const li = document.createElement("li");
        li.textContent = `${absentee.name} (${absentee.user_id}, ${absentee.email})`;
        ul.appendChild(li);
      });
      adminAbsenteesList.appendChild(ul);
    } catch (error) {
      adminAbsenteesList.innerHTML = `<p class="text-red-600">Error loading absentees: ${error.message}</p>`;
    }
  }

  if (adminSubmitRatingForm) {
    adminSubmitRatingForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const volunteerId = adminRatingVolunteerIdSelect.value;
      const taskId = adminRatingTaskIdSelect.value;
      const score = parseInt(adminRatingScoreInput.value);
      const comments = adminRatingCommentsTextarea.value;

      try {
        const result = await apiRequest("/ratings/add", "POST", {
          volunteer_id: volunteerId,
          task_id: taskId,
          score,
          comments,
        });
        showMessage(adminSubmitRatingMessage, result.message, "success");
        adminSubmitRatingForm.reset();
        fetchAllRatings(); // Refresh list
      } catch (error) {
        showMessage(adminSubmitRatingMessage, error.message, "error");
      }
    });
  }

  async function fetchAllRatings() {
    try {
      const ratings = await apiRequest("/ratings", "GET");
      adminAllRatingsList.innerHTML = "";
      if (ratings.length === 0) {
        adminAllRatingsList.innerHTML =
          '<p class="text-gray-600">No ratings found.</p>';
        return;
      }
      const table = document.createElement("table");
      table.className =
        "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
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
      const tbody = table.querySelector("tbody");
      ratings.forEach((rating) => {
        const row = tbody.insertRow();
        row.className = "table-row";
        row.insertCell().textContent = rating.rating_id;
        row.insertCell().textContent = rating.volunteer_id;
        row.insertCell().textContent = rating.task_id;
        row.insertCell().textContent = rating.score;
        row.insertCell().textContent = rating.comments;
        row.insertCell().textContent =
          rating.coordinator_id || rating.admin_id || "N/A";
        const actionsCell = row.insertCell();

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.className = "btn-secondary text-xs mr-2";
        editButton.onclick = () => openEditRatingModal(rating); // Reusing coordinator's modal
        actionsCell.appendChild(editButton);

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className =
          "bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs";
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
        const result = await apiRequest(`/ratings/${ratingId}`, "DELETE");
        showMessage(
          adminAllRatingsList.parentElement.querySelector(".message-box") ||
            adminAllRatingsList,
          result.message,
          "success"
        );
        fetchAllRatings(); // Refresh list
      } catch (error) {
        showMessage(
          adminAllRatingsList.parentElement.querySelector(".message-box") ||
            adminAllRatingsList,
          error.message,
          "error"
        );
      }
    }
  }

  logExpenseForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const taskId = expenseTaskIdSelect.value;
    const amount = parseFloat(expenseAmountInput.value);
    const category = expenseCategoryInput.value;

    try {
      const result = await apiRequest("/expenses/log", "POST", {
        task_id: taskId,
        amount,
        category,
      });
      showMessage(logExpenseMessage, result.message, "success");
      logExpenseForm.reset();
      fetchAllExpenses(); // Refresh list
    } catch (error) {
      showMessage(logExpenseMessage, error.message, "error");
    }
  });

  async function fetchAllExpenses() {
    try {
      const taskId = adminExpenseTaskFilter.value;
      const category = adminExpenseCategoryFilter.value;
      const queryParams = new URLSearchParams();
      if (taskId) queryParams.append("task_id", taskId);
      if (category) queryParams.append("category", category);

      const expenses = await apiRequest(
        `/expenses?${queryParams.toString()}`,
        "GET"
      );
      adminAllExpensesList.innerHTML = "";
      if (expenses.length === 0) {
        adminAllExpensesList.innerHTML =
          '<p class="text-gray-600">No expenses found.</p>';
        return;
      }
      const table = document.createElement("table");
      table.className =
        "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
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
      const tbody = table.querySelector("tbody");
      expenses.forEach((exp) => {
        const row = tbody.insertRow();
        row.className = "table-row";
        row.insertCell().textContent = exp.expense_id;
        row.insertCell().textContent = exp.task_id;
        row.insertCell().textContent = `$${exp.amount.toFixed(2)}`;
        row.insertCell().textContent = exp.category;
        row.insertCell().textContent = exp.logged_by;
        const actionsCell = row.insertCell();

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.className = "btn-secondary text-xs mr-2";
        editButton.onclick = () => openEditExpenseModal(exp);
        actionsCell.appendChild(editButton);

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className =
          "bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 text-xs";
        deleteButton.onclick = () => deleteExpense(exp.expense_id);
        actionsCell.appendChild(deleteButton);
      });
      adminAllExpensesList.appendChild(table);
    } catch (error) {
      adminAllExpensesList.innerHTML = `<p class="text-red-600">Error loading expenses: ${error.message}</p>`;
    }
  }

  if (adminExpenseFilterBtn) {
    adminExpenseFilterBtn.addEventListener("click", fetchAllExpenses);
  }
  if (adminExpenseResetBtn) {
    adminExpenseResetBtn.addEventListener("click", () => {
      adminExpenseTaskFilter.value = "";
      adminExpenseCategoryFilter.value = "";
      fetchAllExpenses();
    });
  }

  function openEditExpenseModal(expense) {
    const newAmount = prompt(
      `Edit amount for expense ${expense.expense_id} (current: ${expense.amount}):`,
      expense.amount
    );
    const newCategory = prompt(
      `Edit category (current: ${expense.category}):`,
      expense.category
    );
    const newTaskID = prompt(
      `Edit Task ID (current: ${expense.task_id}):`,
      expense.task_id
    );

    const updateData = {};
    if (newAmount !== null && !isNaN(parseFloat(newAmount)))
      updateData.amount = parseFloat(newAmount);
    if (newCategory !== null && newCategory !== expense.category)
      updateData.category = newCategory;
    if (newTaskID !== null && newTaskID !== expense.task_id)
      updateData.task_id = newTaskID;

    if (Object.keys(updateData).length > 0) {
      updateExpense(expense.expense_id, updateData);
    } else {
      showMessage(
        adminAllExpensesList.parentElement.querySelector(".message-box") ||
          adminAllExpensesList,
        "No changes detected.",
        "error"
      );
    }
  }

  async function updateExpense(expenseId, updateData) {
    try {
      const result = await apiRequest(
        `/expenses/${expenseId}`,
        "PUT",
        updateData
      );
      showMessage(
        adminAllExpensesList.parentElement.querySelector(".message-box") ||
          adminAllExpensesList,
        result.message,
        "success"
      );
      fetchAllExpenses(); // Refresh list
    } catch (error) {
      showMessage(
        adminAllExpensesList.parentElement.querySelector(".message-box") ||
          adminAllExpensesList,
        error.message,
        "error"
      );
    }
  }

  async function deleteExpense(expenseId) {
    if (confirm(`Are you sure you want to delete expense ${expenseId}?`)) {
      try {
        const result = await apiRequest(`/expenses/${expenseId}`, "DELETE");
        showMessage(
          adminAllExpensesList.parentElement.querySelector(".message-box") ||
            adminAllExpensesList,
          result.message,
          "success"
        );
        fetchAllExpenses(); // Refresh list
      } catch (error) {
        showMessage(
          adminAllExpensesList.parentElement.querySelector(".message-box") ||
            adminAllExpensesList,
          error.message,
          "error"
        );
      }
    }
  }

  async function fetchAdminReports() {
    try {
      // Task Summary
      const taskSummary = await apiRequest("/reports/tasks", "GET");
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
      const attendanceReport = await apiRequest("/reports/attendance", "GET");
      reportAdminAttendance.innerHTML =
        '<h5 class="font-semibold mb-2">Attendance Report:</h5>';
      if (attendanceReport.length === 0) {
        reportAdminAttendance.innerHTML +=
          '<p class="text-gray-600">No attendance data.</p>';
      } else {
        const table = document.createElement("table");
        table.className =
          "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
        table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Date</th><th>User ID</th><th>Task ID</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
        const tbody = table.querySelector("tbody");
        attendanceReport.forEach((log) => {
          const row = tbody.insertRow();
          row.className = "table-row";
          row.insertCell().textContent = log.date;
          row.insertCell().textContent = log.user_id;
          row.insertCell().textContent = log.task_id;
        });
        reportAdminAttendance.appendChild(table);
      }

      // Ratings Summary
      const ratingsSummary = await apiRequest("/reports/ratings", "GET");
      reportAdminRatings.innerHTML =
        '<h5 class="font-semibold mb-2">Ratings Summary:</h5>';
      if (Object.keys(ratingsSummary).length === 0) {
        reportAdminRatings.innerHTML +=
          '<p class="text-gray-600">No ratings data.</p>';
      } else {
        const ul = document.createElement("ul");
        ul.className = "list-disc list-inside text-gray-700 space-y-2";
        for (const volId in ratingsSummary) {
          const data = ratingsSummary[volId];
          const li = document.createElement("li");
          li.innerHTML = `<strong>${
            data.volunteer_name
          } (${volId}):</strong> Avg Score: ${data.average_score.toFixed(
            2
          )}/5, Comments: "${data.comments.join('", "')}"`;
          ul.appendChild(li);
        }
        reportAdminRatings.appendChild(ul);
      }

      // Expenses Report (reusing general expenses fetch)
      const expensesReport = await apiRequest("/reports/expenses", "GET");
      reportAdminExpenses.innerHTML =
        '<h5 class="font-semibold mb-2">Expenses Report:</h5>';
      if (expensesReport.length === 0) {
        reportAdminExpenses.innerHTML +=
          '<p class="text-gray-600">No expense data.</p>';
      } else {
        const table = document.createElement("table");
        table.className =
          "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
        table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task ID</th><th>Amount</th><th>Category</th><th>Logged By</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
        const tbody = table.querySelector("tbody");
        expensesReport.forEach((item) => {
          const row = tbody.insertRow();
          row.className = "table-row";
          row.insertCell().textContent = item.task_id;
          row.insertCell().textContent = `$${item.amount.toFixed(2)}`;
          row.insertCell().textContent = item.category;
          row.insertCell().textContent = item.logged_by;
        });
        reportAdminExpenses.appendChild(table);
      }

      // Assignment Logs (reusing general assignments fetch)
      const assignmentLogs = await apiRequest("/reports/assignments", "GET");
      reportAdminAssignments.innerHTML =
        '<h5 class="font-semibold mb-2">Assignment Logs:</h5>';
      if (assignmentLogs.length === 0) {
        reportAdminAssignments.innerHTML +=
          '<p class="text-gray-600">No assignment logs.</p>';
      } else {
        const table = document.createElement("table");
        table.className =
          "min-w-full divide-y divide-gray-200 rounded-lg overflow-hidden shadow-sm";
        table.innerHTML = `
                <thead class="bg-gray-100"><tr class="table-header"><th>Task</th><th>Assigned To</th><th>Role</th><th>Deadline</th><th>Status</th></tr></thead>
                <tbody class="bg-white divide-y divide-gray-200"></tbody>
            `;
        const tbody = table.querySelector("tbody");
        assignmentLogs.forEach((item) => {
          const row = tbody.insertRow();
          row.className = "table-row";
          row.insertCell().textContent = item.title;
          row.insertCell().textContent = `${item.assigned_to_name} (${item.assigned_to_id})`;
          row.insertCell().textContent = item.role;
          row.insertCell().textContent = item.deadline;
          row.insertCell().textContent = item.status;
        });
        reportAdminAssignments.appendChild(table);
      }
    } catch (error) {
      console.error("Error fetching admin reports:", error);
      reportAdminTasks.innerHTML = `<p class="text-red-600">Error loading task summary: ${error.message}</p>`;
      reportAdminAttendance.innerHTML = `<p class="text-red-600">Error loading attendance report: ${error.message}</p>`;
      reportAdminRatings.innerHTML = `<p class="text-red-600">Error loading ratings summary: ${error.message}</p>`;
      reportAdminExpenses.innerHTML = `<p class="text-red-600">Error loading expenses report: ${error.message}</p>`;
      reportAdminAssignments.innerHTML = `<p class="text-red-600">Error loading assignment logs: ${error.message}</p>`;
    }
  }

  async function loadVolunteerDashboard() {
    const data = await apiRequest("/dashboard/volunteer", "GET");
    document.getElementById("volunteer-name").textContent = data.name;
    document.getElementById("volunteer-attendance").textContent =
      data.attendance_percent + "%";
    document.getElementById("volunteer-rating").textContent =
      data.average_rating;
    // Render tasks and team as needed
  }

  // --- Initial Load ---
  document.addEventListener("DOMContentLoaded", function () {
    // Check if user is already logged in
    checkSession();
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

  // === DASHBOARD WIDGETS LOGIC ===
  async function updateDashboardWidgets() {
    try {
      // Fetch dashboard summary (role-based)
      let summary = {};
      let role = window.sessionRole || "admin"; // fallback
      if (!role && window.sessionStorage) role = sessionStorage.getItem("role");
      let url = "/dashboard/admin";
      if (role === "coordinator") url = "/dashboard/coordinator";
      if (role === "volunteer") url = "/dashboard/volunteer";
      const res = await fetch(url, { credentials: "include" });
      if (res.ok) summary = await res.json();
      // Tasks
      document.getElementById("dashboard-tasks-count").textContent =
        summary.tasks ? summary.tasks.length : summary.total_tasks || "--";
      // Attendance
      document.getElementById("dashboard-attendance-rate").textContent =
        summary.attendance_percent !== undefined
          ? summary.attendance_percent + "%"
          : "--%";
      // Ratings
      document.getElementById("dashboard-average-rating").textContent =
        summary.average_rating !== undefined ? summary.average_rating : "--";
      // Expenses
      document.getElementById("dashboard-expenses-total").textContent =
        summary.expenses_total !== undefined
          ? "$" + summary.expenses_total
          : "--";
      // Reports (dummy: count of tasks+attendance+ratings+expenses)
      let reportsCount = 0;
      if (summary.tasks) reportsCount += summary.tasks.length;
      if (summary.attendance_percent) reportsCount += 1;
      if (summary.average_rating) reportsCount += 1;
      if (summary.expenses_total) reportsCount += 1;
      document.getElementById("dashboard-reports-count").textContent =
        reportsCount || "--";
      // Volunteers
      document.getElementById("dashboard-volunteers-count").textContent =
        summary.team ? summary.team.length : "--";
      // Welcome message
      if (summary.name)
        document.getElementById("volunteer-name").textContent = summary.name;
      if (role)
        document.getElementById("volunteer-role").textContent =
          "(" + role.charAt(0).toUpperCase() + role.slice(1) + ")";
    } catch (e) {
      // fallback to --
    }
  }

  // Notifications and Activity (dummy for now, can be wired to backend)
  function updateDashboardNotifications() {
    const notifications = [
      { msg: 'Task "Cleanup Drive" marked as completed.', time: "2m ago" },
      { msg: "New volunteer registered.", time: "10m ago" },
      { msg: "Expense report submitted.", time: "1h ago" },
    ];
    const notifList = document.getElementById("dashboard-notifications-list");
    notifList.innerHTML = "";
    notifications.forEach((n) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class='font-semibold text-gray-700'>${n.msg}</span> <span class='text-xs text-gray-400 ml-2'>${n.time}</span>`;
      notifList.appendChild(li);
    });
  }
  function updateDashboardActivity() {
    const activity = [
      { msg: 'Attendance marked for "Food Distribution".', time: "Today" },
      { msg: "Rating submitted for Volunteer One.", time: "Yesterday" },
      { msg: 'Task "Event Setup" assigned.', time: "2 days ago" },
    ];
    const actList = document.getElementById("dashboard-activity-list");
    actList.innerHTML = "";
    activity.forEach((a) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class='font-semibold text-gray-700'>${a.msg}</span> <span class='text-xs text-gray-400 ml-2'>${a.time}</span>`;
      actList.appendChild(li);
    });
  }

  // Quick action buttons
  function setupDashboardQuickActions() {
    const showTab =
      window.showTab ||
      function (id) {
        document.getElementById(id).classList.remove("hidden");
      };
    document.getElementById("dashboard-add-task-btn").onclick = () =>
      showTab("admin-tasks");
    document.getElementById("dashboard-mark-attendance-btn").onclick = () =>
      showTab("admin-attendance");
    document.getElementById("dashboard-add-rating-btn").onclick = () =>
      showTab("admin-ratings");
    document.getElementById("dashboard-add-expense-btn").onclick = () =>
      showTab("admin-expenses");
    document.getElementById("dashboard-view-reports-btn").onclick = () =>
      showTab("admin-reports");
    document.getElementById("dashboard-view-volunteers-btn").onclick = () =>
      showTab("admin-users");
  }

  // Unified search (dashboard only)
  document
    .getElementById("dashboard-search")
    .addEventListener("input", function (e) {
      // Implement search/filter logic across dashboard widgets if needed
    });

  // Theme toggle (dashboard only)
  document.getElementById("dashboard-theme-toggle").onclick = function () {
    document.getElementById("dashboard-section").classList.toggle("dark");
  };

  // Auto-refresh every 30s
  setInterval(() => {
    updateDashboardWidgets();
    updateDashboardNotifications();
    updateDashboardActivity();
  }, 30000);

  // Initial load
  if (document.getElementById("dashboard-section")) {
    updateDashboardWidgets();
    updateDashboardNotifications();
    updateDashboardActivity();
    setupDashboardQuickActions();
  }

  // On dashbords.html, check session and show dashboard if logged in
  if (window.location.pathname.includes("dashbords")) {
    checkSession();
  }

  // ... existing code ...
  window.fetchCoordinatorReports = fetchCoordinatorReports;
})(); // End of IIFE
