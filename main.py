
import http.server
import socketserver
import urllib.parse
import json
import os
import mimetypes
from database import Database
from handlers.auth_handler import AuthHandler
from handlers.article_handler import ArticleHandler
from handlers.user_handler import UserHandler
from utils.session_manager import SessionManager
from utils.template_engine import TemplateEngine

class BlogHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.session_manager = SessionManager()
        self.template_engine = TemplateEngine()
        self.auth_handler = AuthHandler(self.db, self.session_manager)
        self.article_handler = ArticleHandler(self.db, self.session_manager)
        self.user_handler = UserHandler(self.db, self.session_manager)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Get session
        session_id = self.get_session_id()
        user = self.session_manager.get_user(session_id) if session_id else None
        
        # Route handling
        if path == '/' or path == '/home':
            self.handle_home(user)
        elif path == '/login':
            self.handle_login_page(user)
        elif path == '/register':
            self.handle_register_page(user)
        elif path == '/logout':
            self.handle_logout()
        elif path == '/create-article':
            self.handle_create_article_page(user)
        elif path.startswith('/article/'):
            article_id = path.split('/')[-1]
            self.handle_article_detail(article_id, user)
        elif path.startswith('/edit-article/'):
            article_id = path.split('/')[-1]
            self.handle_edit_article_page(article_id, user)
        elif path == '/my-articles':
            self.handle_my_articles(user)
        elif path == '/liked-articles':
            self.handle_liked_articles(user)
        elif path == '/saved-articles':
            self.handle_saved_articles(user)
        elif path.startswith('/static/'):
            self.handle_static_file(path)
        else:
            self.handle_404()

    def do_POST(self):
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # Get session
        session_id = self.get_session_id()
        user = self.session_manager.get_user(session_id) if session_id else None
        
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Route handling
        if path == '/login':
            self.handle_login_submit(post_data)
        elif path == '/register':
            self.handle_register_submit(post_data)
        elif path == '/create-article':
            self.handle_create_article_submit(post_data, user)
        elif path.startswith('/edit-article/'):
            article_id = path.split('/')[-1]
            self.handle_edit_article_submit(article_id, post_data, user)
        elif path.startswith('/delete-article/'):
            article_id = path.split('/')[-1]
            self.handle_delete_article(article_id, user)
        elif path.startswith('/like-article/'):
            article_id = path.split('/')[-1]
            self.handle_like_article(article_id, user)
        elif path.startswith('/save-article/'):
            article_id = path.split('/')[-1]
            self.handle_save_article(article_id, user)
        elif path.startswith('/comment-article/'):
            article_id = path.split('/')[-1]
            self.handle_comment_article(article_id, post_data, user)
        else:
            self.handle_404()

    def get_session_id(self):
        """Extract session ID from cookies"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            for cookie in cookie_header.split(';'):
                if cookie.strip().startswith('session_id='):
                    return cookie.strip().split('=')[1]
        return None

    def set_session_cookie(self, session_id):
        """Set session cookie"""
        self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')

    def handle_home(self, user):
        """Handle home page"""
        articles = self.db.get_all_articles()
        context = {
            'user': user,
            'articles': articles,
            'title': 'Accueil - Blog Platform'
        }
        html = self.template_engine.render('index.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_login_page(self, user):
        """Handle login page"""
        if user:
            self.redirect('/')
            return
        
        context = {'title': 'Connexion - Blog Platform'}
        html = self.template_engine.render('auth/login.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_register_page(self, user):
        """Handle register page"""
        if user:
            self.redirect('/')
            return
        
        context = {'title': 'Inscription - Blog Platform'}
        html = self.template_engine.render('auth/register.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_login_submit(self, post_data):
        """Handle login form submission"""
        result = self.auth_handler.login(post_data)
        if result['success']:
            session_id = self.session_manager.create_session(result['user'])
            self.send_response(302)
            self.set_session_cookie(session_id)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            context = {
                'title': 'Connexion - Blog Platform',
                'error': result['error']
            }
            html = self.template_engine.render('auth/login.html', context)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

    def handle_register_submit(self, post_data):
        """Handle register form submission"""
        result = self.auth_handler.register(post_data)
        if result['success']:
            session_id = self.session_manager.create_session(result['user'])
            self.send_response(302)
            self.set_session_cookie(session_id)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            context = {
                'title': 'Inscription - Blog Platform',
                'error': result['error']
            }
            html = self.template_engine.render('auth/register.html', context)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

    def handle_logout(self):
        """Handle logout"""
        session_id = self.get_session_id()
        if session_id:
            self.session_manager.destroy_session(session_id)
        
        self.send_response(302)
        self.send_header('Set-Cookie', 'session_id=; Path=/; HttpOnly; expires=Thu, 01 Jan 1970 00:00:00 GMT')
        self.send_header('Location', '/')
        self.end_headers()

    def handle_create_article_page(self, user):
        """Handle create article page"""
        if not user:
            self.redirect('/login')
            return
        
        context = {
            'user': user,
            'title': 'Créer un article - Blog Platform'
        }
        html = self.template_engine.render('articles/create.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_create_article_submit(self, post_data, user):
        """Handle create article form submission"""
        if not user:
            self.redirect('/login')
            return
        
        result = self.article_handler.create_article(post_data, user['id'])
        if result['success']:
            self.redirect(f"/article/{result['article_id']}")
        else:
            context = {
                'user': user,
                'title': 'Créer un article - Blog Platform',
                'error': result['error']
            }
            html = self.template_engine.render('articles/create.html', context)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

    def handle_article_detail(self, article_id, user):
        """Handle article detail page"""
        article = self.db.get_article_by_id(article_id)
        if not article:
            self.handle_404()
            return
        
        comments = self.db.get_article_comments(article_id)
        is_liked = self.db.is_article_liked(article_id, user['id']) if user else False
        is_saved = self.db.is_article_saved(article_id, user['id']) if user else False
        
        context = {
            'user': user,
            'article': article,
            'comments': comments,
            'is_liked': is_liked,
            'is_saved': is_saved,
            'title': f"{article['title']} - Blog Platform"
        }
        html = self.template_engine.render('articles/detail.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_edit_article_page(self, article_id, user):
        """Handle edit article page"""
        if not user:
            self.redirect('/login')
            return
        
        article = self.db.get_article_by_id(article_id)
        if not article or article['author_id'] != user['id']:
            self.handle_404()
            return
        
        context = {
            'user': user,
            'article': article,
            'title': f"Modifier {article['title']} - Blog Platform"
        }
        html = self.template_engine.render('articles/edit.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_edit_article_submit(self, article_id, post_data, user):
        """Handle edit article form submission"""
        if not user:
            self.redirect('/login')
            return
        
        result = self.article_handler.edit_article(article_id, post_data, user['id'])
        if result['success']:
            self.redirect(f"/article/{article_id}")
        else:
            article = self.db.get_article_by_id(article_id)
            context = {
                'user': user,
                'article': article,
                'title': f"Modifier {article['title']} - Blog Platform",
                'error': result['error']
            }
            html = self.template_engine.render('articles/edit.html', context)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

    def handle_delete_article(self, article_id, user):
        """Handle delete article"""
        if not user:
            self.send_json_response({'success': False, 'error': 'Non authentifié'})
            return
        
        result = self.article_handler.delete_article(article_id, user['id'])
        if result['success']:
            self.redirect('/my-articles')
        else:
            self.send_json_response(result)

    def handle_like_article(self, article_id, user):
        """Handle like/unlike article"""
        if not user:
            self.send_json_response({'success': False, 'error': 'Non authentifié'})
            return
        
        result = self.article_handler.toggle_like(article_id, user['id'])
        self.send_json_response(result)

    def handle_save_article(self, article_id, user):
        """Handle save/unsave article"""
        if not user:
            self.send_json_response({'success': False, 'error': 'Non authentifié'})
            return
        
        result = self.article_handler.toggle_save(article_id, user['id'])
        self.send_json_response(result)

    def handle_comment_article(self, article_id, post_data, user):
        """Handle add comment to article"""
        if not user:
            self.send_json_response({'success': False, 'error': 'Non authentifié'})
            return
        
        result = self.article_handler.add_comment(article_id, post_data, user['id'])
        self.send_json_response(result)

    def handle_my_articles(self, user):
        """Handle my articles page"""
        if not user:
            self.redirect('/login')
            return
        
        articles = self.db.get_user_articles(user['id'])
        context = {
            'user': user,
            'articles': articles,
            'title': 'Mes articles - Blog Platform'
        }
        html = self.template_engine.render('user/my_articles.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_liked_articles(self, user):
        """Handle liked articles page"""
        if not user:
            self.redirect('/login')
            return
        
        articles = self.db.get_liked_articles(user['id'])
        context = {
            'user': user,
            'articles': articles,
            'title': 'Articles aimés - Blog Platform'
        }
        html = self.template_engine.render('user/liked_articles.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_saved_articles(self, user):
        """Handle saved articles page"""
        if not user:
            self.redirect('/login')
            return
        
        articles = self.db.get_saved_articles(user['id'])
        context = {
            'user': user,
            'articles': articles,
            'title': 'Articles sauvegardés - Blog Platform'
        }
        html = self.template_engine.render('user/saved_articles.html', context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_static_file(self, path):
        """Handle static files (CSS, JS, images)"""
        file_path = path[1:]  # Remove leading slash
        
        if not os.path.exists(file_path):
            self.handle_404()
            return
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.handle_404()

    def handle_404(self):
        """Handle 404 errors"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - Page non trouvée</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>404 - Page non trouvée</h1>
            <p><a href="/">Retour à l'accueil</a></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def redirect(self, location):
        """Send redirect response"""
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    def send_json_response(self, data):
        """Send JSON response"""
        json_data = json.dumps(data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))

def run_server(port=8000):
    """Run the HTTP server"""
    handler = BlogHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serveur démarré sur http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            httpd.shutdown()

if __name__ == "__main__":
    # Initialize database
    db = Database()
    db.init_database()
    
    # Run server
    run_server()