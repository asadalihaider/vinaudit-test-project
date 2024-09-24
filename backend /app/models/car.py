from app import db


class CarListing(db.Model):
    __tablename__ = "car_listings"

    vin = db.Column(db.String(20), primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    trim = db.Column(db.String(255))
    dealer_name = db.Column(db.String(255))
    dealer_street = db.Column(db.String(255))
    dealer_city = db.Column(db.String(255))
    dealer_state = db.Column(db.String(255))
    dealer_zip = db.Column(db.String(10))
    listing_price = db.Column(db.Float)
    listing_mileage = db.Column(db.Float)
    used = db.Column(db.Boolean, default=True)
    certified = db.Column(db.Boolean, default=False)
    style = db.Column(db.String(255))
    driven_wheels = db.Column(db.String(255))
    engine = db.Column(db.String(255))
    fuel_type = db.Column(db.String(255))
    exterior_color = db.Column(db.String(255))
    interior_color = db.Column(db.String(255))
    seller_website = db.Column(db.String(255))
    first_seen_date = db.Column(db.Date)
    last_seen_date = db.Column(db.Date)
    dealer_vdp_last_seen_date = db.Column(db.Date)
    listing_status = db.Column(db.String(20))
