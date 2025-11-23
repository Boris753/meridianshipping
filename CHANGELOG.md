# 📝 Journal des modifications

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [v2.2.0] - 2025-10-26

### 🔐 Ajout : Système d'authentification sécurisé


#### Nouvelles fonctionnalités

- **Flask-Login** intégré pour la gestion des sessions
- **Protection des routes** : `/orders`, `/add-order`, `/edit-order/<id>`, `/delete-order/<id>`
- **Page de login moderne** avec design gradient
- **Menu dynamique** selon l'état d'authentification
- **Gestion de la session** : Remember me, redirection après login

#### Modèle User

- Email unique
- Mot de passe haché (Werkzeug Security)
- Rôle admin
- Date de création et dernière connexion

#### Sécurité

- Mots de passe hachés avec `generate_password_hash()`
- Protection CSRF native de Flask
- Sessions sécurisées
- Redirection automatique si non authentifié

#### Scripts

- **create_admin.py** : Création du compte administrateur
  - Email : dissangfrancis@yahoo.com
  - Password : #colis235#

#### Documentation

- AUTHENTIFICATION.md : Guide complet
- TEST_AUTH_RAPIDE.md : Tests rapides
- SECURITE_COMPLETE.md : Détails de sécurité

#### Fichiers modifiés

- `app/models.py` : Ajout du modèle User
- `app/__init__.py` : Configuration Flask-Login
- `app/routes.py` : Protection des routes
- `app/templates/login.html` : Nouvelle page
- `app/templates/base.html` : Menu dynamique
- `requirements.txt` : Ajout Flask-Login

---

## [v2.1.0] - 2025-10-26

### 🚨 Ajout : Gestion professionnelle des erreurs

#### Nouvelles fonctionnalités

- **Modals Bootstrap** pour tous les messages flash
  - Success (vert)
  - Danger (rouge)
  - Warning (jaune)
  - Info (bleu)
- **Page d'erreur personnalisée** pour commandes introuvables
- **Auto-fermeture** des messages de succès après 5 secondes

#### Page order_not_found.html

- Design moderne et responsive
- Animation de l'icône 404
- Suggestions d'actions
- Boutons d'action (Rechercher, Accueil)
- Style cohérent avec l'application

#### UX améliorée

- Messages flash plus visibles
- Feedback immédiat pour l'utilisateur
- Redirection intelligente après erreur
- Design professionnel et rassurant

#### Fichiers modifiés

- `app/routes.py` : Gestion des erreurs
- `app/templates/base.html` : Modals pour flash messages
- `app/templates/order_not_found.html` : Nouvelle page d'erreur

#### Documentation

- SYSTEME_ERREURS.md : Explication complète
- TEST_ERREURS_RAPIDE.md : Guide de test

---

## [v2.0.0] - 2025-10-26

### 🗺️ Ajout majeur : Carte interactive du monde

#### Nouvelles fonctionnalités

- **Leaflet.js** intégré pour la visualisation
- **Carte interactive** sur la page de détail
- **3 marqueurs** :
  - 🟢 Point de départ (vert)
  - 🔵 Position actuelle (bleu, icône cargo)
  - 🔴 Destination (rouge)
- **Tracé du parcours** :
  - Ligne complète (grise)
  - Ligne parcourue (bleue)

#### Villes supportées

40+ villes principales pré-configurées avec coordonnées GPS

#### Design

- Carte en bas de page
- Hauteur 500px
- Bordures arrondies
- Responsive
- Auto-zoom sur les points

#### Fichiers modifiés

- `app/templates/order_detail.html` : Ajout de la carte
- `app/models.py` : Champ `current_location`

#### Documentation

- CARTE_SUIVI.md : Guide complet
- GUIDE_RAPIDE_CARTE.md : Démarrage rapide

---

## [v1.0.0] - 2025-10-26

### 🚀 Version initiale

#### Fonctionnalités

- **CRUD complet** pour les commandes
- **Base de données SQLite** avec SQLAlchemy
- **Suivi par numéro** de tracking
- **Interface moderne** avec Bootstrap
- **Code-barres SVG** sur les détails
- **Design responsive**

#### Modèles

- **Order Model** :
  - Informations expéditeur
  - Informations destinataire
  - Détails de livraison
  - Dates de pickup et delivery

#### Routes

- `/` : Page d'accueil
- `/tracking` : Recherche de colis
- `/orders` : Liste des commandes
- `/add-order` : Ajouter une commande
- `/edit-order/<id>` : Modifier une commande
- `/order/<id>` : Détails par ID
- `/order/tracking/<numero>` : Détails par numéro

#### Scripts

- **init_db.py** : Initialisation avec données de test
- **run.py** : Lancement du serveur

#### Documentation

- README.md : Guide d'utilisation
- GUIDE_TEST.md : Tests

---

## Légende

- 🚀 Version majeure
- 🔑 Authentification / Sécurité
- 🗺️ Carte / Visualisation
- 🚨 Gestion des erreurs
- ⚙️ Configuration
- 📝 Documentation
- 🐛 Correction de bug
- ✨ Amélioration
