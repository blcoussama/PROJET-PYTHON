
import sqlite3
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="data/blog.db"):
        self.db_path = db_path
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT
                content TEXT NOT NULL,
                image_filename TEXT,
                author_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        ''')

        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                article_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Likes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(article_id, user_id),
                FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Saved articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(article_id, user_id),
                FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password, hash_password):
        """Verify password against hash"""
        return self.hash_password(password) == hash_password

    # User methods
    def create_user(self, username, email, password):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            user_id = cursor.lastrowid
            conn.commit()
            return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_user_by_credentials(self, username, password):
        """Get user by username and password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user['password_hash']):
            return dict(user)
        return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, created_at FROM users WHERE id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None

    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, created_at FROM users WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None

    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, created_at FROM users WHERE email = ?
        ''', (email,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None

    # Article methods
    def create_article(self, title, description, content, image_filename, author_id):
        """Create a new article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO articles (title, description, content, image_filename, author_id)
            VALUES (?, ?, ?, ?)
        ''', (title, description, content, image_filename, author_id))
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return article_id

    def get_article_by_id(self, article_id):
        """Get article by ID with author info"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.username as author_name,
                   (SELECT COUNT(*) FROM likes WHERE article_id = a.id) as likes_count,
                   (SELECT COUNT(*) FROM comments WHERE article_id = a.id) as comments_count
            FROM articles a
            JOIN users u ON a.author_id = u.id
            WHERE a.id = ?
        ''', (article_id,))
        article = cursor.fetchone()
        conn.close()
        
        return dict(article) if article else None

    def get_all_articles(self, limit=50):
        """Get all articles with pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.username as author_name,
                   (SELECT COUNT(*) FROM likes WHERE article_id = a.id) as likes_count,
                   (SELECT COUNT(*) FROM comments WHERE article_id = a.id) as comments_count
            FROM articles a
            JOIN users u ON a.author_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ?
        ''', (limit,))
        articles = cursor.fetchall()
        conn.close()
        
        return [dict(article) for article in articles]

    def get_user_articles(self, user_id):
        """Get articles by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.username as author_name,
                   (SELECT COUNT(*) FROM likes WHERE article_id = a.id) as likes_count,
                   (SELECT COUNT(*) FROM comments WHERE article_id = a.id) as comments_count
            FROM articles a
            JOIN users u ON a.author_id = u.id
            WHERE a.author_id = ?
            ORDER BY a.created_at DESC
        ''', (user_id,))
        articles = cursor.fetchall()
        conn.close()
        
        return [dict(article) for article in articles]

    def update_article(self, article_id, title, description, content, image_filename):
        """Update an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
+            UPDATE articles
+            SET title = ?, description = ?, content = ?, image_filename = ?, updated_at = CURRENT_TIMESTAMP
+            WHERE id = ?
+        ''', (title, description, content, image_filename, article_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

    def delete_article(self, article_id, user_id):
        """Delete an article (only by author)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM articles WHERE id = ? AND author_id = ?
        ''', (article_id, user_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

    # Comment methods
    def add_comment(self, article_id, user_id, content):
        """Add a comment to an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments (article_id, user_id, content)
            VALUES (?, ?, ?)
        ''', (article_id, user_id, content))
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return comment_id

    def get_article_comments(self, article_id):
        """Get comments for an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.username as author_name
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.article_id = ?
            ORDER BY c.created_at DESC
        ''', (article_id,))
        comments = cursor.fetchall()
        conn.close()
        
        return [dict(comment) for comment in comments]

    # Like methods
    def toggle_like(self, article_id, user_id):
        """Toggle like for an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already liked
        cursor.execute('''
            SELECT id FROM likes WHERE article_id = ? AND user_id = ?
        ''', (article_id, user_id))
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Remove like
            cursor.execute('''
                DELETE FROM likes WHERE article_id = ? AND user_id = ?
            ''', (article_id, user_id))
            liked = False
        else:
            # Add like
            cursor.execute('''
                INSERT INTO likes (article_id, user_id) VALUES (?, ?)
            ''', (article_id, user_id))
            liked = True
        
        conn.commit()
        
        # Get new likes count
        cursor.execute('''
            SELECT COUNT(*) as count FROM likes WHERE article_id = ?
        ''', (article_id,))
        likes_count = cursor.fetchone()['count']
        
        conn.close()
        
        return {'liked': liked, 'likes_count': likes_count}

    def is_article_liked(self, article_id, user_id):
        """Check if article is liked by user"""
        if not user_id:
            return False
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM likes WHERE article_id = ? AND user_id = ?
        ''', (article_id, user_id))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None

    def get_liked_articles(self, user_id):
        """Get articles liked by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.username as author_name,
                   (SELECT COUNT(*) FROM likes WHERE article_id = a.id) as likes_count,
                   (SELECT COUNT(*) FROM comments WHERE article_id = a.id) as comments_count
            FROM articles a
            JOIN users u ON a.author_id = u.id
            JOIN likes l ON a.id = l.article_id
            WHERE l.user_id = ?
            ORDER BY l.created_at DESC
        ''', (user_id,))
        articles = cursor.fetchall()
        conn.close()
        
        return [dict(article) for article in articles]

    # Save methods
    def toggle_save(self, article_id, user_id):
        """Toggle save for an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already saved
        cursor.execute('''
            SELECT id FROM saved_articles WHERE article_id = ? AND user_id = ?
        ''', (article_id, user_id))
        existing_save = cursor.fetchone()
        
        if existing_save:
            # Remove save
            cursor.execute('''
                DELETE FROM saved_articles WHERE article_id = ? AND user_id = ?
            ''', (article_id, user_id))
            saved = False
        else:
            # Add save
            cursor.execute('''
                INSERT INTO saved_articles (article_id, user_id) VALUES (?, ?)
            ''', (article_id, user_id))
            saved = True
        
        conn.commit()
        conn.close()
        
        return {'saved': saved}

    def is_article_saved(self, article_id, user_id):
        """Check if article is saved by user"""
        if not user_id:
            return False
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM saved_articles WHERE article_id = ? AND user_id = ?
        ''', (article_id, user_id))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None

    def get_saved_articles(self, user_id):
        """Get articles saved by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.username as author_name,
                   (SELECT COUNT(*) FROM likes WHERE article_id = a.id) as likes_count,
                   (SELECT COUNT(*) FROM comments WHERE article_id = a.id) as comments_count
            FROM articles a
            JOIN users u ON a.author_id = u.id
            JOIN saved_articles s ON a.id = s.article_id
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
        ''', (user_id,))
        articles = cursor.fetchall()
        conn.close()
        
        return [dict(article) for article in articles]