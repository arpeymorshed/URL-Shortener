from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize db without binding to an app yet
db = SQLAlchemy()

class URL(db.Model):
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    click_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<URL {self.short_code}>'