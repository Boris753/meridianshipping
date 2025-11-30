# Meridian Shipping - Application Flask

Application Flask pour la gestion des commandes de livraison, déployée sur Vercel avec base de données Neon PostgreSQL.

---

## 📦 Architecture

- **Backend** : Flask 3.x + SQLAlchemy 2.x
- **Base de données** : Neon PostgreSQL (hébergé sur Vercel)
- **Déploiement** : Vercel (serverless)
- **Développement local** : SQLite (fallback si DATABASE_URL non configuré)

---

## 🚀 Configuration Neon + Vercel

### Étape 1 : Créer une base Neon

1. Accédez à [Neon Console](https://console.neon.tech)
2. Créez un nouveau projet ou utilisez un existant
3. Allez dans **Project** → **Connection** → copiez l'URL PostgreSQL
   - Format : `postgresql://user:password@host-pooler.region.neon.tech/dbname?sslmode=require`

### Étape 2 : Configurer sur Vercel

1. Allez sur le dashboard Vercel du projet
2. Allez dans **Settings** → **Environment Variables**
3. Ajoutez une nouvelle variable :
   - **Clé** : `DATABASE_URL`
   - **Valeur** : collez l'URL de Neon
4. Sauvegardez et redéployez

### Étape 3 : Développement local

1. **Copier `.env.example` en `.env`** :
   ```bash
   copy .env.example .env
   ```

2. **Éditer `.env`** et remplacer par votre URL Neon :
   ```env
   DATABASE_URL=postgresql://user:password@host-pooler.region.neon.tech/dbname?sslmode=require
   SECRET_KEY=your-random-secret-key
   ```

3. **Créer l'environnement virtuel** :
   ```powershell
   python -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   ```

4. **Installer les dépendances** :
   ```powershell
   pip install -r requirements.txt
   ```

5. **Démarrer l'app en dev** :
   ```powershell
   python app.py
   ```
   - L'app utilisera Neon PostgreSQL si `DATABASE_URL` est défini
   - Sinon, elle tombera sur SQLite local (`instance/dev.db`)

---

## 🔧 Configuration de la base de données

### Neon PostgreSQL (Production)

L'app lit automatiquement `DATABASE_URL` depuis les variables d'environnement (Vercel ou `.env` en local).

**Points clés** :
- SSL est **obligatoire** (ajouté automatiquement si absent)
- Pool de connexions géré par Neon
- Sur Vercel → `NullPool` utilisé (serverless, pas de persistence)
- Sur local → pool normal avec `pool_recycle=300`

### SQLite (Développement local)

Si `DATABASE_URL` **n'est pas défini**, l'app bascule sur :
```
sqlite:///./instance/dev.db
```

⚠️ **Note** : SQLite ne persiste **pas** sur Vercel (système de fichiers éphémère). Utilisez toujours Neon en production.

---

## 📝 Routes principales

### Public
- `GET /` → Page d'accueil
- `GET /tracking` → Page de suivi de colis
- `GET /track-order?noor=XXXXX` → Rechercher une commande

### Admin (authentifiée)
- `POST /login` → Connexion
- `GET /logout` → Déconnexion
- `GET /orders` → Liste des commandes
- `GET /add-order`, `POST /add-order` → Ajouter une commande
- `GET /edit-order/<id>`, `POST /edit-order/<id>` → Modifier
- `POST /delete-order/<id>` → Supprimer

### Utilitaires
- `GET /health` → Vérification de santé (status, DB, env)
- `GET /test-db` → Test connexion DB
- `GET /test-db-full` → Test complet CRUD
- `POST /init-db` → Initialiser tables (premier déploiement)
- `POST /create-admin` → Créer l'admin initial

---

## 🛠️ Dépannage

### Erreur : `FUNCTION_INVOCATION_FAILED` sur Vercel

✅ **Solution** : Assurez-vous que `DATABASE_URL` est configuré dans les variables d'environnement Vercel.

```bash
vercel env list  # Vérifier les variables
vercel logs      # Voir les logs en direct
```

### Erreur : `SSL connection has been closed unexpectedly`

✅ **Solution** : L'URL DATABASE_URL doit contenir `?sslmode=require`. Vérifiez :
- URL Neon copiée correctement
- `sslmode=require` présent dans l'URL
- Vercel re-déployé après changement

### App démarre mais pas de données

1. Allez sur `https://yourapp.vercel.app/init-db` pour initialiser les tables
2. Allez sur `https://yourapp.vercel.app/create-admin` pour créer l'admin
3. Connectez-vous avec les credentials fournis

---

## 📊 Structure BD

**Tables** :
- `users` → Admin users (email, password_hash, is_admin, created_at, last_login)
- `orders` → Commandes (sender/receiver info, tracking, dates, location, timestamps)

**Indexes** :
- `users.email` (unique)
- `orders.tracking_number` (unique)

---

## 🔐 Sécurité

**À faire en production** :
- ✅ `SECRET_KEY` → Générer une clé aléatoire sécurisée
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- ✅ Protéger routes `/init-db`, `/create-admin`, `/clear-db` (ou les supprimer après setup)
- ✅ HTTPS obligatoire (Vercel le force)
- ✅ SSL Neon (`sslmode=require`)

---

## 📦 Déploiement rapide

```bash
# Initialiser Vercel (si pas déjà fait)
vercel

# Déployer
vercel --prod

# Vérifier les logs
vercel logs
```

---

## 🛑 Arrêt de Render → Neon

Si vous migrez de Render PostgreSQL vers Neon :

1. **Exporter les données de Render** (si nécessaire)
2. **Créer une nouvelle base sur Neon**
3. **Mettre à jour `DATABASE_URL` sur Vercel** avec URL Neon
4. **Exécuter `/init-db`** pour créer les schémas
5. **Réimporter les données** (si applicable) ou redémarrer

L'application est maintenant prête à utiliser **Neon PostgreSQL** ! 🎉

---

## 📞 Support

- Neon Console : https://console.neon.tech
- Vercel Dashboard : https://vercel.com/dashboard
- Logs Vercel : `vercel logs` (local) ou Dashboard → Deployments
