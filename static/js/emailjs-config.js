// EmailJS Configuration
// Replace these with your actual EmailJS credentials

window.EMAILJS_CONFIG = {
  // Your EmailJS Public Key
  PUBLIC_KEY: "0fZktgXQ4vYz_IEBO",

  // Your EmailJS Service ID
  SERVICE_ID: "service_m5zm9vl",

  // Email Template IDs (Only 2 templates needed!)
  TEMPLATES: {
    NOTIFICATION: "notification_template", // Used for all notifications
    ADMIN: "admin_template", // Used for admin/coordinator emails
  },
};

// Instructions:
// 1. Go to https://www.emailjs.com/
// 2. Create an account and get your Public Key and Service ID
// 3. Create ONLY 2 email templates with these IDs:
//    - notification_template (for volunteers)
//    - admin_template (for coordinators)
// 4. Replace the values above with your actual credentials
// 5. The templates should use these variables:
//    - notification_template: {{to_email}}, {{volunteer_name}}, {{subject}}, {{message}}, {{from_name}}
//    - admin_template: {{to_email}}, {{coordinator_name}}, {{subject}}, {{message}}, {{from_name}}
