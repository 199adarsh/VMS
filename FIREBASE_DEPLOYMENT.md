# Firebase Deployment Guide for VMS

This guide will help you deploy your Vehicle Management System (VMS) on Firebase using Firebase Functions and Hosting.

## Prerequisites

1. **Node.js and npm** installed on your system
2. **Firebase CLI** installed globally
3. **Python 3.11** (for Firebase Functions)
4. A **Firebase project** created

## Installation Steps

### 1. Install Firebase CLI

```bash
npm install -g firebase-tools
```

### 2. Login to Firebase

```bash
firebase login
```

### 3. Initialize Firebase in your project

```bash
firebase init
```

When prompted:

- Select **Functions** and **Hosting**
- Choose your Firebase project
- For Functions: Select **Python** as the language
- For Hosting: Use `public` as the public directory

### 4. Update Firebase Project ID

Edit `.firebaserc` and replace `your-firebase-project-id` with your actual Firebase project ID:

```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

## Project Structure

```
VMS/
├── functions/
│   ├── main.py                 # Main Flask app with Firebase Functions
│   ├── requirements.txt        # Python dependencies
│   ├── database_service.py     # Database service
│   ├── firebase_auth_service.py # Firebase auth service
│   ├── firebase_config.py      # Firebase configuration
│   └── ai_service.py          # AI service
├── public/
│   ├── static/                # Static files (CSS, JS, images)
│   └── templates/             # HTML templates
├── firebase.json              # Firebase configuration
├── .firebaserc               # Firebase project settings
└── deploy-firebase.ps1       # Windows deployment script
```

## Environment Variables

Set up the following environment variables in your Firebase project:

1. Go to Firebase Console → Project Settings → Service Accounts
2. Generate a new private key
3. Set the following environment variables in Firebase Functions:

```bash
firebase functions:config:set firebase.project_id="your-project-id"
firebase functions:config:set firebase.private_key_id="your-private-key-id"
firebase functions:config:set firebase.private_key="your-private-key"
firebase functions:config:set firebase.client_email="your-client-email"
firebase functions:config:set firebase.client_id="your-client-id"
firebase functions:config:set firebase.auth_uri="https://accounts.google.com/o/oauth2/auth"
firebase functions:config:set firebase.token_uri="https://oauth2.googleapis.com/token"
firebase functions:config:set firebase.auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs"
firebase functions:config:set firebase.client_x509_cert_url="your-client-x509-cert-url"
firebase functions:config:set flask.secret_key="your-secret-key"
```

## Deployment

### Option 1: Using the deployment script

**Windows (PowerShell):**

```powershell
.\deploy-firebase.ps1
```

**Linux/Mac:**

```bash
chmod +x deploy-firebase.sh
./deploy-firebase.sh
```

### Option 2: Manual deployment

```bash
# Deploy everything
firebase deploy

# Deploy only functions
firebase deploy --only functions

# Deploy only hosting
firebase deploy --only hosting
```

## Accessing Your Application

After successful deployment, your application will be available at:

- **Hosting URL**: `https://your-project-id.web.app`
- **Functions URL**: `https://your-project-id.web.app/api/`

## Troubleshooting

### Common Issues

1. **Firebase Functions timeout**: Increase timeout in `firebase.json`
2. **Memory issues**: Increase memory allocation for functions
3. **CORS issues**: Check CORS configuration in `main.py`
4. **Static files not loading**: Verify file paths in `firebase.json`

### Debugging

1. **View logs**:

   ```bash
   firebase functions:log
   ```

2. **Test locally**:

   ```bash
   firebase emulators:start
   ```

3. **Check function status**:
   ```bash
   firebase functions:list
   ```

## Configuration Files

### firebase.json

```json
{
  "functions": {
    "source": "functions",
    "runtime": "python311",
    "predeploy": ["pip install -r requirements.txt"]
  },
  "hosting": {
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "/api/**",
        "function": "api"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

### functions/requirements.txt

```
Flask==2.3.3
Flask-CORS==4.0.0
firebase-admin==6.2.0
Werkzeug==2.3.7
functions-framework==3.*
PyJWT==2.8.0
requests==2.31.0
python-dotenv==1.0.0
google-generativeai==0.3.2
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive keys to version control
2. **CORS**: Configure CORS properly for production
3. **Authentication**: Implement proper authentication mechanisms
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints

## Monitoring

1. **Firebase Console**: Monitor function executions and errors
2. **Google Cloud Console**: Monitor resource usage and costs
3. **Logs**: Use Firebase Functions logs for debugging

## Next Steps

1. Set up custom domain (optional)
2. Configure SSL certificates
3. Set up monitoring and alerting
4. Implement CI/CD pipeline
5. Add performance monitoring

For more information, visit the [Firebase Documentation](https://firebase.google.com/docs).
