// AI Components for Smart Volunteering Portal

// EmailJS Integration
class EmailNotificationService {
  constructor() {
    this.isInitialized = false;
    this.init();
  }

  init() {
    // Load EmailJS script dynamically
    if (!window.emailjs) {
      const script = document.createElement("script");
      script.src =
        "https://cdn.jsdelivr.net/npm/@emailjs/browser@3/dist/email.min.js";
      script.onload = () => {
        this.setupEmailJS();
      };
      document.head.appendChild(script);
    } else {
      this.setupEmailJS();
    }
  }

  setupEmailJS() {
    // Initialize EmailJS with credentials from config
    const publicKey = window.EMAILJS_CONFIG?.PUBLIC_KEY || "YOUR_PUBLIC_KEY";
    emailjs.init(publicKey);
    this.isInitialized = true;
    console.log("EmailJS initialized with key:", publicKey);
  }

  async sendTaskAssignedEmail(
    volunteerEmail,
    volunteerName,
    taskTitle,
    taskDescription,
    deadline
  ) {
    if (!this.isInitialized) {
      console.error("EmailJS not initialized");
      return false;
    }

    try {
      const templateParams = {
        to_email: volunteerEmail,
        volunteer_name: volunteerName,
        subject: `New Task Assigned: ${taskTitle}`,
        message: `Hello ${volunteerName},\n\nYou have been assigned a new task:\n\nTask: ${taskTitle}\nDescription: ${taskDescription}\nDeadline: ${deadline}\n\nPlease log in to your VMS dashboard to view full details and get started.\n\nBest regards,\nVMS Coordinator`,
        from_name: "VMS Coordinator",
      };

      const serviceId = window.EMAILJS_CONFIG?.SERVICE_ID || "YOUR_SERVICE_ID";
      const templateId =
        window.EMAILJS_CONFIG?.TEMPLATES?.NOTIFICATION ||
        "notification_template";
      const result = await emailjs.send(serviceId, templateId, templateParams);
      console.log("Task assigned email sent:", result);
      return true;
    } catch (error) {
      console.error("Error sending task assigned email:", error);
      return false;
    }
  }

  async sendAnnouncementEmail(
    volunteerEmail,
    volunteerName,
    announcementTitle,
    announcementContent
  ) {
    if (!this.isInitialized) {
      console.error("EmailJS not initialized");
      return false;
    }

    try {
      const templateParams = {
        to_email: volunteerEmail,
        volunteer_name: volunteerName,
        subject: announcementTitle,
        message: `Hello ${volunteerName},\n\n${announcementContent}\n\nBest regards,\nVMS Coordinator`,
        from_name: "VMS Coordinator",
      };

      const serviceId = window.EMAILJS_CONFIG?.SERVICE_ID || "YOUR_SERVICE_ID";
      const templateId =
        window.EMAILJS_CONFIG?.TEMPLATES?.NOTIFICATION ||
        "notification_template";
      const result = await emailjs.send(serviceId, templateId, templateParams);
      console.log("Announcement email sent:", result);
      return true;
    } catch (error) {
      console.error("Error sending announcement email:", error);
      return false;
    }
  }

  async sendTaskCompletedEmail(
    coordinatorEmail,
    coordinatorName,
    volunteerName,
    taskTitle,
    completionNotes
  ) {
    if (!this.isInitialized) {
      console.error("EmailJS not initialized");
      return false;
    }

    try {
      const templateParams = {
        to_email: coordinatorEmail,
        coordinator_name: coordinatorName,
        subject: `Task Completed: ${taskTitle}`,
        message: `Hello ${coordinatorName},\n\n${volunteerName} has completed the following task:\n\nTask: ${taskTitle}\nNotes: ${
          completionNotes || "Task completed successfully"
        }\n\nPlease review the completion in your VMS dashboard.\n\nBest regards,\nVMS System`,
        from_name: "VMS System",
      };

      const serviceId = window.EMAILJS_CONFIG?.SERVICE_ID || "YOUR_SERVICE_ID";
      const templateId =
        window.EMAILJS_CONFIG?.TEMPLATES?.ADMIN || "admin_template";
      const result = await emailjs.send(serviceId, templateId, templateParams);
      console.log("Task completed email sent:", result);
      return true;
    } catch (error) {
      console.error("Error sending task completed email:", error);
      return false;
    }
  }
}

// Global email service instance (declared later)

class AITaskGuide {
  constructor() {
    this.modal = null;
    this.currentTaskId = null;
  }

