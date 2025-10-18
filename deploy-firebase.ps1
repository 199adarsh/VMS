# Firebase Deployment Script for VMS
Write-Host "Starting Firebase deployment for VMS..." -ForegroundColor Green

# Check if Firebase CLI is installed
try {
    firebase --version
} catch {
    Write-Host "Firebase CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g firebase-tools" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in
try {
    firebase projects:list
} catch {
    Write-Host "Please login to Firebase first:" -ForegroundColor Red
    Write-Host "firebase login" -ForegroundColor Yellow
    exit 1
}

# Set the project ID (replace with your actual project ID)
$projectId = Read-Host "Enter your Firebase project ID"

if ($projectId) {
    firebase use $projectId
}

# Deploy functions and hosting
Write-Host "Deploying Firebase Functions and Hosting..." -ForegroundColor Green
firebase deploy

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Your app should be available at: https://$projectId.web.app" -ForegroundColor Cyan
