-- CptS 451 Milestone 2
-- Kwadwo Afriyie
-- RELATIONS_v2.sql

CREATE TABLE ZipcodeData (
    zipcode VARCHAR(10) PRIMARY KEY,
    population INT,
    avg_income NUMERIC
);

CREATE TABLE Business (
    business_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(10) NOT NULL,
    zipcode VARCHAR(10) NOT NULL,
    stars NUMERIC(3,1),
    review_count INT DEFAULT 0,
    is_open INT,
    num_checkins INT DEFAULT 0,
    reviewrating NUMERIC(3,2) DEFAULT 0.0,
    FOREIGN KEY (zipcode) REFERENCES ZipcodeData(zipcode)
);

CREATE TABLE Category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Business_Category (
    business_id VARCHAR(50),
    category_id INT,
    PRIMARY KEY (business_id, category_id),
    FOREIGN KEY (business_id) REFERENCES Business(business_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

CREATE TABLE Business_Attribute (
    business_id VARCHAR(50),
    attribute_name VARCHAR(100),
    attribute_value VARCHAR(100),
    PRIMARY KEY (business_id, attribute_name),
    FOREIGN KEY (business_id) REFERENCES Business(business_id) ON DELETE CASCADE
);

CREATE TABLE Yelp_User (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    yelping_since VARCHAR(50),
    review_count INT,
    fans INT,
    avg_stars NUMERIC(3,2),
    funny INT,
    useful INT,
    cool INT
);

CREATE TABLE Review (
    review_id VARCHAR(50) PRIMARY KEY,
    business_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    stars NUMERIC(3,1) NOT NULL,
    date VARCHAR(50),
    text TEXT,
    useful INT,
    funny INT,
    cool INT,
    FOREIGN KEY (business_id) REFERENCES Business(business_id),
    FOREIGN KEY (user_id) REFERENCES Yelp_User(user_id)
);

CREATE TABLE Checkin (
    business_id VARCHAR(50) NOT NULL,
    day VARCHAR(20) NOT NULL,
    time VARCHAR(10) NOT NULL,
    count INT NOT NULL,
    PRIMARY KEY (business_id, day, time),
    FOREIGN KEY (business_id) REFERENCES Business(business_id) ON DELETE CASCADE
);