from app.models.car import CarListing
from sqlalchemy.sql import func
from scipy import stats
import numpy as np

# Fetch data in batches to prevent memory overload with large datasets
def fetch_car_data_in_batches(year, make, model, batch_size=1000):
    offset = 0
    make = make.lower()  # Lower the input make
    model = model.lower()  # Lower the input model
    found_data = False  # Flag to track if any data is found

    while True:
        # Fetch a batch of data, exclude rows with null prices and mileages
        batch = CarListing.query.with_entities(
            CarListing.listing_price, 
            CarListing.listing_mileage
        ).filter(
            CarListing.year == year, 
            func.lower(CarListing.make) == make,  # Lower the DB make for comparison
            func.lower(CarListing.model) == model,  # Lower the DB model for comparison
            CarListing.listing_price.isnot(None),   # Exclude null prices
            CarListing.listing_mileage.isnot(None)  # Exclude null mileages
        ).offset(offset).limit(batch_size).all()

        if not batch:
            break  # No more data to fetch

        found_data = True
        yield batch
        offset += batch_size

    # If no data is found, raise an exception or return None
    if not found_data:
        return None  # No data found

# Calculate dynamic depreciation rate using linear regression based on mileage and price
def calculate_depreciation_rate_from_batches(year, make, model):
    prices = []
    mileages = []

    # Fetch the car data in batches
    batch_generator = fetch_car_data_in_batches(year, make, model)

    if batch_generator is None:
        return None, None  # No data found

    for batch in batch_generator:
        for price, mileage in batch:
            prices.append(price)
            mileages.append(mileage)

    # Ensure there are enough data points to perform regression
    if len(prices) < 2:
        return None, None  # Not enough data to calculate depreciation

    # Perform linear regression on price vs mileage
    prices = np.array(prices)
    mileages = np.array(mileages)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(mileages, prices)

    depreciation_rate = abs(slope)  # Take the absolute value of the slope (depreciation rate)
    return depreciation_rate, intercept  # Return both depreciation rate and starting price (intercept)

# Fetch the minimum price for the given year, make, and model from the database
def fetch_min_price(year, make, model):
    make = make.lower()  # Lower the input make
    model = model.lower()  # Lower the input model
    min_price = CarListing.query.with_entities(
        func.min(CarListing.listing_price)
    ).filter(
        CarListing.year == year, 
        func.lower(CarListing.make) == make,  # Lower the DB make for comparison
        func.lower(CarListing.model) == model,  # Lower the DB model for comparison
        CarListing.listing_price.isnot(None)  # Ensure we exclude null prices
    ).scalar()

    # Return None if no price is found (instead of defaulting to 500)
    return min_price

# Fetch up to 100 sample listings, excluding null prices and mileages
def fetch_sample_listings(year, make, model, limit=100):
    make = make.lower()  # Lower the input make
    model = model.lower()  # Lower the input model
    listings = CarListing.query.filter(
        CarListing.year == year, 
        func.lower(CarListing.make) == make,  # Lower the DB make for comparison
        func.lower(CarListing.model) == model,  # Lower the DB model for comparison
        CarListing.listing_price.isnot(None),   # Exclude listings with null prices
        CarListing.listing_mileage.isnot(None)  # Exclude listings with null mileages
    ).order_by(CarListing.listing_price).limit(limit).all()

    if not listings:
        return None  # Return None if no listings are found

    # Format the listings to include relevant fields
    formatted_listings = [{
        'name': f"{listing.year} {listing.make} {listing.model} {listing.trim}",
        'vin': listing.vin,
        'price': listing.listing_price,
        'mileage': listing.listing_mileage,
        'location': f"{listing.dealer_city}, {listing.dealer_state}"
    } for listing in listings]

    return formatted_listings

# Get the adjusted price and sample listings based on the calculated depreciation rate and user mileage
def get_adjusted_price_and_listings(year, make, model, user_mileage=None):
    make = make.lower()  # Lower the input make
    model = model.lower()  # Lower the input model

    # Step 1: Calculate the depreciation rate and intercept (starting price)
    depreciation_rate, starting_price = calculate_depreciation_rate_from_batches(year, make, model)

    # If no data is found, return "Data not found"
    if depreciation_rate is None:
        return None, None

    # Step 2: Fetch the minimum price from the database for this car (return None if not found)
    min_price = fetch_min_price(year, make, model)

    # If no data is found in the database, return "Data not found"
    if min_price is None:
        return None, None

    # If we don't have enough data or the depreciation rate is 0, return the starting price
    if depreciation_rate == 0:
        adjusted_price = starting_price
    else:
        # If mileage is provided, adjust the price based on the user's mileage
        if user_mileage:
            adjusted_price = starting_price - (user_mileage * depreciation_rate)
        else:
            # If no mileage is provided, return the starting price
            adjusted_price = starting_price

    # Step 3: Ensure that the adjusted price doesn't fall below the minimum price from the DB
    if adjusted_price < min_price:
        adjusted_price = min_price

    # Step 4: Round the adjusted price to the nearest hundred
    adjusted_price = round(adjusted_price / 100) * 100

    # Step 5: Fetch up to 100 sample listings used for the market value estimate, excluding null prices and mileages
    sample_listings = fetch_sample_listings(year, make, model)

    if sample_listings is None:
        return adjusted_price, "Data not found"

    return adjusted_price, sample_listings
