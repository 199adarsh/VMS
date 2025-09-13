# Firebase Setup Guide for VMS

This guide will help you set up Firebase as the database for your Vehicle Management System (VMS).

## Prerequisites

1. A Google account
2. Python 3.7 or higher
3. pip package manager

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "vms-database")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Firestore Database

1. In your Firebase project, go to "Firestore Database" in the left sidebar
2. Click "Create database"
3. Choose "Start in test mode" for development (you can secure it later)
4. Select a location for your database (choose the closest to your users)
5. Click "Done"

## Step 3: Generate Service Account Key

1. Go to Project Settings (gear icon) → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file and rename it to `serviceAccountKey.json`
4. Place this file in your project root directory (same level as `backend.py`)

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run Migration Script

To populate your Firebase database with sample data:

```bash
python migrate_to_firebase.py
```

## Step 6: Start the Application

```bash
python backend.py
```

## Security Rules (Optional)

For production, update your Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to all documents for authenticated users
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Environment Variables (Optional)

For better security, you can use environment variables instead of the service account key file:

1. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account key file
2. Or set the `FIREBASE_PROJECT_ID` environment variable

## Troubleshooting

### Common Issues:

1. **"Firebase not initialized" error**: Make sure your `serviceAccountKey.json` file is in the correct location
2. **Permission denied**: Check your Firestore security rules
3. **Connection timeout**: Verify your internet connection and Firebase project settings

### Testing the Connection:

You can test if Firebase is working by running:

```python
from firebase_config import get_firestore_db
db = get_firestore_db()
if db:
    print("Firebase connected successfully!")
else:
    print("Firebase connection failed!")
```

## Data Structure

The VMS system uses the following Firestore collections:

- `users`: User accounts (volunteers, coordinators, admins)
- `tasks`: Task assignments and details
- `attendance_logs`: Attendance records
- `ratings`: Performance ratings and feedback
- `expenses`: Expense tracking
- `absentees_logs`: Absence records

## Next Steps

1. Customize the security rules for your specific needs
2. Set up monitoring and alerts in Firebase Console
3. Consider implementing data backup strategies
4. Add authentication if needed (Firebase Auth)

## Support

If you encounter any issues, check the [Firebase Documentation](https://firebase.google.com/docs) or the [Firebase Admin SDK Python Documentation](https://firebase.google.com/docs/admin/setup).
