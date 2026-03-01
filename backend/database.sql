-- CREATE DATABASE yelp_db;
-- USE yelp_db;
-- CREATE TABLE users (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     
--     name VARCHAR(100) NOT NULL,
--     email VARCHAR(150) NOT NULL UNIQUE,
--     password_hash VARCHAR(255) NOT NULL,
--     
--     phone VARCHAR(20),
--     about TEXT,
--     city VARCHAR(100),
--     state VARCHAR(10),
--     country VARCHAR(100),
--     languages VARCHAR(255),
--     gender VARCHAR(20),
--     profile_pic VARCHAR(255),

--     role ENUM('user', 'owner') DEFAULT 'user',

--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- );

-- CREATE TABLE restaurants (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     
--     name VARCHAR(150) NOT NULL,
--     cuisine VARCHAR(100) NOT NULL,
--     
--     address VARCHAR(255),
--     city VARCHAR(100),
--     state VARCHAR(10),
--     zip_code VARCHAR(20),
--     
--     description TEXT,
--     contact_phone VARCHAR(20),
--     contact_email VARCHAR(150),
--     
--     price_tier ENUM('$', '$$', '$$$', '$$$$'),
--     
--     ambiance VARCHAR(255),
--     amenities VARCHAR(255),
--     
--     hours TEXT,
--     photos TEXT,
--     
--     owner_id INT NULL,
--     
--     avg_rating DECIMAL(2,1) DEFAULT 0.0,
--     review_count INT DEFAULT 0,

--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

--     FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
-- );

-- CREATE TABLE reviews (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     
--     user_id INT NOT NULL,
--     restaurant_id INT NOT NULL,
--     
--     rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
--     comment TEXT,
--     photos TEXT,
--     
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
--     FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,

--     UNIQUE KEY unique_user_review (user_id, restaurant_id)
-- );

-- CREATE TABLE favourites (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     
--     user_id INT NOT NULL,
--     restaurant_id INT NOT NULL,
--     
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
--     FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,

--     UNIQUE KEY unique_favourite (user_id, restaurant_id)
-- );

-- CREATE TABLE user_preferences (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     
--     user_id INT NOT NULL UNIQUE,
--     
--     cuisines VARCHAR(255),
--     price_range ENUM('$', '$$', '$$$', '$$$$'),
--     preferred_locations VARCHAR(255),
--     dietary_needs VARCHAR(255),
--     ambiance VARCHAR(255),
--     sort_preference VARCHAR(50),

--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
-- );

ALTER TABLE users ADD COLUMN restaurant_location VARCHAR(255);