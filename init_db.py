"""
Script pour initialiser la base de données avec des données de test
"""
from app import app, db, Order

def init_database():
    """Initialise la base de données et ajoute des données de test"""
    
    with app.app_context():
        # Supprimer toutes les tables existantes
        print("Suppression des tables existantes...")
        db.drop_all()
        
        # Créer toutes les tables
        print("Creation des tables...")
        db.create_all()
        
        # Ajouter des commandes de test
        print("Ajout des commandes de test...")
        
        orders = [
            Order(
                sender_name="Alice Dupont",
                sender_phone="0612345678",
                sender_email="alice@example.com",
                sender_address="12 Rue de la Paix, 75001 Paris",
                receiver_name="Bob Martin",
                receiver_phone="0698765432",
                receiver_email="bob@example.com",
                receiver_address="45 Avenue des Champs, 75008 Paris",
                shipment_name="Ordinateur Portable",
                tracking_number="ORD123456",
                origin_city="Paris",
                origin_country="France",
                destination_city="Lyon",
                destination_country="France",
                pickup_date="2025-09-12",
                pickup_time="10:30",
                delivery_date="2025-09-15",
                delivery_time="14:00",
                current_location="En transit - Lyon"
            ),
            Order(
                sender_name="Charlie Bernard",
                sender_phone="0623456789",
                sender_email="charlie@example.com",
                sender_address="34 Boulevard Saint-Germain, 75005 Paris",
                receiver_name="David Petit",
                receiver_phone="0678901234",
                receiver_email="david@example.com",
                receiver_address="78 Rue de la République, 69002 Lyon",
                shipment_name="Smartphone",
                tracking_number="ORD654321",
                origin_city="Paris",
                origin_country="France",
                destination_city="Lyon",
                destination_country="France",
                pickup_date="2025-10-01",
                pickup_time="09:00",
                delivery_date="2025-10-03",
                delivery_time="16:30",
                current_location="Livré"
            ),
            Order(
                sender_name="Mrs Alice Cooper",
                sender_phone="+1 (414) 727-828",
                sender_email="johndoe@example.com",
                sender_address="2201 MENAUL BLVD NE STE A",
                receiver_name="Ethan Harper",
                receiver_phone="+1 (231) 672-6729",
                receiver_email="ethanharper20241@gmail.com",
                receiver_address="2201 MENAUL BLVD NE STE A",
                shipment_name="Electronic bike",
                tracking_number="MRK45892IUS",
                origin_city="New York",
                origin_country="USA",
                destination_city="Los Angeles",
                destination_country="USA",
                pickup_date="2025-09-12",
                pickup_time="10:30",
                delivery_date="2025-09-15",
                delivery_time="14:00",
                current_location="En transit - Chicago"
            )
        ]
        
        for order in orders:
            db.session.add(order)
        
        try:
            db.session.commit()
            print(f"OK - {len(orders)} commandes ajoutees avec succes!")
            print("\nListe des numeros de suivi:")
            for order in orders:
                print(f"   - {order.tracking_number} : {order.shipment_name}")
            print("\nBase de donnees initialisee avec succes!")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERREUR lors de l'ajout des donnees : {str(e)}")

if __name__ == "__main__":
    init_database()

