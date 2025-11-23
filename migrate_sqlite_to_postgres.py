import sqlite3
from app import app, db, User, Order
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from datetime import datetime

SQLITE_FILE = 'orders.db'

def migrate():
    with app.app_context():
        conn = sqlite3.connect(SQLITE_FILE)
        c = conn.cursor()
        # ----- USERS -----
        print('\n--- Migration des admins/Users ---')
        try:
            users = c.execute('SELECT id, email, password_hash, is_admin, created_at, last_login FROM users').fetchall()
        except Exception as e:
            print('Table users non trouvée ou vide:', e)
            users = []
        imported_users = 0
        for (id, email, password_hash, is_admin, created_at, last_login) in users:
            if User.query.filter_by(email=email).first():
                print(f'- [User] {email} existe déjà, skip.')
                continue
            user = User(
                email=email,
                password_hash=password_hash or generate_password_hash('changeme123'),
                is_admin=bool(is_admin),
                created_at=datetime.fromisoformat(created_at) if created_at else None,
                last_login=datetime.fromisoformat(last_login) if last_login else None
            )
            db.session.add(user)
            imported_users += 1
        # ----- ORDERS -----
        print('\n--- Migration des commandes (Order) ---')
        try:
            orders = c.execute('SELECT * FROM orders').fetchall()
            cols = [desc[0] for desc in c.description]
        except Exception as e:
            print('Table orders non trouvée ou vide:', e)
            orders = []
        imported_orders = 0
        for row in orders:
            order_data = dict(zip(cols, row))
            if Order.query.filter_by(tracking_number=order_data['tracking_number']).first():
                print(f'- [Order] {order_data["tracking_number"]} déjà existante, skip.')
                continue
            order = Order(**order_data)
            db.session.add(order)
            imported_orders += 1
        try:
            db.session.commit()
            print(f"Migration terminée : {imported_users} user(s), {imported_orders} commande(s).")
        except IntegrityError as e:
            db.session.rollback()
            print('Erreur d\'unicité, rollback!', e)
        except Exception as e:
            db.session.rollback()
            print('Erreur inconnue lors de la migration!', e)
        conn.close()
        print('Fin, vous pouvez tester l\'application sur PostgreSQL !')

if __name__ == '__main__':
    migrate()
