from firebase_admin import firestore, initialize_app

# Application Default credentials are automatically created.
app = initialize_app()
client = firestore.client()