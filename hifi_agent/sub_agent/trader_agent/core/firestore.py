# Application Default credentials are automatically created.
_db = None

def get_firestore_client():
    from firebase_admin import firestore, initialize_app, credentials, get_app

    global _db
    if _db is None:
        try:
            get_app()
        except ValueError:
            creds = credentials.Certificate('firebase_service_account.json')
            initialize_app(creds)
        _db = firestore.client()
    return _db

# For backward compatibility, though usage should be updated to call the function
# client = firestore.client()