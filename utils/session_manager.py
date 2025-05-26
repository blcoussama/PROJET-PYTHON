
import secrets
import json
import os
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, sessions_dir="data/sessions"):
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)
        self.session_duration = timedelta(days=7)  # Sessions valides 7 jours

    def create_session(self, user):
        """Create a new session for user"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'user': user,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + self.session_duration).isoformat()
        }
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        return session_id

    def get_user(self, session_id):
        """Get user from session ID"""
        if not session_id:
            return None
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                self.destroy_session(session_id)
                return None
            
            return session_data['user']
        
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid session file
            self.destroy_session(session_id)
            return None

    def destroy_session(self, session_id):
        """Destroy a session"""
        if not session_id:
            return
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except OSError:
                pass

    def cleanup_expired_sessions(self):
        """Clean up expired session files"""
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    session_file = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                        
                        expires_at = datetime.fromisoformat(session_data['expires_at'])
                        if datetime.now() > expires_at:
                            os.remove(session_file)
                    
                    except (json.JSONDecodeError, KeyError, ValueError, OSError):
                        # Remove invalid session files
                        try:
                            os.remove(session_file)
                        except OSError:
                            pass
        except OSError:
            pass