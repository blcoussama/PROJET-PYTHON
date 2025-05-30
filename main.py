from flask import (
    Flask, render_template, request, redirect,
    url_for, make_response, jsonify, abort
)
from database import Database
from handlers.auth_handler import AuthHandler
from handlers.article_handler import ArticleHandler
from handlers.user_handler import UserHandler
from utils.session_manager import SessionManager
from datetime import datetime

app = Flask(
    __name__,
    template_folder="templates"  # répertoire des templates
)

# ── Filtres de Template ─────────────────────────────────────────────
@app.template_filter('format_date')
def format_date_filter(date_value):
    """Formate la date pour l'affichage dans les templates"""
    if isinstance(date_value, str):
        # Si c'est une chaîne, essayer de l'analyser
        try:
            date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Essayer différents formats courants
                date_value = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return date_value  # Retourner tel quel si impossible à analyser
    
    if isinstance(date_value, datetime):
        return date_value.strftime('%d %B %Y à %H:%M')
    
    return str(date_value)  # Solution de secours vers représentation string

@app.template_filter('truncate')
def truncate_filter(text, length=100):
    """Tronque le texte à la longueur spécifiée et ajoute des points de suspension si nécessaire"""
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= length:
        return text
    
    return text[:length].rstrip() + "..."

# Alternative: on peut aussi les ajouter comme fonctions globales
# @app.template_global()
# def format_date(date_value):
#     return format_date_filter(date_value)
# 
# @app.template_global()
# def truncate(text, length=100):
#     return truncate_filter(text, length)

# ── Initialisation ──────────────────────────────────────────────────
db = Database()
db.init_database()

session_mgr = SessionManager()
auth_h = AuthHandler(db, session_mgr)
article_h = ArticleHandler(db, session_mgr)
user_h = UserHandler(db, session_mgr)


# ── Fonctions d'aide ────────────────────────────────────────────────
def get_current_user():
    sid = request.cookies.get("session_id")
    return session_mgr.get_user(sid) if sid else None

def set_session_cookie(resp, session_id):
    resp.set_cookie("session_id", session_id, httponly=True, path="/")


# ── Routes ──────────────────────────────────────────────────────────
@app.route("/")
def home():
    user = get_current_user()
    articles = db.get_all_articles()
    return render_template(
        "index.html",
        title="Accueil - Blog Platform",
        user=user,
        articles=articles
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    user = get_current_user()
    if user:
        return redirect(url_for("home"))

    if request.method == "POST":
        result = auth_h.login(request.get_data(as_text=True))
        if result["success"]:
            sid = session_mgr.create_session(result["user"])
            resp = make_response(redirect(url_for("home")))
            set_session_cookie(resp, sid)
            return resp
        return render_template(
            "auth/login.html",
            title="Connexion - Blog Platform",
            error=result["error"]
        )

    return render_template("auth/login.html", title="Connexion - Blog Platform")


@app.route("/register", methods=["GET", "POST"])
def register():
    user = get_current_user()
    if user:
        return redirect(url_for("home"))

    if request.method == "POST":
        result = auth_h.register(request.get_data(as_text=True))
        if result["success"]:
            sid = session_mgr.create_session(result["user"])
            resp = make_response(redirect(url_for("home")))
            set_session_cookie(resp, sid)
            return resp
        return render_template(
            "auth/register.html",
            title="Inscription - Blog Platform",
            error=result["error"]
        )

    return render_template("auth/register.html", title="Inscription - Blog Platform")


@app.route("/logout")
def logout():
    sid = request.cookies.get("session_id")
    if sid:
        session_mgr.destroy_session(sid)
    resp = make_response(redirect(url_for("home")))
    resp.set_cookie("session_id", "", expires=0, path="/")
    return resp


@app.route("/create-article", methods=["GET", "POST"])
def create_article():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        result = article_h.create_article(request.get_data(as_text=True), user["id"])
        if result["success"]:
            return redirect(url_for("article_detail", article_id=result["article_id"]))
        return render_template(
            "articles/create.html",
            title="Créer un article - Blog Platform",
            user=user,
            error=result["error"]
        )

    return render_template(
        "articles/create.html",
        title="Créer un article - Blog Platform",
        user=user
    )


@app.route("/article/<int:article_id>")
def article_detail(article_id):
    user = get_current_user()
    article = db.get_article_by_id(article_id) or abort(404)
    comments = db.get_article_comments(article_id)
    is_liked = db.is_article_liked(article_id, user["id"]) if user else False
    is_saved = db.is_article_saved(article_id, user["id"]) if user else False

    return render_template(
        "articles/detail.html",
        title=f"{article['title']} - Blog Platform",
        user=user,
        article=article,
        comments=comments,
        is_liked=is_liked,
        is_saved=is_saved
    )


@app.route("/edit-article/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    article = db.get_article_by_id(article_id) or abort(404)
    if article["author_id"] != user["id"]:
        abort(403)

    if request.method == "POST":
        result = article_h.edit_article(article_id, request.get_data(as_text=True), user["id"])
        if result["success"]:
            return redirect(url_for("article_detail", article_id=article_id))
        return render_template(
            "articles/edit.html",
            title=f"Modifier {article['title']} - Blog Platform",
            user=user,
            article=article,
            error=result["error"]
        )

    return render_template(
        "articles/edit.html",
        title=f"Modifier {article['title']} - Blog Platform",
        user=user,
        article=article
    )


@app.route("/delete-article/<int:article_id>", methods=["POST"])
def delete_article(article_id):
    user = get_current_user()
    if not user:
        return jsonify(success=False, error="Non authentifié"), 401

    result = article_h.delete_article(article_id, user["id"])
    return jsonify(result)


@app.route("/like-article/<int:article_id>", methods=["POST"])
def like_article(article_id):
    user = get_current_user()
    if not user:
        return jsonify(success=False, error="Non authentifié"), 401
    return jsonify(article_h.toggle_like(article_id, user["id"]))


@app.route("/save-article/<int:article_id>", methods=["POST"])
def save_article(article_id):
    user = get_current_user()
    if not user:
        return jsonify(success=False, error="Non authentifié"), 401
    return jsonify(article_h.toggle_save(article_id, user["id"]))


@app.route("/comment-article/<int:article_id>", methods=["POST"])
def comment_article(article_id):
    user = get_current_user()
    if not user:
        return jsonify(success=False, error="Non authentifié"), 401
    return jsonify(article_h.add_comment(article_id, request.get_data(as_text=True), user["id"]))


@app.route("/my-articles")
def my_articles():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    articles = db.get_user_articles(user["id"])
    return render_template(
        "user/my_articles.html",
        title="Mes articles - Blog Platform",
        user=user,
        articles=articles
    )


@app.route("/liked-articles")
def liked_articles():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    articles = db.get_liked_articles(user["id"])
    return render_template(
        "user/liked_articles.html",
        title="Articles aimés - Blog Platform",
        user=user,
        articles=articles
    )


@app.route("/saved-articles")
def saved_articles():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    articles = db.get_saved_articles(user["id"])
    return render_template(
        "user/saved_articles.html",
        title="Articles sauvegardés - Blog Platform",
        user=user,
        articles=articles
    )


# ── Exécution ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8000)