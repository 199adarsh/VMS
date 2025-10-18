#!/bin/bash

# Firebase Deployment Script for VMS
echo "Starting Firebase deployment for VMS..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "Firebase CLI not found. Please install it first:"
    echo "npm install -g firebase-tools"
    exit 1
fi

# Check if user is logged in
if ! firebase projects:list &> /dev/null; then
    echo "Please login to Firebase first:"
    echo "firebase login"
    exit 1
fi

# Set the project ID (replace with your actual project ID)
read -p "Enter your Firebase project ID: " projectId

if [ ! -z "$projectId" ]; then
    firebase use $projectId
fi

# Deploy functions and hosting
echo "Deploying Firebase Functions and Hosting..."
firebase deploy

echo "Deployment completed!"
echo "Your app should be available at: https://$projectId.web.app"
