"""
Application Flask consolidée pour le déploiement sur Vercel
Tous les services et fonctionnalités sont regroupés dans ce fichier unique
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import text
import os
import uuid
import random
import string

# Charger les variables d'environnement depuis .env (pour le développement local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv n'est pas installé, ce n'est pas grave pour la production
    pass

# ============================
#   EXTENSIONS FLASK
# ============================
db = SQLAlchemy()
login_manager = LoginManager()

# ============================
#   MODÈLES
# ============================

class User(UserMixin, db.Model):
    """Modèle pour les utilisateurs administrateurs"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash et stocke le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Order(db.Model):
    """Modèle pour les commandes de livraison"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations de l'expéditeur
    sender_name = db.Column(db.String(100), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    sender_email = db.Column(db.String(120), nullable=False)
    sender_address = db.Column(db.Text, nullable=False)
    
    # Informations du destinataire
    receiver_name = db.Column(db.String(100), nullable=False)
    receiver_phone = db.Column(db.String(20), nullable=False)
    receiver_email = db.Column(db.String(120), nullable=False)
    receiver_address = db.Column(db.Text, nullable=False)
    
    # Détails de l'envoi
    shipment_name = db.Column(db.String(200), nullable=False)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    origin_city = db.Column(db.String(100), nullable=False)
    origin_country = db.Column(db.String(100), nullable=False)
    destination_city = db.Column(db.String(100), nullable=False)
    destination_country = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(200), default='En préparation')
    
    # Planification
    pickup_date = db.Column(db.String(20), nullable=True)
    pickup_time = db.Column(db.String(10), nullable=True)
    delivery_date = db.Column(db.String(20), nullable=True)
    delivery_time = db.Column(db.String(10), nullable=True)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.tracking_number} - {self.shipment_name}>'
    
    def to_dict(self):
        """Convertir l'objet Order en dictionnaire"""
        return {
            'id': self.id,
            'sender_name': self.sender_name,
            'sender_phone': self.sender_phone,
            'sender_email': self.sender_email,
            'sender_address': self.sender_address,
            'receiver_name': self.receiver_name,
            'receiver_phone': self.receiver_phone,
            'receiver_email': self.receiver_email,
            'receiver_address': self.receiver_address,
            'shipment_name': self.shipment_name,
            'tracking_number': self.tracking_number,
            'origin_city': self.origin_city,
            'origin_country': self.origin_country,
            'destination_city': self.destination_city,
            'destination_country': self.destination_country,
            'current_location': self.current_location,
            'pickup_date': self.pickup_date or '',
            'pickup_time': self.pickup_time or '',
            'delivery_date': self.delivery_date or '',
            'delivery_time': self.delivery_time or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================
#   CONFIGURATION DE L'APPLICATION
# ============================

# Configuration des chemins pour les templates et statiques
# Flask cherchera dans app/templates et app/static
# Sur Vercel, le système de fichiers est en lecture seule, donc on ne peut pas utiliser instance_path
# On configure instance_path vers /tmp qui est accessible en écriture
is_vercel = os.environ.get('VERCEL') == '1'

# Déterminer le répertoire de base (où se trouve app.py)
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'app', 'templates')
static_dir = os.path.join(base_dir, 'app', 'static')

# Vérifier que les dossiers existent (pour le débogage)
if not os.path.exists(template_dir):
    print(f"⚠️  ATTENTION: Le dossier templates n'existe pas : {template_dir}")
else:
    print(f"✓ Dossier templates trouvé : {template_dir}")
if not os.path.exists(static_dir):
    print(f"⚠️  ATTENTION: Le dossier static n'existe pas : {static_dir}")
else:
    print(f"✓ Dossier static trouvé : {static_dir}")

if is_vercel:
    # Créer le dossier /tmp/instance si nécessaire (accessible en écriture sur Vercel)
    instance_path = '/tmp/instance'
    try:
        os.makedirs(instance_path, exist_ok=True)
    except Exception:
        # Si on ne peut pas créer le dossier, ne pas utiliser instance_path
        instance_path = None
else:
    instance_path = None

