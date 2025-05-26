
import urllib.parse
import re

class AuthHandler:
    def __init__(self, database, session_manager):
        self.db = database
        self.session_manager = session_manager

    def login(self, post_data):
        """Handle user login"""
        try:
            # Parse form data
            data = urllib.parse.parse_qs(post_data)
            username = data.get('username', [''])[0].strip()
            password = data.get('password', [''])[0]

            # Validate input
            if not username or not password:
                return {'success': False, 'error': 'Veuillez remplir tous les champs'}

            # Check credentials
            user = self.db.get_user_by_credentials(username, password)
            if not user:
                return {'success': False, 'error': 'Nom d\'utilisateur ou mot de passe incorrect'}

            return {'success': True, 'user': user}

        except Exception as e:
            return {'success': False, 'error': 'Erreur lors de la connexion'}

    def register(self, post_data):
        """Handle user registration"""
        try:
            # Parse form data
            data = urllib.parse.parse_qs(post_data)
            username = data.get('username', [''])[0].strip()
            email = data.get('email', [''])[0].strip()
            password = data.get('password', [''])[0]
            confirm_password = data.get('confirm_password', [''])[0]

            # Validate input
            validation_result = self.validate_registration_data(username, email, password, confirm_password)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}

            # Check if user already exists
            if self.db.get_user_by_username(username):
                return {'success': False, 'error': 'Ce nom d\'utilisateur existe déjà'}

            if self.db.get_user_by_email(email):
                return {'success': False, 'error': 'Cette adresse email est déjà utilisée'}

            # Create user
            user = self.db.create_user(username, email, password)
            if not user:
                return {'success': False, 'error': 'Erreur lors de la création du compte'}

            return {'success': True, 'user': user}

        except Exception as e:
            return {'success': False, 'error': 'Erreur lors de l\'inscription'}

    def validate_registration_data(self, username, email, password, confirm_password):
        """Validate registration form data"""
        # Check if all fields are filled
        if not all([username, email, password, confirm_password]):
            return {'valid': False, 'error': 'Veuillez remplir tous les champs'}

        # Validate username
        if len(username) < 3:
            return {'valid': False, 'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}
        
        if len(username) > 50:
            return {'valid': False, 'error': 'Le nom d\'utilisateur ne peut pas dépasser 50 caractères'}

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return {'valid': False, 'error': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscore'}

        # Validate email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {'valid': False, 'error': 'Adresse email invalide'}

        # Validate password
        if len(password) < 6:
            return {'valid': False, 'error': 'Le mot de passe doit contenir au moins 6 caractères'}

        if len(password) > 100:
            return {'valid': False, 'error': 'Le mot de passe ne peut pas dépasser 100 caractères'}

        # Check password confirmation
        if password != confirm_password:
            return {'valid': False, 'error': 'Les mots de passe ne correspondent pas'}

        return {'valid': True}