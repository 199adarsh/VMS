# VMS Deployment Guide

## Deploy to Vercel

### Prerequisites

1. Vercel account (free at vercel.com)
2. Firebase project with Firestore enabled
3. Git repository (GitHub recommended)

### Steps

#### 1. Prepare Firebase Credentials

1. Go to Firebase Console → Project Settings → Service Accounts
2. Generate new private key (downloads JSON file)
3. Extract these values from the JSON:
   - `project_id`
   - `private_key_id`
   - `private_key` (keep the \n characters)
   - `client_email`
   - `client_id`
   - `auth_uri`
   - `token_uri`
   - `auth_provider_x509_cert_url`
   - `client_x509_cert_url`

#### 2. Deploy to Vercel

1. Push your code to GitHub
2. Go to vercel.com and import your repository
3. In Vercel dashboard, go to Settings → Environment Variables
4. Add these environment variables:
   ```
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=your-client-email
   FIREBASE_CLIENT_ID=your-client-id
   FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
   FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
   FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
   FIREBASE_CLIENT_X509_CERT_URL=your-client-cert-url
   FLASK_SECRET_KEY=your-super-secret-key-here
   ```
5. Deploy!

#### 3. Test Your Deployment

- Visit your Vercel URL
- Test login/registration
- Check if data persists in Firebase

### Alternative: Railway/Render

If Vercel doesn't work, try:

- **Railway**: railway.app (supports Python better)
- **Render**: render.com (free tier available)

### Troubleshooting

- Check Vercel function logs for errors
- Ensure all environment variables are set
- Verify Firebase rules allow your operations
- Test locally with environment variables first
