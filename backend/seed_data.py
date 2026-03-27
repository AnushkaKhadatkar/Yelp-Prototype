import random
import mysql.connector
from faker import Faker

fake = Faker()

# --- DB CONNECTION ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Password123!",
    database="yelp_db"
)
cursor = conn.cursor()

# --- DATA ---
cuisines = ["Italian", "Chinese", "Mexican", "Indian", "Japanese", "American"]
cities = ["San Jose", "San Francisco", "New York", "Los Angeles", "Chicago"]
states = ["CA", "NY", "IL", "TX"]

price_tiers = ["$", "$$", "$$$", "$$$$"]
ambiance_list = ["casual", "fine dining", "romantic", "family-friendly"]
amenities_list = ["wifi", "outdoor seating", "parking", "pet-friendly"]

review_phrases = [
    "Amazing food!", "Would definitely come back.",
    "Service was slow but food was great.",
    "Highly recommend!", "Not worth the price.",
    "Loved the ambiance.", "Great for family dinners.",
    "Best place in town!", "Decent experience.",
    "Could be better."
]

# --- USERS ---
user_ids = []
for _ in range(15):
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, city, state, country)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        fake.name(),
        fake.unique.email(),
        "fake_hashed_password",
        random.choice(cities),
        random.choice(states),
        "USA"
    ))
    user_ids.append(cursor.lastrowid)

# --- RESTAURANTS ---
restaurant_ids = []

for _ in range(60):
    city = random.choice(cities)
    state = random.choice(states)

    cursor.execute("""
        INSERT INTO restaurants 
        (name, cuisine, address, city, state, zip_code, description,
         contact_phone, contact_email, price_tier, ambiance, amenities, hours)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        fake.company(),
        random.choice(cuisines),
        fake.address(),
        city,
        state,
        fake.zipcode(),
        fake.text(max_nb_chars=120),
        fake.phone_number(),
        fake.email(),
        random.choice(price_tiers),
        random.choice(ambiance_list),
        random.choice(amenities_list),
        "9 AM - 10 PM"
    ))

    restaurant_ids.append(cursor.lastrowid)

# --- REVIEWS ---
for r_id in restaurant_ids:
    ratings = []

    # pick unique users for this restaurant
    num_reviews = random.randint(3, 8)
    selected_users = random.sample(user_ids, min(num_reviews, len(user_ids)))

    for user_id in selected_users:
        rating = random.randint(1, 5)
        ratings.append(rating)

        cursor.execute("""
            INSERT INTO reviews (user_id, restaurant_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            r_id,
            rating,
            random.choice(review_phrases)
        ))

    # --- UPDATE avg_rating + review_count ---
    avg_rating = round(sum(ratings) / len(ratings), 1)

    cursor.execute("""
        UPDATE restaurants
        SET avg_rating = %s,
            review_count = %s
        WHERE id = %s
    """, (avg_rating, len(ratings), r_id))

# --- COMMIT ---
conn.commit()
cursor.close()
conn.close()

print("Seed data inserted successfully!")