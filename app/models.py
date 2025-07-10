from . import db
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))         # <-- Required
    description = db.Column(db.String(255))  # <-- Required
    price = db.Column(db.Float)              # <-- Required
    image = db.Column(db.String(100))        # <-- Already works
    category = db.Column(db.String(50))      # Optional
