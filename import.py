import psycopg2
from nltk.corpus import brown
import json
import random
from nltk import pos_tag, word_tokenize, map_tag, UnigramTagger, FreqDist, ConditionalFreqDist

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
    with open(filename, 'r') as f:
        json_obj = json.load(f)
        for _, recipe in json_obj.items():
            if recipe == {}: continue  # Skip if it's an empty object
            recipe_db_obj = {}
            recipe['recipe_name'] = recipe['title']
            recipe['number_of_serves'] = random.randint(1, 10)
            process_ingredients(recipe['ingredients'])



def process_ingredients(ingredients):
    for ingredient_string in ingredients:
        text = word_tokenize(ingredient_string)
        tags = baseline_tagger.tag(text) #pos_tag(text)
        ingredient_name = []
        ingredient_details = []
        quantity = 0
        unit_of_measurement = ""
        for tag in tags:
            word, part_of_speech = split_tuple(tag)
            if part_of_speech in ('NN', 'NNS'):  # Nouns and possessive nouns
                ingredient_name.append(word)
            elif part_of_speech == 'CD':  # cardinal numbers
                if looks_like_fraction(word):
                    quantity += looks_like_fraction(word)
                else:
                    quantity += float(word)
            elif part_of_speech == 'ADJ':  # Adjectives
                ingredient_details.append(word)
            else:
                ingredient_details.append(word)
        if unit_of_measurement == "":
            unit_of_measurement = "s"  # single
                
                


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

baseline_tagger = get_baseline_tagger()

FILES = ["input_files/recipes_raw_nosource_ar.json", "input_files/recipes_raw_nosource_fn.json", "input_files/recipes_raw_nosource_epi.json"]
UNITS_OF_MEASUREMENT = {
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
    
}



for file in FILES:
    process_file(file)