# When deploying on Vercel, static assets are served from `public/**` by the CDN.
# Do not set Flask's `static_folder`/`static_url_path` to avoid conflicts with Vercel.
app = Flask(__name__, template_folder=template_dir)

# Configuration de la base de données
# Sur Vercel, SQLite ne fonctionne pas (pas de persistance)
# Il est fortement recommandé de configurer DATABASE_URL avec une base PostgreSQL
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    if os.environ.get('VERCEL') == '1':
        # Sur Vercel, on ne peut pas utiliser SQLite
        # Utiliser une URL PostgreSQL factice pour éviter les erreurs d'initialisation
        # L'utilisateur devra configurer DATABASE_URL dans les variables d'environnement Vercel
        database_url = 'postgresql://user:pass@localhost/dbname'
        print("⚠️  ERREUR CRITIQUE: DATABASE_URL non configuré sur Vercel")
        print("⚠️  Veuillez configurer DATABASE_URL dans les variables d'environnement Vercel")
        print("⚠️  L'application ne fonctionnera pas correctement sans une base de données PostgreSQL")
    else:
        # Valeur par défaut pour le développement local uniquement
        # Créer le dossier instance s'il n'existe pas
        instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        try:
            os.makedirs(instance_dir, exist_ok=True)
        except Exception as e:
            print(f"⚠️  Erreur lors de la création du dossier instance : {str(e)}")
        database_url = f'sqlite:///{os.path.join(instance_dir, "dev.db")}'
        print("⚠️  ATTENTION: DATABASE_URL non configuré. Utilisation de SQLite (développement local uniquement)")
        print(f"✓ Base de données SQLite : {database_url}")
else:
    # Nettoyer l'URL (supprimer les espaces, etc.)
    database_url = database_url.strip()
    # Pour Render.com PostgreSQL, ajouter le mode SSL si nécessaire
    if 'render.com' in database_url and '?sslmode=' not in database_url:
        # Ajouter le paramètre SSL pour Render
        separator = '&' if '?' in database_url else '?'
        database_url = f"{database_url}{separator}sslmode=require"
    # Pour Vercel avec PostgreSQL, s'assurer que SSL est activé
    if os.environ.get('VERCEL') == '1' and 'postgresql://' in database_url and '?sslmode=' not in database_url:
        separator = '&' if '?' in database_url else '?'
        database_url = f"{database_url}{separator}sslmode=require"
    print("✓ Base de données PostgreSQL configurée")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Configuration des options du moteur SQLAlchemy
# Sur Vercel, on ne peut pas utiliser le système de fichiers pour les pools de connexion
engine_options = {}

# Configurer les options selon le type de base de données
database_url_lower = database_url.lower()
if 'postgresql' in database_url_lower or 'postgres' in database_url_lower:
    # Options pour PostgreSQL
    print("✓ Configuration PostgreSQL détectée")
    engine_options = {
        'pool_pre_ping': True,  # Vérifier les connexions avant utilisation
        'pool_recycle': 300,    # Recycler les connexions après 5 minutes
        'connect_args': {
            'connect_timeout': 10  # Timeout de connexion de 10 secondes (uniquement pour PostgreSQL)
        }
    }
    
    # Sur Vercel, utiliser un pool NullPool pour éviter les problèmes de fichiers
    if os.environ.get('VERCEL') == '1':
        from sqlalchemy.pool import NullPool
        engine_options['poolclass'] = NullPool
        # Ne pas utiliser le système de fichiers pour les pools
        engine_options.pop('pool_pre_ping', None)  # NullPool n'a pas besoin de pre_ping
        # Garder connect_timeout pour PostgreSQL même avec NullPool
elif 'sqlite' in database_url_lower:
    # Options pour SQLite (pas de connect_timeout)
    print("✓ Configuration SQLite détectée")
    engine_options = {
        'connect_args': {
            'check_same_thread': False  # Permettre l'utilisation dans plusieurs threads
        }
    }
    # SQLite n'a pas besoin de pool_pre_ping ni pool_recycle
