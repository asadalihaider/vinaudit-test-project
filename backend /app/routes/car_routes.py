from flask import Blueprint, request, jsonify
from app.services.car_service import get_adjusted_price_and_listings

car_bp = Blueprint("car", __name__)


@car_bp.route("/api/market_value", methods=["GET"])
def market_value():
    year = request.args.get("year", type=int)
    make = request.args.get("make")
    model = request.args.get("model")
    mileage = request.args.get("mileage", type=float)

    if not year or not make or not model:
        return jsonify({"error": "Year, make, and model are required fields."}), 400
    
    if not isinstance(year, int):
        return jsonify({"error": "Year must be an integer."}), 400

    if not isinstance(make, str) or not isinstance(model, str):
        return jsonify({"error": "Make and model must be strings."}), 400
    
    if mileage and not isinstance(mileage, float):
        return jsonify({"error": "Mileage must be a number"}), 400

    market_price, listings = get_adjusted_price_and_listings(year, make, model, mileage)

    if market_price is None:
        return jsonify({"error": "No data found for the given criteria."}), 404

    return jsonify({"market_price": market_price, "listings": listings})
