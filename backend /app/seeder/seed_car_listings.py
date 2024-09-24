import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details from .env file
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

# Function to connect to the database
def connect_db():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to create the table if it doesn't exist
def create_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS car_listings (
                vin VARCHAR(20) PRIMARY KEY,
                year INT,
                make VARCHAR(255),
                model VARCHAR(255),
                trim VARCHAR(255),
                dealer_name VARCHAR(255),
                dealer_street VARCHAR(255),
                dealer_city VARCHAR(255),
                dealer_state VARCHAR(255),
                dealer_zip VARCHAR(10),
                listing_price FLOAT,
                listing_mileage FLOAT,
                used BOOLEAN,
                certified BOOLEAN,
                style VARCHAR(255),
                driven_wheels VARCHAR(255),
                engine VARCHAR(255),
                fuel_type VARCHAR(255),
                exterior_color VARCHAR(255),
                interior_color VARCHAR(255),
                seller_website VARCHAR(255),
                first_seen_date DATE,
                last_seen_date DATE,
                dealer_vdp_last_seen_date DATE,
                listing_status VARCHAR(20)
            );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        print("Table 'car_listings' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

# Function to insert data from the text file
def insert_data_from_file(connection, file_path):
    try:
        cursor = connection.cursor()
        batch_size = 100000  # Commit after every 100,000 records
        counter = 0

        # Open the file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            # Skip the first line (header)
            next(file)
            for line in file:
                # Split data using the pipe delimiter '|'
                data = line.strip().split('|')
                
                if len(data) == 25:  # Ensure that the data has 25 columns
                    vin, year, make, model, trim, dealer_name, dealer_street, dealer_city, dealer_state, dealer_zip, \
                    listing_price, listing_mileage, used, certified, style, driven_wheels, engine, fuel_type, \
                    exterior_color, interior_color, seller_website, first_seen_date, last_seen_date, \
                    dealer_vdp_last_seen_date, listing_status = data

                    # Handle empty string fields by converting them to None
                    listing_price = float(listing_price) if listing_price else None
                    listing_mileage = float(listing_mileage) if listing_mileage else None
                    used = True if used == 'TRUE' else False
                    certified = True if certified == 'TRUE' else False
                    first_seen_date = first_seen_date if first_seen_date else None
                    last_seen_date = last_seen_date if last_seen_date else None
                    dealer_vdp_last_seen_date = dealer_vdp_last_seen_date if dealer_vdp_last_seen_date else None
                    style = style if style else None
                    listing_status = listing_status if listing_status else None

                    insert_query = '''
                        INSERT INTO car_listings (vin, year, make, model, trim, dealer_name, dealer_street, dealer_city, dealer_state, dealer_zip,
                                                  listing_price, listing_mileage, used, certified, style, driven_wheels, engine, fuel_type,
                                                  exterior_color, interior_color, seller_website, first_seen_date, last_seen_date,
                                                  dealer_vdp_last_seen_date, listing_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (vin) DO NOTHING
                    '''

                    cursor.execute(insert_query, (
                        vin, year, make, model, trim, dealer_name, dealer_street, dealer_city, dealer_state, dealer_zip,
                        listing_price, listing_mileage, used, certified, style, driven_wheels, engine, fuel_type,
                        exterior_color, interior_color, seller_website, first_seen_date, last_seen_date, dealer_vdp_last_seen_date, listing_status
                    ))

                    counter += 1

                    # Commit after every 100,000 entries
                    if counter % batch_size == 0:
                        connection.commit()
                        print(f"{counter} records inserted and committed.")

            # Final commit for remaining entries
            if counter % batch_size != 0:
                connection.commit()
                print(f"Final commit: {counter} records inserted.")

        cursor.close()
        print(f"Data from '{file_path}' inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")

if __name__ == "__main__":
    # Path to the text file
    file_path = 'NEWTEST-inventory-listing-2022-08-17.txt'

    # Connect to the database
    connection = connect_db()

    if connection:
        # Create the table
        create_table(connection)
        
        # Insert data from the text file
        insert_data_from_file(connection, file_path)

        # Close the connection
        connection.close()
    else:
        print("Failed to connect to the database.")
