# from https://www.federalregister.gov/documents/2016/05/27/2016-11867/food-labeling-revision-of-the-nutrition-and-supplement-facts-labels
drv = {
    'Vitamin A': 900.0,  # mcg
    'Vitamin C': 90.0,  # mg
    'Calcium': 1300.0,  # mg
    'Iron': 18.0,  # mg
    'Vitamin D': 20.0,  # mcg
    'Vitamin E': 15.0,  # mg
    'Vitamin K': 120.0,  # mcg
    'Thiamin': 1.2,  # mg
    'Riboflavin': 1.3,  # mg
    'Niacin': 16.0,  # mg
    'Vitamin B6': 1.7,  # mg
    'Folate': 400.0,  # mcg
    'Vitamin B12': 2.4,  # mcg
    'Biotin': 30.0,  # mcg
    'Pantothenic Acid': 5.0,  # mg
    'Phosphorus': 1250.0,  # mg
    'Iodine': 150.0,  # mcg
    'Magnesium': 420.0,  # mg
    'Zinc': 11.0,  # mg
    'Selenium': 55.0,  # mcg
    'Copper': 0.9,  # mg
    'Manganese': 2.3,  # mg
    'Chromium': 35.0,  # mcg
    'Molybdenum': 45.0,  # mcg
    'Chloride': 2300.0,  # mg
    'Potassium': 4700,  # mg
    'Choline': 550.0,  # mg
    'Fat': 78.0,  # g
    'Saturated fat': 20.0,  # g
    'Cholesterol': 300.0,  # mg
    'Carbohydrate': 275.0,  # g
    'Sodium': 2300.0,  # mg
    'Fiber': 28.0,  # g
    'Protein': 50.0,  # g
    'Added Sugars': 50.0,  # g
}

nutrient_names = [
    'Vitamin A',
    'Vitamin C',
    'Vitamin D',
    'Vitamin E',
    'Vitamin K',
    'Thiamin',
    'Riboflavin',
    'Niacin',
    'Vitamin B6',
    'Folate',
    'Vitamin B12',
    'Pantothenic Acid',
    'Biotin',
    'Choline',
    'Calcium',
    'Chromium',
    'Copper',
    #'Fluoride',
    'Iodine',
    'Iron',
    'Magnesium',
    'Manganese',
    'Molybdenum',
    'Phosphorus',
    'Selenium',
    'Zinc',
    'Potassium',
    'Sodium',
    'Chloride',
    'Carbohydrate',
    'Fiber',
    #'Linoleic Acid',
    #'Alpha-Linolenic Acid',
    'Protein',
]

nutrient_names_lookup = {
    'Vitamin A': 'Vitamin A, RAE',
    'Vitamin C': 'Vitamin C, total ascorbic acid',
    'Vitamin D': 'Vitamin D (D2 + D3)',
    'Vitamin E': 'Vitamin E (alpha-tocopherol)',
    'Vitamin K': 'Vitamin K (phylloquinone)',
    'Thiamin': 'Thiamin',
    'Riboflavin': 'Riboflavin',
    'Niacin': 'Niacin',
    'Vitamin B6': 'Vitamin B-6',
    'Folate': 'Folate',
    'Vitamin B12': 'Vitamin B-12',
    'Pantothenic Acid': 'Pantothenic acid',
    'Biotin': 'Biotin',
    'Choline': 'Choline, total',
    'Calcium': 'Calcium, Ca',
    'Chromium': 'Chromium, Cr',
    'Copper': 'Copper, Cu',
    'Fluoride': 'Fluoride, F',
    'Iodine': 'Iodine, I',
    'Iron': 'Iron, Fe',
    'Magnesium': 'Magnesium, Mg',
    'Manganese': 'Manganese, Mn',
    'Molybdenum': 'Molybdenum, Mo',
    'Phosphorus': 'Phosphorus, P',
    'Selenium': 'Selenium, Se',
    'Zinc': 'Zinc, Zn',
    'Potassium': 'Potassium, K',
    'Sodium': 'Sodium, Na',
    'Chloride': 'Chlorine',
    'Carbohydrate': 'Carbohydrate, by difference',
    'Fiber': 'Fiber, total dietary',
    'Linoleic Acid': '18:2 n-6 c,c',
    'Alpha-Linolenic Acid': '18:3 n-3 c,c,c (ALA)',
    'Protein': 'Protein',
}

nutrient_units = {
    'Vitamin A': 'mcg',
    'Vitamin C': 'mg',
    'Vitamin D': 'mcg',
    'Vitamin E': 'mg',
    'Vitamin K': 'mcg',
    'Thiamin': 'mg',
    'Riboflavin': 'mg',
    'Niacin': 'mg',
    'Vitamin B6': 'mg',
    'Folate': 'mcg',
    'Vitamin B12': 'mcg',
    'Pantothenic Acid': 'mg',
    'Biotin': 'mcg',
    'Choline': 'mg',
    'Calcium': 'mg',
    'Chromium': 'mcg',
    'Copper': 'mg',
    'Fluoride': 'mcg',
    'Iodine': 'mcg',
    'Iron': 'mg',
    'Magnesium': 'mg',
    'Manganese': 'mg',
    'Molybdenum': 'mcg',
    'Phosphorus': 'mg',
    'Selenium': 'mcg',
    'Zinc': 'mg',
    'Potassium': 'mg',
    'Sodium': 'mg',
    'Chloride': 'mg',
    'Carbohydrate': 'g',
    'Fiber': 'g',
    'Linoleic Acid': 'g',
    'Alpha-Linolenic Acid': 'g',
    'Protein': 'g',
}

