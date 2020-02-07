#!/usr/bin/env python
import requests
from tqdm import tqdm
from pyodideapp.build import *

import csv
import glob
import json
import os
import re
import shutil

SR_URL = 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_%202019-04-02.zip'
SR_SHA256SUM = '541b56ee704e1ba7b48d9ef06683f817ef941da7a3f5e5888858b58f57b1fda3'
SUPPORT_URL = 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_Supporting_Data_csv_%202019-04-02.zip'
SUPPORT_SHA256SUM = '67c9abfdd8634fcec058c78154c31627c3c6b21e42ddd9d8cb2dc0805ae3d8de'


def load(path, table):
    with open(os.path.join(path, f'{table}.csv'), 'r') as file:
        lines = file.read().splitlines()
        return csv.DictReader(lines)


def energy_fix(row):
    if row['name'] == 'Energy' and row['unit_name'] == 'kJ':
        row['name'] = 'Energy, kJ'
    return row


class FoodsSource:
    def build(self, root, copy, **kwargs):
        sr_dir = Archive(Url(SR_URL, sha256sum=SR_SHA256SUM)).build(root, copy=copy, **kwargs)
        support_dir = Archive(Url(SUPPORT_URL, sha256sum=SUPPORT_SHA256SUM)).build(root, copy=copy, **kwargs)

        cache_destination = os.path.join(CACHE_PATH, 'all_foods.json')
        if not os.path.exists(cache_destination):
            print('Extracting info from files')
            categories = {row['id']: row['description'] for row in load(support_dir, 'food_category')}
            attribute_types = {row['id']: row['name'] for row in load(support_dir, 'food_attribute_type')}
            nutrients = {row['id']: row['name'] for row in map(energy_fix, load(support_dir, 'nutrient'))}
            uoms = {row['id']: row['name'] for row in load(support_dir, 'measure_unit')}
            foods = load(sr_dir, 'food')

            food_attributes = {}
            for row in load(sr_dir, 'food_attribute'):
                fdc_id = row['fdc_id']
                if fdc_id not in food_attributes:
                    food_attributes[fdc_id] = []
                food_attributes[fdc_id].append(row)

            food_nutrients = {}
            for row in load(sr_dir, 'food_nutrient'):
                fdc_id = row['fdc_id']
                if fdc_id not in food_nutrients:
                    food_nutrients[fdc_id] = []
                food_nutrients[fdc_id].append(row)

            food_portions = {}
            for row in load(sr_dir, 'food_portion'):
                fdc_id = row['fdc_id']
                if fdc_id not in food_portions:
                    food_portions[fdc_id] = []
                food_portions[fdc_id].append(row)


            print('Normalizing nutrient data')

            all_foods = []


            pattern = re.compile('[, ]')

            for food_record in tqdm(list(foods)):
                fdc_id = food_record['fdc_id']
                food = {'nutrients_per_100g':{}}
                food['_id'] = food_record['description'].lower()
                food['name'] = food_record['description']
                food['fdc_id'] = food_record['fdc_id']
                food['keywords'] = sorted(set([keyword for keyword in pattern.split(food['_id']) if keyword]))
                food['category'] = categories[food_record['food_category_id']]

                for attribute in food_attributes.get(fdc_id, []):
                    attribute_name = attribute_types[attribute['food_attribute_type_id']]
                    if attribute_name == 'Common Name':
                        if 'common_names' not in food:
                            food['common_names'] = []
                        food['common_names'].append(attribute['value'])
                    elif attribute_name == 'Additional Description':
                        if 'additional_descriptions' not in food:
                            food['additional_descriptions'] = []
                        food['additional_descriptions'].append(attribute['value'])

                for nutrient in food_nutrients.get(fdc_id, []):
                    nutrient_name = nutrients[nutrient['nutrient_id']]
                    food['nutrients_per_100g'][nutrient_name] = float(nutrient['amount'])

                for portion_record in food_portions.get(fdc_id, []):
                    if 'portions' not in food:
                        food['portions'] = []
                    uom = portion_record['measure_unit_id']
                    portion = {
                        'amount': float(portion_record['amount']),
                        'modifier': portion_record['modifier'],
                        'weight_grams': float(portion_record['gram_weight']),
                    }
                    if portion_record['portion_description']:
                        portion['description'] = portion_record['portion_description']
                    food['portions'].append(portion)

                all_foods.append(food)

            with open(cache_destination, 'w') as output:
                output.write(json.dumps(all_foods))

        destination = os.path.join(root, 'all_foods.json')
        if not os.path.exists(destination):
            if copy:
                shutil.copy(cache_destination, destination)
            else:
                os.symlink(os.path.abspath(cache_destination), destination)