else:
    # Options par défaut pour autres bases de données
    print(f"⚠ Configuration de base de données non reconnue : {database_url_lower}")
    engine_options = {
        'pool_pre_ping': True,
        'pool_recycle': 300
    }

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
print(f"✓ Options du moteur SQLAlchemy configurées : {engine_options}")

# SECRET_KEY pour les sessions Flask
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    # Valeur par défaut (non sécurisée pour la production)
    secret_key = 'OPENSECRETKEY'
    print("⚠️  ATTENTION: SECRET_KEY non configuré. Utilisation d'une clé par défaut (non sécurisée)")
    print("⚠️  Pour la production, configurez SECRET_KEY avec une clé aléatoire sécurisée")

app.config['SECRET_KEY'] = secret_key

# Initialiser les extensions
# Gérer les erreurs d'initialisation de SQLAlchemy pour ne pas bloquer l'application
try:
    db.init_app(app)
    print("✓ SQLAlchemy initialisé avec succès")
except Exception as e:
    print(f"⚠ Erreur lors de l'initialisation de SQLAlchemy : {str(e)}")
    print(f"⚠ Les fonctionnalités de base de données peuvent ne pas fonctionner correctement")
    # Ne pas bloquer l'application, mais les routes qui utilisent la DB échoueront
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'

# User loader pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Charger un utilisateur par son ID"""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        # Si la base de données n'est pas disponible, retourner None
        # Cela permet au rendu des templates de continuer même sans DB
        print(f"⚠ Erreur lors du chargement de l'utilisateur {user_id}: {str(e)}")
        return None

# ============================
#   FONCTIONS UTILITAIRES
# ============================

def generate_tracking_number():
    """
    Génère un numéro de colis unique au format XXXXXYY (5 chiffres + 2 lettres majuscules)
    Exemple: 26382TU
    Cette fonction doit être appelée depuis une route Flask pour avoir le contexte d'application.
    """
    max_attempts = 100  # Limite de tentatives pour éviter une boucle infinie
    
    for _ in range(max_attempts):
        # Générer 5 chiffres aléatoires
        digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        
        # Générer 2 lettres majuscules aléatoires
        letters = ''.join([random.choice(string.ascii_uppercase) for _ in range(2)])
        
        # Combiner pour former le numéro de suivi
        tracking_number = f"{digits}{letters}"
        
        # Vérifier l'unicité dans la base de données
        # Le contexte d'application Flask est déjà actif car appelé depuis une route
        existing_order = Order.query.filter_by(tracking_number=tracking_number).first()
        if not existing_order:
            return tracking_number
    
    # Si on n'a pas trouvé de numéro unique après max_attempts tentatives,
    # utiliser un UUID court comme fallback (très rare)
    fallback = f"{random.randint(10000, 99999)}{''.join([random.choice(string.ascii_uppercase) for _ in range(2)])}"
    return fallback