  // Show AI Task Completion Guide Modal
  showTaskGuide(taskId, taskTitle) {
    this.currentTaskId = taskId;
    this.createModal(taskTitle);
    this.loadTaskGuide(taskId);
  }

  createModal(taskTitle) {
    // Remove existing modal if any
    if (this.modal) {
      this.modal.remove();
    }

    const modalHTML = `
            <div id="ai-task-guide-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div class="bg-white rounded-xl max-w-5xl w-full max-h-[95vh] overflow-hidden shadow-2xl">
                    <div class="flex justify-between items-center p-6 border-b bg-gradient-to-r from-blue-50 to-purple-50">
                        <h3 class="text-2xl font-bold text-gray-900">
                            <i class="fas fa-robot text-blue-500 mr-3"></i>
                            AI Task Completion Guide
                        </h3>
                        <button onclick="aiTaskGuide.closeModal()" class="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-100">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    <div class="p-6 overflow-y-auto max-h-[calc(95vh-140px)]">
                        <div class="mb-6">
                            <h4 class="text-xl font-semibold text-gray-800 mb-3 bg-gray-100 p-3 rounded-lg">${taskTitle}</h4>
                            <div id="guide-loading" class="text-center py-12">
                                <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-500"></div>
                                <p class="mt-4 text-gray-600 text-lg">Generating AI-powered completion guide...</p>
                                <p class="mt-2 text-gray-400 text-sm">This may take a few seconds</p>
                            </div>
                        </div>
                        <div id="guide-content" class="hidden">
                            <!-- Guide content will be loaded here -->
                        </div>
                        <div id="guide-error" class="hidden text-center py-12">
                            <i class="fas fa-exclamation-triangle text-red-500 text-6xl mb-6"></i>
                            <p class="text-red-600 text-lg mb-4">Failed to generate guide. Please try again.</p>
                            <button onclick="aiTaskGuide.loadTaskGuide('${this.currentTaskId}')" 
                                    class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium">
                                <i class="fas fa-redo mr-2"></i>Retry
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

    document.body.insertAdjacentHTML("beforeend", modalHTML);
    this.modal = document.getElementById("ai-task-guide-modal");
  }

  async loadTaskGuide(taskId) {
    try {
      const response = await fetch(`/ai/task-guide/${taskId}`, {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.success) {
        this.displayGuide(data.guide);
      } else {
        this.showError();
      }
    } catch (error) {
      console.error("Error loading task guide:", error);
      this.showError();
    }
  }

  displayGuide(guide) {
    const loadingEl = document.getElementById("guide-loading");
    const contentEl = document.getElementById("guide-content");
    const errorEl = document.getElementById("guide-error");

    loadingEl.classList.add("hidden");
    errorEl.classList.add("hidden");
    contentEl.classList.remove("hidden");

    contentEl.innerHTML = `
            <div class="space-y-6">
                <!-- Overview -->
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h5 class="font-semibold text-blue-900 mb-2">
                        <i class="fas fa-lightbulb mr-2"></i>Overview
                    </h5>
                    <p class="text-blue-800">${guide.overview}</p>
                </div>

                <!-- Steps -->
                <div>
                    <h5 class="font-semibold text-gray-900 mb-4">
                        <i class="fas fa-list-ol mr-2"></i>Step-by-Step Guide
                    </h5>
                    <div class="space-y-6">
                        ${guide.steps
                          .map(
                            (step, index) => `
                            <div class="flex items-start space-x-6 p-6 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                                <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                                    ${step.step}
                                </div>
                                <div class="flex-1">
                                    <h6 class="font-semibold text-gray-900 mb-3 text-lg">${step.title}</h6>
                                    <p class="text-gray-700 mb-4 leading-relaxed">${step.description}</p>
                                    <div class="flex items-center text-sm text-blue-600 bg-blue-50 px-3 py-2 rounded-lg inline-block">
                                        <i class="fas fa-clock mr-2"></i>
                                        <span class="font-medium">${step.estimated_time}</span>
                                    </div>
                                </div>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>

                <!-- Pro Tips -->
                <div class="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200">
                    <h5 class="font-semibold text-green-900 mb-4 text-lg">
                        <i class="fas fa-lightbulb mr-3 text-yellow-500"></i>Pro Tips
                    </h5>
                    <ul class="space-y-3">
                        ${(guide.pro_tips || guide.tips || [])
                          .map(
                            (tip) => `
                            <li class="flex items-start space-x-3 text-green-800">
                                <i class="fas fa-check-circle text-green-500 mt-1 flex-shrink-0"></i>
                                <span class="leading-relaxed">${tip}</span>
                            </li>`
                          )
                          .join("")}
                    </ul>
                </div>

                <!-- Things to Avoid -->
                <div class="bg-gradient-to-r from-yellow-50 to-orange-50 p-6 rounded-xl border border-yellow-200">
                    <h5 class="font-semibold text-yellow-900 mb-4 text-lg">
                        <i class="fas fa-exclamation-triangle mr-3 text-orange-500"></i>Things to Avoid
                    </h5>
                    <ul class="space-y-3">
                        ${(guide.things_to_avoid || guide.pitfalls || [])
                          .map(
                            (item) => `
                            <li class="flex items-start space-x-3 text-yellow-800">
                                <i class="fas fa-times-circle text-red-500 mt-1 flex-shrink-0"></i>
                                <span class="leading-relaxed">${item}</span>
                            </li>`
                          )
                          .join("")}
                    </ul>
                </div>

                <!-- Success Criteria -->
                ${
                  guide.success_criteria
                    ? `
                <div class="bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-xl border border-purple-200">
                    <h5 class="font-semibold text-purple-900 mb-4 text-lg">
                        <i class="fas fa-check-circle mr-3 text-purple-500"></i>Success Criteria
                    </h5>
                    <p class="text-purple-800 leading-relaxed text-lg">${guide.success_criteria}</p>
                </div>
                `
                    : ""
                }

                <!-- Total Time -->
                <div class="bg-gradient-to-r from-blue-100 to-indigo-100 p-6 rounded-xl text-center border border-blue-200">
                    <div class="flex items-center justify-center space-x-3">
                        <i class="fas fa-stopwatch text-blue-600 text-2xl"></i>
                        <div>
                            <p class="text-gray-700 text-lg font-medium">Total Estimated Time</p>
                            <p class="text-blue-600 text-2xl font-bold">${
                              guide.total_estimated_time
                            }</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
  }

  showError() {
    const loadingEl = document.getElementById("guide-loading");
    const contentEl = document.getElementById("guide-content");
    const errorEl = document.getElementById("guide-error");

    loadingEl.classList.add("hidden");
    contentEl.classList.add("hidden");
    errorEl.classList.remove("hidden");
  }

  closeModal() {
    if (this.modal) {
      this.modal.remove();
      this.modal = null;
    }
  }
}

class AIChatbot {
  constructor() {
    this.isOpen = false;
    this.chatContainer = null;
    this.messageHistory = [];
  }

  // Toggle chatbot visibility
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  open() {
    this.createChatInterface();
    this.isOpen = true;
  }

  close() {
    if (this.chatContainer) {
      this.chatContainer.remove();
      this.chatContainer = null;
    }
    this.isOpen = false;
  }

  createChatInterface() {
    const chatHTML = `
            <div id="ai-chatbot" class="fixed bottom-4 right-4 w-80 h-96 bg-white rounded-lg shadow-lg border z-50 flex flex-col">
                <!-- Header -->
                <div class="bg-blue-500 text-white p-4 rounded-t-lg flex justify-between items-center">
                    <div class="flex items-center">
                        <i class="fas fa-robot mr-2"></i>
                        <span class="font-semibold">AI Assistant</span>
                    </div>
                    <button onclick="aiChatbot.close()" class="text-white hover:text-gray-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <!-- Messages -->
                <div id="chat-messages" class="flex-1 p-4 overflow-y-auto space-y-3">
                    <div class="text-center text-gray-500 text-sm">
                        <i class="fas fa-robot mr-1"></i>
                        Hi! I am your AI assistant. How can I help you today?
                    </div>
                    <div id="quick-actions" class="flex flex-wrap gap-2 justify-center">
                        <!-- Quick actions will be populated based on user role -->
                    </div>
                </div>

                <!-- Input -->
                <div class="p-4 border-t">
                    <div class="flex space-x-2">
                        <input type="text" id="chat-input" placeholder="Type your message..." 
                               class="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                               onkeypress="if(event.key==='Enter') aiChatbot.sendMessage()">
                        <button onclick="aiChatbot.sendMessage()" 
                                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

    document.body.insertAdjacentHTML("beforeend", chatHTML);
    this.chatContainer = document.getElementById("ai-chatbot");

    // Focus on input
    document.getElementById("chat-input").focus();

    // Load quick actions based on user role
    this.loadQuickActions();
  }

  async loadQuickActions() {
    try {
      // Get user role from the page or make an API call
      const response = await fetch("/user/profile", { credentials: "include" });
      const userData = await response.json();
      const userRole = userData.role || "volunteer";

      this.populateQuickActions(userRole);
    } catch (error) {
      console.log("Could not determine user role, using default actions");
      this.populateQuickActions("volunteer");
    }
  }

  populateQuickActions(userRole) {
    const quickActionsContainer = document.getElementById("quick-actions");
    if (!quickActionsContainer) return;

    let actions = [];

    if (userRole === "coordinator" || userRole === "admin") {
      actions = [
        {
          text: "Create Task",
          message: "How do I create a new task?",
          color: "blue",
        },
        {
          text: "Assign Volunteers",
          message: "How do I assign volunteers to tasks?",
          color: "green",
        },
        {
          text: "AI Recommendations",
          message: "How do I use AI volunteer recommendations?",
          color: "purple",
        },
        {
          text: "Track Attendance",
          message: "How do I track volunteer attendance?",
          color: "orange",
        },
        {
          text: "View Reports",
          message: "How do I view reports and analytics?",
          color: "indigo",
        },
      ];
    } else {
      actions = [
        {
          text: "My Tasks",
          message: "How do I view my assigned tasks?",
          color: "blue",
        },
        {
          text: "Mark Complete",
          message: "How do I mark a task as completed?",
          color: "green",
        },
        {
          text: "Check Attendance",
          message: "How do I check my attendance?",
          color: "purple",
        },
        {
          text: "Get Help",
          message: "I need help with something",
          color: "orange",
        },
      ];
    }

    quickActionsContainer.innerHTML = actions
      .map(
        (action) =>
          `<button onclick="aiChatbot.sendQuickMessage('${action.message}')" 
              class="px-3 py-1 bg-${action.color}-100 text-${action.color}-700 text-xs rounded-full hover:bg-${action.color}-200">
        ${action.text}
      </button>`
      )
      .join("");
  }

  sendQuickMessage(message) {
    // Set the input value and send the message
    const input = document.getElementById("chat-input");
    input.value = message;
    this.sendMessage();
  }

  async sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    this.addMessage(message, "user");
    input.value = "";

    // Show typing indicator
    this.addTypingIndicator();

    try {
      const response = await fetch("/ai/chatbot", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      });

      const data = await response.json();

      // Remove typing indicator
      this.removeTypingIndicator();

      if (data.success) {
        this.addMessage(data.response, "bot");
      } else {
        this.addMessage(
          "Sorry, I encountered an error. Please try again.",
          "bot"
        );
      }
    } catch (error) {
      console.error("Chatbot error:", error);
      this.removeTypingIndicator();
      this.addMessage(
        "Sorry, I am having trouble connecting. Please try again.",
        "bot"
      );
    }
  }

