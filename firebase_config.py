import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Optional

class FirebaseConfig:
    """Firebase configuration and initialization"""
    
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.db = firestore.client()
                return
            
            # For production (Vercel), use environment variables
            if os.getenv('FIREBASE_PROJECT_ID'):
                cred_dict = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
                    "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
                }
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            elif os.path.exists('serviceAccountKey.json'):
                # Use service account key file for local development
                cred = credentials.Certificate('serviceAccountKey.json')
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for development with Firebase emulator or GCP)
                firebase_admin.initialize_app()
            
            self.db = firestore.client()
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            # Fallback to in-memory storage for development
            self.db = None
    
    def get_db(self):
        """Get Firestore database instance"""
        return self.db

# Global Firebase instance
firebase_config = FirebaseConfig()

def get_firestore_db():
    """Get Firestore database instance"""
    return firebase_config.get_db()
