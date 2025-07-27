from firebase_admin import firestore, initialize_app, credentials

# Application Default credentials are automatically created.
creds = credentials.Certificate('firebase_service_account.json')
app = initialize_app(creds)
client = firestore.client()