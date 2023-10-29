from database import SessionLocal
from models import User
from services import hash

def initialize_admin():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.name == 'admin').first()
    
    if not admin_user:
        admin = User(name='admin', password=hash('123'), isAdmin=True, balance=1000000000)
        db.add(admin)
        db.commit()