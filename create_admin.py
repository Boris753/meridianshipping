"""
Script pour créer l'utilisateur administrateur
"""
from app import app, db, User

def create_admin():
    """Crée l'utilisateur admin principal"""
    with app.app_context():
        # Vérifier si l'admin existe déjà
        admin_email = "boristefang3@gmail.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"L'administrateur {admin_email} existe deja.")
            print("Souhaitez-vous reinitialiser le mot de passe? (o/n)")
            response = input().strip().lower()
            
            if response == 'o':
                existing_admin.set_password("#boris235")
                db.session.commit()
                print(f"Mot de passe reinitialise pour {admin_email} !")
            else:
                print("Operation annulee.")
            return
        # Créer le nouvel admin
        print("Creation de l'administrateur...")
        admin = User(
            email=admin_email,
            is_admin=True
        )
        admin.set_password("#boris235")
        try:
            db.session.add(admin)
            db.session.commit()
            print("\n" + "="*50)
            print("ADMINISTRATEUR CREE AVEC SUCCES!")
            print("="*50)
            print(f"Email     : {admin_email}")
            print(f"Password  : #boris235")
            print("="*50)
            print("\nVous pouvez maintenant vous connecter sur /login")
        except Exception as e:
            db.session.rollback()
            print(f"ERREUR lors de la creation : {str(e)}")

if __name__ == "__main__":
    create_admin()

