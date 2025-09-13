import firebase_admin
from firebase_admin import auth
import requests
import json
from typing import Optional, Dict, Any
import os

class FirebaseAuthService:
    """Firebase Authentication service for Google Auth and user management"""
    
    def __init__(self):
        self.firebase_project_id = os.getenv('FIREBASE_PROJECT_ID', 'smart-volunteering-portal')
        self.google_public_keys_url = f"https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        self._public_keys = None
    
    def get_google_public_keys(self) -> Dict[str, str]:
        """Get Google's public keys for JWT verification"""
        if not self._public_keys:
            try:
                response = requests.get(self.google_public_keys_url, timeout=10)
                response.raise_for_status()
                self._public_keys = response.json()
            except Exception as e:
                print(f"Error fetching Google public keys: {e}")
                return {}
        return self._public_keys
    
    def verify_google_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        try:
            print(f"Attempting to verify Google token: {id_token[:50]}...")
            
            # Check if Firebase Admin is initialized
            if not firebase_admin._apps:
                print("Firebase Admin not initialized!")
                return None
            
            # Use Firebase Admin SDK to verify the token
            decoded_token = auth.verify_id_token(id_token)
            print(f"Token verified successfully: {decoded_token}")
            
            # Extract user information
            user_info = {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'email_verified': decoded_token.get('email_verified', False),
                'provider': 'google',
                'firebase_claims': decoded_token
            }
            
            print(f"Extracted user info: {user_info}")
            return user_info
            
        except Exception as e:
            print(f"Error verifying Google token: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> str:
        """Create a custom Firebase token for the user"""
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return custom_token.decode('utf-8')
        except Exception as e:
            print(f"Error creating custom token: {e}")
            return None
    
    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user from Firebase Auth by UID"""
        try:
            user_record = auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'photo_url': user_record.photo_url,
                'email_verified': user_record.email_verified,
                'disabled': user_record.disabled,
                'metadata': {
                    'creation_timestamp': user_record.user_metadata.creation_timestamp,
                    'last_sign_in_timestamp': user_record.user_metadata.last_sign_in_timestamp
                }
            }
        except Exception as e:
            print(f"Error getting user by UID: {e}")
            return None
    
    def create_user(self, email: str, password: str, display_name: str = None) -> Optional[Dict[str, Any]]:
        """Create a new user in Firebase Auth"""
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified
            }
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user(self, uid: str, **kwargs) -> bool:
        """Update user in Firebase Auth"""
        try:
            auth.update_user(uid, **kwargs)
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, uid: str) -> bool:
        """Delete user from Firebase Auth"""
        try:
            auth.delete_user(uid)
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def verify_custom_token(self, custom_token: str) -> Optional[Dict[str, Any]]:
        """Verify custom token and return decoded token"""
        try:
            decoded_token = auth.verify_id_token(custom_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying custom token: {e}")
            return None

# Global Firebase Auth service instance
firebase_auth_service = FirebaseAuthService()
