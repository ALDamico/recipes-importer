import psycopg2
from nltk.corpus import brown
import json
import random
from nltk import word_tokenize, UnigramTagger, FreqDist, ConditionalFreqDist
import csv
import threading
from datetime import datetime
from collections import defaultdict

def get_baseline_tagger():
    print("Initializing...", end=" ")
    tagged_words = brown.tagged_words()
    fd = FreqDist(brown.words())
    cfd = ConditionalFreqDist(brown.tagged_words())
    most_freq_words = fd.most_common()
    likely_tags = dict((word, cfd[word].max()) for (word, _) in most_freq_words)
    baseline_tagger = UnigramTagger(model=likely_tags)
    print("Done!")
    return baseline_tagger

def process_file(filename):
    start_time = datetime.now()
    with open(filename, 'r') as f:
        json_obj = json.load(f)
        for _, recipe in json_obj.items():
            if recipe == {}: continue  # Skip if it's an empty object
            recipe_db_obj = {}
            recipe['recipe_name'] = recipe['title']
            recipe['number_of_serves'] = random.randint(1, 10)
            process_ingredients(recipe['ingredients'])
    end_time = datetime.now() - start_time
    print(f"Processing for file {filename} ({len(json_obj.keys())} items) finished in {end_time}")



def process_ingredients(ingredients):
    for ingredient_string in ingredients:
        text = word_tokenize(ingredient_string)
        tags = baseline_tagger.tag(text) 
        ingredient_name = []
        ingredient_details = []
        quantity = 0
        unit_of_measurement = ""
        for tag in tags:
            word, part_of_speech = split_tuple(tag)
            try:
                uom = UNITS_OF_MEASUREMENT[word]
                unit_of_measurement = uom
            except KeyError:
                pass
            if part_of_speech in ('NN', 'NNS'):  # Nouns and possessive nouns
                if part_of_speech in UNITS_OF_MEASUREMENT.keys():
                    unit_of_measurement = part_of_speech
                else:
                    ingredient_name.append(word)
            elif part_of_speech == 'CD':  # cardinal numbers
                if looks_like_fraction(word):
                    quantity += looks_like_fraction(word)
                elif word.isdigit():
                    quantity += float(word)
                else:
                    ingredient_name.append(word)
            elif part_of_speech == 'ADJ':  # Adjectives
                ingredient_details.append(word)
            else:
                ingredient_details.append(word)
        if unit_of_measurement == "":
            unit_of_measurement = "s"  # single
        ingredient_name = ' '.join(ingredient_name)
        ingredients_csv[ingredient_name] = {'ingredient_name': ingredient_name}
                
                


def split_tuple(input):
    return input[0], input[1]


def looks_like_fraction(input):
    components = input.split('/')
    if len(components) != 2:
        return False
    try:
        return float(components[0]) / float(components[1])
    except ValueError:
        return False


def units_of_measurement_factory():
    return {
    # Tea spoon
    'tsp': 'tsp', 'tsp.': 'tsp', 'teaspoon': 'tsp', 'teaspoons': 'tsp', 'tea spoon'
    # Table spoon
    'tbsp': 'tbsp', 'tbsp.': 'tbsp', 'tablespoon': 'tbsp', 'table spoon': 'tbsp', 'tbsps': 'tbsp', 'tbsps.': 'tbsp', 'tablespoons': 'tbsp', 'table spoons': 'tbsp',
    # Fluid ounce
    'fluid ounce': 'fl oz', 'fluid ounces': 'fl oz', 'fl oz': 'fl oz',
    # Gill
    'gill': 'gill', 'gills': 'gill',
    # Cup
    'cup': 'c', 'cups': 'c', 'c': 'c',
    # Pint
    'pint': 'p', 'pints': 'p', 'p': 'p',
    # Quart
    'quart': 'q', 'quarts': 'q', 'q': 'q',
    # Gallon
    'gallon': 'gal', 'gallons': 'gal', 'gal': 'gal',
    # Milliliter
    'milliliter': 'ml', 'milliliters': 'ml', 'millilitre': 'ml', 'millilitres': 'ml', 'ml': 'ml',
    # Liter
    'liter': 'l', 'litre': 'l', 'litres': 'l', 'liters': 'l', 'l': 'l',
    # Deciliter
    'deciliter': 'dl', 'deciliters': 'dl', 'decilitre': 'dl', 'decilitres': 'dl', 'dl': 'dl',
    # Pound
    'pound': 'lb', 'pounds': 'lb', 'lb': 'lb',
    # Ounce
    'ounce': 'oz', 'ounces': 'oz', 'oz': 'oz',
    # Milligram
    'milligram': 'mg', 'milligrams': 'mg', 'milligramme': 'mg', 'milligrammes': 'mg', 'mg': 'mg',
    # Gram
    'gram': 'g', 'gramme': 'g', 'grams': 'g', 'grammes': 'g', 'g': 'g',
    # Kilogram
    'kilogram': 'kg', 'kilograms': 'kg', 'kilogramme': 'kg', 'kilogrammes': 'kg', 'kg': 'kg',
    # Millimeter
    'millimeter': 'mm', 'millimeters': 'mm', 'millimetre': 'mm', 'millimetres': 'mm', 'mm': 'mm',
    # Centimeter
    'centimeter': 'cm', 'centimeters': 'cm', 'centimetre': 'cm', 'centimetres': 'cm', 'cm': 'cm',
    # Meter
    'meter': 'm', 'meters': 'm', 'metres': 'm', 'metre': 'm', 'm': 'm',
    # Inch
    'inch': 'in', 'in': 'in', 'inches': 'in', '#': 'in'
}

baseline_tagger = get_baseline_tagger()

FILES = ["input_files/recipes_raw_nosource_ar.json", "input_files/recipes_raw_nosource_fn.json", "input_files/recipes_raw_nosource_epi.json"]
UNITS_OF_MEASUREMENT = defaultdict()
uom_fact = units_of_measurement_factory()
for key, value in uom_fact.items():
    UNITS_OF_MEASUREMENT[key] = value

ingredients_csv = {}

threads = []

"""
for file in FILES:
    print("Starting new thread for file {}".format(file))
    th = threading.Thread(target=process_file, args=(file,))
    threads.append(th)
    th.start()
    

for th in threads:
    th.join()"""


# Database connection
print("Establishing connection to postgres database")
connection_string = "dbname=recipes user=postgres password=password host=localhost"
sql_connection = psycopg2.connect(connection_string)
cursor = sql_connection.cursor()
cursor.execute(open("database/schema.sql", "r").read())
sql_connection.commit()
print("Recreated table structure")

print("Writing ingredients to csv file")
"""with open('output_files/ingredients.csv', 'w') as ingredient_file:
    fields = ['ingredient_name']
    ingredient_writer = csv.DictWriter(ingredient_file, fields)
    for row in ingredients_csv.keys():
        ingredient_writer.writerow(ingredients_csv[row])"""

print("Copying data to ingredients table")
with open("output_files/ingredients.csv", 'r', newline='\n') as ingredient_file:
    cursor.copy_from(ingredient_file, "ingredients", columns=("ingredient_name",), sep=";")
    sql_connection.commit()