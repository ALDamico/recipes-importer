DROP TABLE IF EXISTS ingredients_fulltext;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS units_of_measurement;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipe_comments;
DROP TABLE IF EXISTS recipes_fulltext;
DROP TABLE IF EXISTS recipe_steps;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(40) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    password_salt VARCHAR(200) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    registered_on TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activated_on TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_registration_date ON users(registered_on);

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    recipe_name VARCHAR(100) NOT NULL,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0,
    number_of_serves INTEGER,
    posted_on TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_recipes_users ON recipes(user_id);
CREATE INDEX idx_recipes_posted_on ON recipes(posted_on);

CREATE TABLE recipe_steps (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL,
    step_text VARCHAR(500),
    step_image VARCHAR(5000),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

CREATE TABLE units_of_measurement (
    code VARCHAR(5) NOT NULL PRIMARY KEY,
    unit_name VARCHAR(20) NOT NULL,
    unit_type VARCHAR(20)
);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(80)
);

CREATE TABLE recipe_ingredients (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit_of_measurement_code VARCHAR(5),
    details VARCHAR(500),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (unit_of_measurement_code) REFERENCES units_of_measurement(code)
);

CREATE INDEX idx_recipe_ingredients_recipes ON recipe_ingredients(recipe_id, ingredient_id);

CREATE TABLE ingredients_fulltext (
	id SERIAL PRIMARY KEY,
	recipe_ingredients_id INTEGER NOT NULL,
	ingredient_data TSVECTOR NOT NULL,
	FOREIGN KEY (recipe_ingredients_id) REFERENCES recipe_ingredients(id)
);

CREATE INDEX idx_text_search_ingredients ON ingredients_fulltext USING GIN(ingredient_data);
CREATE INDEX idx_text_search_recipe ON ingredients_fulltext(recipe_ingredients_id);

CREATE TABLE recipes_fulltext (
	id SERIAL PRIMARY KEY,
	recipe_id INTEGER NOT NULL,
	recipe_step_id INTEGER NOT NULL,
	recipe_data TSVECTOR,
	FOREIGN KEY (recipe_id) REFERENCES recipes(id),
	FOREIGN KEY (recipe_step_id) REFERENCES recipe_steps(id)
);

CREATE INDEX idx_text_search_recipes ON recipes_fulltext USING GIN(recipe_data);
CREATE INDEX idx_text_search_recipe_id ON recipes_fulltext(recipe_id);

CREATE OR REPLACE FUNCTION recipe_fulltext_search_indexing()
RETURNS TRIGGER
LANGUAGE plpgsql
AS 
$$
DECLARE vec TSVECTOR;
BEGIN 
	INSERT INTO recipes_fulltext(recipe_id, recipe_step_id, recipe_data)
	VALUES (NEW.recipe_id, NEW.recipe_step_id, TO_TSVECTOR(NEW.step_text));
	RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION ingredients_fulltext_search_indexing()
RETURNS TRIGGER 
LANGUAGE plpgsql
AS
$$
DECLARE vec TSVECTOR;
DECLARE str TEXT;
DECLARE ingr_name TEXT;
BEGIN
	SELECT ingredient_name 
	INTO ingr_name
	FROM ingredients
	WHERE id = NEW.ingredient_id;

	RAISE NOTICE 'ingredient name % new details % old details %', ingr_name, NEW.details, OLD.details;
	
	str := ingr_name || ' ' || NEW.details;

	INSERT INTO ingredients_fulltext (recipe_ingredients_id, ingredient_data)
	VALUES (NEW.id, to_tsvector(str));
	RETURN NEW;
END;
$$;



CREATE TRIGGER ingredient_fulltext_indexing 
AFTER INSERT ON recipe_ingredients 
FOR EACH ROW 
EXECUTE PROCEDURE ingredients_fulltext_search_indexing();

CREATE TRIGGER recipe_fulltext_indexing 
AFTER INSERT ON recipes_fulltext 
FOR EACH ROW 
EXECUTE PROCEDURE recipe_fulltext_search_indexing();




INSERT INTO users(username, password_hash, password_salt, is_admin, registered_on, activated_on)
VALUES ('admin', 'admin', 'admin', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    , ('demo', 'demo', 'demo', FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


INSERT INTO units_of_measurement(code, unit_name, unit_type)
VALUES  ('tsp', 'teaspoon', 'volume'),
        ('tbsp', 'tablespoon', 'volume'),
        ('fl oz', 'fluid ounce', 'volume'),
        ('gill', 'gill', 'volume'),
        ('c', 'cup', 'volume'),
        ('p', 'pint', 'volume'),
        ('q', 'quart', 'volume'),
        ('gal', 'gallon', 'volume'),
        ('ml', 'milliliter', 'volume'),
        ('l', 'liter', 'volume'),
        ('dl', 'deciliter', 'volume'),
        ('lb', 'pound', 'weight'),
        ('oz', 'ounce',  'weight'),
        ('mg', 'milligram', 'weight'),
        ('g', 'gram', 'weight'),
        ('kg', 'kilogram', 'weight'),
        ('mm', 'millimeter', 'length'),
        ('cm', 'centimeter', 'length'),
        ('m', 'meter', 'length'),
        ('in', 'inch', 'length'),
        ('s', 'unit', NULL);
        
    
    
CREATE TABLE recipe_comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    comment_text VARCHAR(1000) NOT NULL,
    likes INTEGER,
    dislikes INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);