# ============================
#   ROUTES - AUTHENTIFICATION
# ============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion admin"""
    if current_user.is_authenticated:
        return redirect(url_for('orders_list'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Veuillez remplir tous les champs', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Mise à jour de la dernière connexion
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=True)
            flash(f'Bienvenue {email} !', 'success')
            
            # Rediriger vers la page demandée ou vers orders_list
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('orders_list'))
        else:
            flash('Email ou mot de passe incorrect', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html', title="Connexion Admin")


@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté avec succès', 'info')
    return redirect(url_for('home'))

# ============================
#   ROUTES - PAGES PUBLIQUES
# ============================

@app.route('/')
def home():
    """Page d'accueil"""
    try:
        return render_template('index.html', title="Accueil")
    except Exception as e:
        # Si le template ne peut pas être chargé, retourner une réponse JSON avec plus de détails
        import traceback
        error_traceback = traceback.format_exc()
        return jsonify({
            "error": "Erreur lors du chargement de la page d'accueil",
            "message": str(e),
            "traceback": error_traceback if app.debug else None,
            "hint": "Vérifiez que les templates existent dans app/templates/",
            "template_dir": app.template_folder,
            "static_dir": app.static_folder
        }), 500


@app.route('/tracking')
def tracking():
    """Page de suivi de colis"""
    return render_template('tracking.html', title="Suivi de colis")


# ============================
#   ROUTES - GESTION DES COMMANDES
# ============================

@app.route('/add-order', methods=['GET', 'POST'])
@login_required
def add_order():
    """Ajouter une nouvelle commande"""
    if request.method == 'POST':
        # Générer automatiquement un numéro de colis unique
        tracking_number = generate_tracking_number()
        
        # Champs obligatoires
        required_fields = {
            'sender_name': request.form.get('sender_name'),
            'sender_phone': request.form.get('sender_phone'),
            'sender_email': request.form.get('sender_email'),
            'sender_address': request.form.get('sender_address'),
            'receiver_name': request.form.get('receiver_name'),
            'receiver_phone': request.form.get('receiver_phone'),
            'receiver_email': request.form.get('receiver_email'),
            'receiver_address': request.form.get('receiver_address'),
            'shipment_name': request.form.get('shipment_name'),
            'tracking_number': tracking_number,
            'origin_city': request.form.get('origin_city'),
            'origin_country': request.form.get('origin_country'),
            'destination_city': request.form.get('destination_city'),
            'destination_country': request.form.get('destination_country')
        }

        if not all(required_fields.values()):
            flash('Veuillez remplir tous les champs obligatoires ⚠️', 'warning')
            return redirect(url_for('add_order'))

        try:
            # Créer une nouvelle commande
            new_order = Order(
                sender_name=required_fields['sender_name'],
                sender_phone=required_fields['sender_phone'],
                sender_email=required_fields['sender_email'],
                sender_address=required_fields['sender_address'],
                receiver_name=required_fields['receiver_name'],
                receiver_phone=required_fields['receiver_phone'],
                receiver_email=required_fields['receiver_email'],
                receiver_address=required_fields['receiver_address'],
                shipment_name=required_fields['shipment_name'],
                tracking_number=tracking_number,
                origin_city=required_fields['origin_city'],
                origin_country=required_fields['origin_country'],
                destination_city=required_fields['destination_city'],
                destination_country=required_fields['destination_country'],
                pickup_date=request.form.get('pickup_date') or None,
                pickup_time=request.form.get('pickup_time') or None,
                delivery_date=request.form.get('delivery_date') or None,
                delivery_time=request.form.get('delivery_time') or None,
                current_location=request.form.get('current_location') or 'En préparation'
            )
            
            db.session.add(new_order)
            db.session.commit()
            
            flash(f'Commande ajoutée avec succès ✅ - Numéro de colis: {tracking_number}', 'success')
            return redirect(url_for('order_detail', order_id=new_order.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout de la commande : {str(e)} ⚠️', 'danger')
            return redirect(url_for('add_order'))

    return render_template('add_order.html', title="Ajouter une commande")


@app.route('/edit-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Modifier une commande existante"""
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        # Champs obligatoires
        required_fields = {
            'sender_name': request.form.get('sender_name'),
            'sender_phone': request.form.get('sender_phone'),
            'sender_email': request.form.get('sender_email'),
            'sender_address': request.form.get('sender_address'),
            'receiver_name': request.form.get('receiver_name'),
            'receiver_phone': request.form.get('receiver_phone'),
            'receiver_email': request.form.get('receiver_email'),
            'receiver_address': request.form.get('receiver_address'),
            'shipment_name': request.form.get('shipment_name'),
            'tracking_number': request.form.get('tracking_number'),
            'origin_city': request.form.get('origin_city'),
            'origin_country': request.form.get('origin_country'),
            'destination_city': request.form.get('destination_city'),
            'destination_country': request.form.get('destination_country')
        }

        if not all(required_fields.values()):
            flash('Veuillez remplir tous les champs obligatoires ⚠️', 'warning')
            return redirect(url_for('edit_order', order_id=order_id))

        # Vérifier si le numéro de suivi existe déjà pour une autre commande
        tracking_number = request.form.get('tracking_number')
        existing_order = Order.query.filter(
            Order.tracking_number == tracking_number,
            Order.id != order_id
        ).first()
        
        if existing_order:
            flash('Ce numéro de suivi est déjà utilisé par une autre commande ⚠️', 'warning')
            return redirect(url_for('edit_order', order_id=order_id))

        try:
            # Mettre à jour la commande
            order.sender_name = required_fields['sender_name']
            order.sender_phone = required_fields['sender_phone']
            order.sender_email = required_fields['sender_email']
            order.sender_address = required_fields['sender_address']
            order.receiver_name = required_fields['receiver_name']
            order.receiver_phone = required_fields['receiver_phone']
            order.receiver_email = required_fields['receiver_email']
            order.receiver_address = required_fields['receiver_address']
            order.shipment_name = required_fields['shipment_name']
            order.tracking_number = tracking_number
            order.origin_city = required_fields['origin_city']
            order.origin_country = required_fields['origin_country']
            order.destination_city = required_fields['destination_city']
            order.destination_country = required_fields['destination_country']
            order.pickup_date = request.form.get('pickup_date') or None
            order.pickup_time = request.form.get('pickup_time') or None
            order.delivery_date = request.form.get('delivery_date') or None
            order.delivery_time = request.form.get('delivery_time') or None
            order.current_location = request.form.get('current_location') or 'En préparation'
            
            db.session.commit()
            flash('Commande modifiée avec succès ✅', 'success')
            return redirect(url_for('order_detail', order_id=order_id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification : {str(e)} ⚠️', 'danger')
            return redirect(url_for('edit_order', order_id=order_id))

    return render_template('edit_order.html', order=order, order_id=order_id, title="Modifier la commande")


@app.route('/order/<int:order_id>')
def order_detail(order_id):
    """Détail d'une commande par ID"""
    order = Order.query.get_or_404(order_id)
    return render_template('order_detail.html', order=order, title="Détail de la commande")


@app.route('/order/tracking/<tracking_number>')
def order_detail_by_tracking(tracking_number):
    """Détail d'une commande par numéro de suivi"""
    order = Order.query.filter_by(tracking_number=tracking_number).first()
    
    if not order:
        return render_template('order_not_found.html', 
                             tracking_number=tracking_number, 
                             title="Commande introuvable")
    
    return render_template('order_detail.html', order=order, title="Détail de la commande")


@app.route('/orders')
@login_required
def orders_list():
    """Liste de toutes les commandes"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('orders_list.html', orders=orders, title="Liste des commandes")


@app.route('/track-order', methods=['GET'])
def track_order():
    """Rechercher une commande par numéro de suivi"""
    tracking_num = request.args.get('noor')
    
    if not tracking_num:
        flash('Veuillez entrer un numéro de suivi', 'warning')
        return redirect(url_for('tracking'))

    order = Order.query.filter_by(tracking_number=tracking_num).first()
    
    if order:
        return redirect(url_for('order_detail', order_id=order.id))
    
    # Rediriger vers la page d'erreur personnalisée
    return render_template('order_not_found.html', 
                         tracking_number=tracking_num, 
                         title="Commande introuvable")


@app.route('/delete-order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """Supprimer une commande"""
    order = Order.query.get_or_404(order_id)
    
    try:
        db.session.delete(order)
        db.session.commit()
        flash('Commande supprimée avec succès ✅', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)} ⚠️', 'danger')
    
    return redirect(url_for('orders_list'))

# ============================
#   ROUTES - INITIALISATION BASE DE DONNÉES
# ============================

@app.route('/init-db', methods=['GET', 'POST'])
def init_database():
    """Initialiser la base de données (créer les tables)"""
    try:
        with app.app_context():
            # Créer toutes les tables si elles n'existent pas
            db.create_all()
            return jsonify({
                "status": "success",
                "message": "Base de données initialisée avec succès. Les tables ont été créées."
            }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de l'initialisation : {str(e)}"
        }), 500


@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin_route():
    """Créer l'administrateur initial via API"""
    try:
        with app.app_context():
            # S'assurer que les tables existent
            db.create_all()
            
            admin_email = "boristefang3@gmail.com"
            admin_password = "#boris235"
            
            # Vérifier si l'admin existe déjà
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if existing_admin:
                return jsonify({
                    "status": "exists",
                    "message": f"L'administrateur {admin_email} existe déjà."
                }), 200
            
            # Créer le nouvel admin
            admin = User(
                email=admin_email,
                is_admin=True
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": f"Administrateur créé avec succès !",
                "email": admin_email,
                "password": admin_password
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de la création : {str(e)}"
        }), 500


@app.route('/clear-db', methods=['GET', 'POST'])
def clear_database():
    """Vider toutes les données de la base de données"""
    try:
        with app.app_context():
            # Compter les enregistrements avant suppression
            orders_count = Order.query.count()
            users_count = User.query.count()
            
            # Supprimer toutes les commandes
            Order.query.delete()
            
            # Supprimer tous les utilisateurs
            User.query.delete()
            
            # Valider les suppressions
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": "Base de données vidée avec succès",
                "deleted": {
                    "orders": orders_count,
                    "users": users_count
                }
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du vidage de la base de données : {str(e)}"
        }), 500


def initialize_database():
    """Fonction d'initialisation automatique appelée au démarrage"""
    try:
        with app.app_context():
            # Tester la connexion à la base de données
            try:
                db.session.execute(text("SELECT 1"))
                db.session.commit()
            except Exception as db_error:
                print(f"⚠ Erreur de connexion à la base de données : {str(db_error)}")
                raise
            
            # Créer les tables si elles n'existent pas
            db.create_all()
            print("✓ Base de données initialisée - Tables créées/vérifiées")
            
            # Vérifier si l'admin existe, sinon le créer
            admin_email = "boristefang3@gmail.com"
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if not existing_admin:
                admin = User(
                    email=admin_email,
                    is_admin=True
                )
                admin.set_password("#boris235")
                db.session.add(admin)
                db.session.commit()
                print(f"✓ Administrateur créé : {admin_email}")
            else:
                print(f"✓ Administrateur existe déjà : {admin_email}")
                
    except Exception as e:
        print(f"⚠ Erreur lors de l'initialisation automatique : {str(e)}")
        # Ne pas bloquer le démarrage si l'initialisation échoue
        # Sur Vercel, l'initialisation peut échouer si la base de données n'est pas encore disponible
        # L'utilisateur pourra initialiser via /init-db si nécessaire
        raise  # Re-lancer l'erreur pour que l'appelant puisse la gérer

# Initialiser la base de données au démarrage (uniquement en développement local)
# Sur Vercel, l'initialisation se fera à la première requête via /init-db si nécessaire
# Désactiver l'initialisation automatique sur Vercel pour éviter les problèmes de démarrage
if os.environ.get('VERCEL') != '1' and __name__ == '__main__':
    try:
        initialize_database()
    except Exception as e:
        # Ignorer les erreurs d'initialisation au démarrage en développement
        print(f"⚠ Initialisation différée : {str(e)}")
        print("⚠ Vous pouvez initialiser la base de données via /init-db si nécessaire")
        pass

# ============================
#   ROUTES - TESTS
# ============================

@app.route('/test-db')
def test_db():
    """Test simple de connexion à la base de données"""
    try:
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        return jsonify({
            "db_status": "ok",
            "database_url": "configuré" if os.environ.get('DATABASE_URL') else "non configuré",
            "vercel": os.environ.get('VERCEL') == '1'
        }), 200
    except Exception as e:
        return jsonify({
            "db_status": "fail", 
            "error": str(e),
            "database_url": "configuré" if os.environ.get('DATABASE_URL') else "non configuré",
            "hint": "Vérifiez que DATABASE_URL est correctement configuré dans Vercel"
        }), 500

@app.route('/health')
def health_check():
    """Vérification de santé de l'application"""
    try:
        health_status = {
            "status": "ok",
            "app": "Flask",
            "vercel": os.environ.get('VERCEL') == '1',
            "database_url": "configuré" if os.environ.get('DATABASE_URL') else "non configuré",
            "secret_key": "configuré" if os.environ.get('SECRET_KEY') else "non configuré"
        }
        
        # Tester la connexion à la base de données si configurée
        if os.environ.get('DATABASE_URL'):
            try:
                db.session.execute(text("SELECT 1"))
                db.session.commit()
                health_status["database_connection"] = "ok"
            except Exception as db_error:
                health_status["database_connection"] = "fail"
                health_status["database_error"] = str(db_error)
        
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/test-db-full')
def test_db_full():
    """Test complet CRUD de la base de données"""
    response = {
        "connection_status": "unknown",
        "create_status": "skipped",
        "read_status": "skipped",
        "update_status": "skipped",
        "delete_status": "skipped",
        "details": {}
    }
    try:
        # Test de connexion
        db.session.execute(text("SELECT 1"))
        response["connection_status"] = "ok"
    except Exception as e:
        response["connection_status"] = "fail"
        response["details"]["connection_error"] = str(e)
        return jsonify(response), 500

    try:
        # Création
        tracking = f"TEST-{uuid.uuid4().hex[:12]}"
        new_order = Order(
            sender_name="Test Sender",
            sender_phone="+33123456789",
            sender_email="test.sender@example.com",
            sender_address="1 rue de Test, Paris",
            receiver_name="Test Receiver",
            receiver_phone="+33987654321",
            receiver_email="test.receiver@example.com",
            receiver_address="2 avenue de Test, Lyon",
            shipment_name="Colis de test",
            tracking_number=tracking,
            origin_city="Paris",
            origin_country="France",
            destination_city="Lyon",
            destination_country="France",
            current_location="Entrepôt Paris",
            pickup_date=datetime.utcnow().strftime("%Y-%m-%d"),
            pickup_time=datetime.utcnow().strftime("%H:%M")
        )
        db.session.add(new_order)
        db.session.commit()
        response["create_status"] = "ok"
        response["details"]["created_order"] = {"id": new_order.id, "tracking_number": tracking}

        # Lecture
        fetched = Order.query.filter_by(tracking_number=tracking).first()
        if fetched is None:
            raise RuntimeError("created order not found")
        response["read_status"] = "ok"
        response["details"]["fetched_order"] = {"id": fetched.id, "current_location": fetched.current_location}

        # Mise à jour
        fetched.current_location = "Centre logistique Dijon"
        db.session.commit()
        response["update_status"] = "ok"

        # Suppression
        db.session.delete(fetched)
        db.session.commit()
        response["delete_status"] = "ok"

        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        response["details"]["error"] = str(e)
        # Si création a eu lieu mais échec ensuite, tenter un nettoyage best-effort
        try:
            if 'tracking' in locals():
                leftover = Order.query.filter_by(tracking_number=tracking).first()
                if leftover is not None:
                    db.session.delete(leftover)
                    db.session.commit()
        except Exception as _:
            db.session.rollback()
        return jsonify(response), 500

# ============================
#   GESTIONNAIRE D'ERREURS GLOBAL
# ============================

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500 pour afficher des messages plus clairs"""
    db.session.rollback()
    return jsonify({
        "error": "Erreur interne du serveur",
        "message": str(error) if app.debug else "Une erreur s'est produite",
        "hint": "Vérifiez les logs pour plus de détails" if not app.debug else None
    }), 500

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404"""
    return jsonify({
        "error": "Ressource non trouvée",
        "message": "La page demandée n'existe pas"
    }), 404

@app.errorhandler(Exception)
def handle_exception(e):
    """Gestionnaire d'exception global"""
    db.session.rollback()
    # En production, ne pas exposer les détails de l'erreur
    if app.debug:
        return jsonify({
            "error": "Exception non gérée",
            "message": str(e),
            "type": type(e).__name__
        }), 500
    else:
        return jsonify({
            "error": "Une erreur s'est produite",
            "message": "Veuillez contacter l'administrateur"
        }), 500

# ============================
#   POINT D'ENTRÉE POUR VERCEL
# ============================

# L'application Flask est exportée pour Vercel
# Vercel cherche automatiquement la variable 'app' dans ce fichier
# L'application est déjà définie ci-dessus comme variable globale

if __name__ == '__main__':
    app.run(debug=True)