  addMessage(message, sender) {
    const messagesContainer = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");

    const isUser = sender === "user";
    messageDiv.className = `flex ${isUser ? "justify-end" : "justify-start"}`;

    messageDiv.innerHTML = `
            <div class="max-w-xs px-3 py-2 rounded-lg ${
              isUser ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"
            }">
                ${message}
            </div>
        `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  addTypingIndicator() {
    const messagesContainer = document.getElementById("chat-messages");
    const typingDiv = document.createElement("div");
    typingDiv.id = "typing-indicator";
    typingDiv.className = "flex justify-start";
    typingDiv.innerHTML = `
            <div class="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg">
                <i class="fas fa-robot mr-1"></i>
                <span class="typing-dots">Typing</span>
            </div>
        `;

    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  removeTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
}

class AIRecommendations {
  constructor() {
    this.recommendations = [];
  }

  async loadRecommendations() {
    try {
      // First check if user is a coordinator
      const userResponse = await fetch("/user/profile", {
        credentials: "include",
      });
      const userData = await userResponse.json();

      if (userData.role !== "coordinator" && userData.role !== "admin") {
        this.hideRecommendationsForVolunteers();
        return;
      }

      console.log("Loading AI recommendations...");

      // Set a timeout for the request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch("/ai/recommendations", {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      console.log("Response status:", response.status);

      const data = await response.json();
      console.log("Response data:", data);

      if (data.success) {
        this.recommendations = data.recommendations.recommendations || [];
        console.log("Recommendations loaded:", this.recommendations.length);
        this.displayRecommendations();
      } else {
        console.error("Failed to load recommendations:", data.message);
        this.showRecommendationsError(
          data.message || "Failed to load recommendations"
        );
      }
    } catch (error) {
      console.error("Error loading recommendations:", error);
      if (error.name === "AbortError") {
        this.showRecommendationsError("Request timed out. Please try again.");
      } else {
        this.showRecommendationsError(
          "Network error. Please check your connection."
        );
      }
    }
  }

  hideRecommendationsForVolunteers() {
    const section = document.getElementById("ai-recommendations-section");
    if (!section) return;

    // Hide the entire recommendations section (including title) for volunteers
    section.style.display = "none";
  }

  showCoordinatorOnlyMessage() {
    const container = document.getElementById("ai-recommendations");
    if (!container) return;

    container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-user-shield text-4xl mb-4 text-blue-500"></i>
                <p class="text-lg font-medium mb-2">Coordinator Feature</p>
                <p class="text-sm">AI task recommendations are only available to coordinators and administrators.</p>
                <div class="mt-4 text-xs text-gray-400">
                    <i class="fas fa-info-circle mr-1"></i>
                    This feature helps coordinators assign the right volunteers to tasks
                </div>
            </div>
        `;
  }

  showRecommendationsError(message) {
    const container = document.getElementById("ai-recommendations");
    if (!container) return;

    container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4 text-yellow-500"></i>
                <p class="text-lg font-medium mb-2">AI Recommendations Unavailable</p>
                <p class="text-sm">${message}</p>
                <button onclick="aiRecommendations.loadRecommendations()" 
                        class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    <i class="fas fa-refresh mr-2"></i>Retry
                </button>
                <div class="mt-4 text-xs text-gray-400">
                    <i class="fas fa-info-circle mr-1"></i>
                    This may take up to 30 seconds to load
                </div>
            </div>
        `;
  }

  displayRecommendations() {
    const container = document.getElementById("ai-recommendations");
    if (!container) return;

    if (this.recommendations.length === 0) {
      // Show fallback recommendations instead of empty state
      this.showFallbackRecommendations();
      return;
    }

    container.innerHTML = `
            <div class="space-y-4">
                <div class="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-4">
                    <h3 class="font-semibold text-blue-900 mb-2">
                        <i class="fas fa-robot mr-2"></i>AI Volunteer Recommendations
                    </h3>
                    <p class="text-blue-800 text-sm">These volunteers are recommended based on their skills, experience, and availability for optimal task assignment.</p>
                </div>
                ${this.recommendations
                  .map(
                    (rec) => `
                    <div class="bg-white p-4 rounded-lg border hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start mb-2">
                            <h4 class="font-semibold text-gray-900">${
                              rec.volunteer_name || rec.title
                            }</h4>
                            <span class="px-2 py-1 text-xs rounded-full ${this.getConfidenceColor(
                              rec.confidence
                            )}">
                                ${rec.confidence || "Medium"} Confidence
                            </span>
                        </div>
                        <p class="text-gray-600 text-sm mb-3">${rec.reason}</p>
                        <div class="flex justify-between items-center">
                            <div class="flex items-center space-x-2">
                                <div class="w-16 bg-gray-200 rounded-full h-2">
                                    <div class="bg-blue-500 h-2 rounded-full" style="width: ${
                                      rec.match_score
                                    }%"></div>
                                </div>
                                <span class="text-xs text-gray-500">${
                                  rec.match_score
                                }% match</span>
                            </div>
                            <button onclick="aiRecommendations.assignVolunteer('${
                              rec.volunteer_id || rec.task_id
                            }')" 
                                    class="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600">
                                <i class="fas fa-user-plus mr-1"></i>Assign
                            </button>
                        </div>
                    </div>
                `
                  )
                  .join("")}
            </div>
        `;
  }

  getConfidenceColor(confidence) {
    switch (confidence?.toLowerCase()) {
      case "high":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  }

  getDifficultyColor(difficulty) {
    switch (difficulty?.toLowerCase()) {
      case "easy":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "hard":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  }

  assignVolunteer(volunteerId) {
    // This would integrate with your existing volunteer assignment functionality
    console.log("Assign volunteer:", volunteerId);
    // You can implement volunteer assignment logic here
    // For now, show an alert
    alert(
      `Assigning volunteer ${volunteerId} to task. This feature will be integrated with the task assignment system.`
    );
  }

  viewTask(taskId) {
    // This would integrate with your existing task viewing functionality
    console.log("View task:", taskId);
    // You can implement task viewing logic here
  }

  showFallbackRecommendations() {
    const container = document.getElementById("ai-recommendations");
    if (!container) return;

    container.innerHTML = `
            <div class="space-y-4">
                <div class="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-4">
                    <h3 class="font-semibold text-blue-900 mb-2">
                        <i class="fas fa-robot mr-2"></i>AI Volunteer Recommendations
                    </h3>
                    <p class="text-blue-800 text-sm">These volunteers are recommended based on their skills, experience, and availability for optimal task assignment.</p>
                </div>
                
                <div class="bg-white p-4 rounded-lg border hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-semibold text-gray-900">John Smith</h4>
                        <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                            High Confidence
                        </span>
                    </div>
                    <p class="text-gray-600 text-sm mb-3">Experienced volunteer with strong organizational skills and previous event coordination experience.</p>
                    <div class="flex justify-between items-center">
                        <div class="flex items-center space-x-2">
                            <div class="w-16 bg-gray-200 rounded-full h-2">
                                <div class="bg-blue-500 h-2 rounded-full" style="width: 90%"></div>
                            </div>
                            <span class="text-xs text-gray-500">90% match</span>
                        </div>
                        <button onclick="aiRecommendations.assignVolunteer('demo-vol-1')" 
                                class="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600">
                            <i class="fas fa-user-plus mr-1"></i>Assign
                        </button>
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg border hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-semibold text-gray-900">Sarah Johnson</h4>
                        <span class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                            Medium Confidence
                        </span>
                    </div>
                    <p class="text-gray-600 text-sm mb-3">Reliable volunteer with good communication skills and flexible availability.</p>
                    <div class="flex justify-between items-center">
                        <div class="flex items-center space-x-2">
                            <div class="w-16 bg-gray-200 rounded-full h-2">
                                <div class="bg-blue-500 h-2 rounded-full" style="width: 75%"></div>
                            </div>
                            <span class="text-xs text-gray-500">75% match</span>
                        </div>
                        <button onclick="aiRecommendations.assignVolunteer('demo-vol-2')" 
                                class="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600">
                            <i class="fas fa-user-plus mr-1"></i>Assign
                        </button>
                    </div>
                </div>
                
                <div class="text-center text-sm text-gray-500 mt-4">
                    <i class="fas fa-info-circle mr-1"></i>
                    AI recommendations are being loaded. These are sample volunteer recommendations.
                </div>
            </div>
        `;
  }
}

// Initialize AI components when DOM is ready
let aiTaskGuide, aiChatbot, aiRecommendations, emailService;

document.addEventListener("DOMContentLoaded", function () {
  console.log("Initializing AI components...");
  aiTaskGuide = new AITaskGuide();
  aiChatbot = new AIChatbot();
  aiRecommendations = new AIRecommendations();
  emailService = new EmailNotificationService();

  // Make them globally available
  window.aiTaskGuide = aiTaskGuide;
  window.aiChatbot = aiChatbot;
  window.aiRecommendations = aiRecommendations;
  window.emailService = emailService;

  console.log("AI components initialized:", {
    aiTaskGuide: !!window.aiTaskGuide,
    aiChatbot: !!window.aiChatbot,
    aiRecommendations: !!window.aiRecommendations,
    emailService: !!window.emailService,
  });
});

// Add AI buttons to task cards
function addAITaskGuideButton(taskId, taskTitle) {
  return `
        <button onclick="if(window.aiTaskGuide) { window.aiTaskGuide.showTaskGuide('${taskId}', '${taskTitle}'); } else { alert('AI Guide is loading, please try again in a moment.'); }" 
                class="px-3 py-1 bg-purple-500 text-white text-sm rounded hover:bg-purple-600 flex items-center">
            <i class="fas fa-robot mr-1"></i>
            AI Guide
        </button>
    `;
}

// Add chatbot toggle button
function addChatbotToggleButton() {
  return `
        <button onclick="aiChatbot.toggle()" 
                class="fixed bottom-4 right-4 w-12 h-12 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 z-40">
            <i class="fas fa-robot"></i>
        </button>
    `;
}

// Load recommendations when page loads
document.addEventListener("DOMContentLoaded", function () {
  // Add chatbot toggle button
  document.body.insertAdjacentHTML("beforeend", addChatbotToggleButton());

  // Load recommendations if container exists with a delay to ensure page is fully loaded
  if (document.getElementById("ai-recommendations")) {
    setTimeout(() => {
      if (window.aiRecommendations) {
        window.aiRecommendations.loadRecommendations();
      }
    }, 1000);
  }
});
