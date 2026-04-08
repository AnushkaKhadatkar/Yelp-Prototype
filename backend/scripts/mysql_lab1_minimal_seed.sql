-- Minimal Lab 1–style schema + sample rows for migrate_mysql_to_mongo.py.
-- Run against your MySQL (Docker example):
--   docker exec -i <mysql_container_name> mysql -uyelp -pyelppass yelp_db < scripts/mysql_lab1_minimal_seed.sql
-- Or: mysql -h 127.0.0.1 -P 3307 -uyelp -pyelppass yelp_db < scripts/mysql_lab1_minimal_seed.sql

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  phone VARCHAR(20) NULL,
  about TEXT NULL,
  city VARCHAR(100) NULL,
  state VARCHAR(10) NULL,
  country VARCHAR(100) NULL,
  languages VARCHAR(255) NULL,
  gender VARCHAR(20) NULL,
  profile_pic VARCHAR(255) NULL,
  restaurant_location VARCHAR(255) NULL,
  role ENUM('user','owner') NOT NULL DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS restaurants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  cuisine VARCHAR(100) NOT NULL,
  address VARCHAR(255) NULL,
  city VARCHAR(100) NULL,
  state VARCHAR(10) NULL,
  zip_code VARCHAR(20) NULL,
  description TEXT NULL,
  contact_phone VARCHAR(20) NULL,
  contact_email VARCHAR(150) NULL,
  price_tier ENUM('$','$$','$$$','$$$$') NULL,
  ambiance VARCHAR(255) NULL,
  amenities VARCHAR(255) NULL,
  hours TEXT NULL,
  photos TEXT NULL,
  owner_id INT NULL,
  avg_rating DECIMAL(2,1) DEFAULT 0.0,
  review_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  restaurant_id INT NOT NULL,
  rating INT NOT NULL,
  comment TEXT NULL,
  photos TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS favourites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  restaurant_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_restaurant (user_id, restaurant_id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  cuisines VARCHAR(255) NULL,
  price_range ENUM('$','$$','$$$','$$$$') NULL,
  preferred_locations VARCHAR(255) NULL,
  dietary_needs VARCHAR(255) NULL,
  ambiance VARCHAR(255) NULL,
  sort_preference VARCHAR(50) NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

SET FOREIGN_KEY_CHECKS = 1;

-- bcrypt hash for plain password: password123
INSERT IGNORE INTO users (id, name, email, password_hash, role, city, state)
VALUES
  (1, 'Demo User', 'demo@example.com', '$2b$12$HFswGaXwLn6Y/CsOLxJv3eO/A3ALR0LDclpAgZf0D14fZ57nPZzhC', 'user', 'San Jose', 'CA'),
  (2, 'Demo Owner', 'owner@example.com', '$2b$12$HFswGaXwLn6Y/CsOLxJv3eO/A3ALR0LDclpAgZf0D14fZ57nPZzhC', 'owner', 'San Jose', 'CA');

INSERT IGNORE INTO restaurants (id, name, cuisine, address, city, state, zip_code, description, price_tier, amenities, avg_rating, review_count, owner_id)
VALUES
  (1, 'Mazala Pizza', 'Italian', '123 Main St', 'San Jose', 'CA', '95112', 'Neighborhood pizza', '$$', 'outdoor', 4.5, 1, 2),
  (2, 'Bombay Spice', 'Indian', '456 Oak Ave', 'San Jose', 'CA', '95123', 'Indian vegetarian options', '$$', 'casual', 4.2, 0, NULL);

INSERT IGNORE INTO reviews (id, user_id, restaurant_id, rating, comment)
VALUES (1, 1, 1, 5, 'Great pizza!');

INSERT IGNORE INTO user_preferences (id, user_id, cuisines, price_range)
VALUES (1, 1, '["Italian","Indian"]', '$$');
