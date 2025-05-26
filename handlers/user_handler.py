
class UserHandler:
    def __init__(self, database, session_manager):
        self.db = database
        self.session_manager = session_manager

    def get_user_profile(self, user_id):
        """Get user profile information"""
        try:
            user = self.db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'Utilisateur non trouvé'}

            # Get user statistics
            user_articles = self.db.get_user_articles(user_id)
            liked_articles = self.db.get_liked_articles(user_id)
            saved_articles = self.db.get_saved_articles(user_id)

            stats = {
                'articles_count': len(user_articles),
                'liked_count': len(liked_articles),
                'saved_count': len(saved_articles)
            }

            return {
                'success': True,
                'user': user,
                'stats': stats
            }

        except Exception as e:
            return {'success': False, 'error': 'Erreur lors de la récupération du profil'}

    def get_user_articles(self, user_id):
        """Get articles created by user"""
        try:
            articles = self.db.get_user_articles(user_id)
            return {'success': True, 'articles': articles}

        except Exception as e:
            return {'success': False, 'error': 'Erreur lors de la récupération des articles'}

    def get_liked_articles(self, user_id):
        """Get articles liked by user"""
        try:
            articles = self.db.get_liked_articles(user_id)
            return {'success': True, 'articles': articles}

        except Exception as e:
            return {'success': False, 'error': 'Erreur lors de la récupération des articles aimés'}

    def get_saved_articles(self, user_id):
        """Get articles saved by user"""
        try:
            articles = self.db.get_saved_articles(user_id)
            return {'success': True, 'articles': articles}

        except Exception as e:
            return {'success': False, 'error': 'Erreur lors de la récupération des articles sauvegardés'}