CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE,
  password TEXT,
  admin BOOLEAN,
  barowner BOOLEAN
);
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  category TEXT
);
CREATE TABLE bars (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE,
  owner_id INTEGER REFERENCES users,
  category INTEGER REFERENCES categories
);

CREATE TABLE description (
  id SERIAL PRIMARY KEY,
  description TEXT,
  bar_id INTEGER REFERENCES bars
);

CREATE TABLE openhours (
  id SERIAL PRIMARY KEY,
  weekday INTEGER,
  opening TEXT,
  closing TEXT,
  bar_id INTEGER REFERENCES bars
);
CREATE TABLE location (
  id SERIAL PRIMARY KEY,
  address TEXT,
  bar_id INTEGER REFERENCES bars
);
CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  comment TEXT,
  rating INTEGER,
  user_id INTEGER REFERENCES users,
  bar_id INTEGER REFERENCES bars
);
