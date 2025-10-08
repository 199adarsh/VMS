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
            
            # For local development, prioritize serviceAccountKey.json file
            if os.path.exists('serviceAccountKey.json'):
                print("Using serviceAccountKey.json for Firebase initialization")
                # Use service account key file for local development
                try:
                    cred = credentials.Certificate('serviceAccountKey.json')
                    firebase_admin.initialize_app(cred)
                    print("Firebase initialized with serviceAccountKey.json")
                except Exception as e:
                    print(f"Error loading serviceAccountKey.json: {e}")
                    # Try to use default credentials as fallback
                    firebase_admin.initialize_app()
            # For production (Vercel), use environment variables
            elif os.getenv('FIREBASE_PROJECT_ID'):
                print("Using environment variables for Firebase initialization")
                # Get private key and properly format it
                private_key = os.getenv('FIREBASE_PRIVATE_KEY', '')
                if private_key:
                    # Handle both escaped and unescaped newlines
                    private_key = private_key.replace('\\n', '\n')
                    # Ensure proper PEM format
                    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                        private_key = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
                
                cred_dict = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": private_key,
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
                }
                print(f"Firebase project ID: {cred_dict['project_id']}")
                print(f"Client email: {cred_dict['client_email']}")
                
                # Validate required fields
                required_fields = ['project_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if not cred_dict.get(field)]
                if missing_fields:
                    print(f"ERROR: Missing required Firebase environment variables: {missing_fields}")
                    raise ValueError(f"Missing required Firebase environment variables: {missing_fields}")
                
                print(f"DEBUG: All required fields present. Project ID: {cred_dict['project_id']}")
                print(f"DEBUG: Client email: {cred_dict['client_email']}")
                print(f"DEBUG: Private key starts with: {cred_dict['private_key'][:50]}...")
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("SUCCESS: Firebase initialized with environment variables")
            else:
                print("Using default credentials for Firebase initialization")
                # Use default credentials (for development with Firebase emulator or GCP)
                firebase_admin.initialize_app()
            
            self.db = firestore.client()
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            print("Firebase initialization failed. App will run without Firebase features.")
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
