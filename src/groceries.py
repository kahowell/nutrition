from datetime import datetime
import json
import math
from fractions import Fraction
from itertools import permutations

from vue import *
from js import VueOnsen, Vue, document, console, window, PouchDB

from recommendations import drv, nutrient_names, nutrient_names_lookup
from recommendations import nutrient_units as _nutrient_units
from store import store, meal_plans_store

groceries_db = PouchDB.new('groceries')


class GroceryListStore(VueStore):
    def __init__(self):
        super().__init__()
        self.state.list = []
        self.load_list()

    def load_list(self):
        def on_loaded(error, result):
            self.state.list = list(map(lambda row: row.doc, result.rows))
        groceries_db.allDocs({'include_docs': True}, on_loaded)

    def remove(self, item):
        def on_removed(*args):
            self.load_list()
        groceries_db.remove(item, on_removed)

    def format_ingredient(self, ingredient):
        return {
            '_id': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'name': f'{ingredient.ingredient.name} - {ingredient.amount} {ingredient.portion}',
            'checked': False,
        }

    def add_ingredients(self, ingredients):
        def callback(*args):
            self.load_list()
            store.pop_page()
        groceries_db.bulkDocs([self.format_ingredient(ingredient) for ingredient in ingredients], callback)

    def save_item(self, item):
        def callback(error, result=None):
            if error:
                alert(error)
            item._rev = result.rev
        groceries_db.put(item, callback)

list_store = GroceryListStore()


@vue_class
class AddItemsPage:
    options = {
        'template': '#add-grocery-items'
    }

    def __init__(self):
        self.plans_state = meal_plans_store.state
        self.checked_plans = []
        self.checked_days = []
        self.checked_meals = []

    @property
    def plans(self, *args):
        return meal_plans_store.state.plans

    def toggle_plan(self, plan, event):
        checked = event.value
        for day_index, day in enumerate(plan.days):
            value = f'{plan.name},{day_index}'
            array_index = self.checked_days.indexOf(value)
            if checked and array_index == -1:
                self.checked_days.push(value)
            elif not checked and array_index != -1:
                self.checked_days.splice(array_index, 1)
            for meal in ['breakfast', 'lunch', 'dinner', 'snacks']:
                value = f'{plan.name},{day_index},{meal}'
                array_index = self.checked_meals.indexOf(value)
                if checked and array_index == -1:
                    self.checked_meals.push(value)
                elif not checked and array_index != -1:
                    self.checked_meals.splice(array_index, 1)

    def toggle_day(self, plan, day_index, event):
        checked = event.value
        for meal in ['breakfast', 'lunch', 'dinner', 'snacks']:
            value = f'{plan.name},{day_index},{meal}'
            array_index = self.checked_meals.indexOf(value)
            if checked and array_index == -1:
                self.checked_meals.push(value)
            elif not checked and array_index != -1:
                self.checked_meals.splice(array_index, 1)

    def add(self, *args):
        plans = {plan.name: plan for plan in meal_plans_store.state.plans}
        all_ingredients = []
        for value in self.checked_meals:
            plan_name, day_index, meal = value.rsplit(',', 2)
            for recipe in plans[plan_name].days[day_index][meal]:
                for ingredient in recipe.ingredients:
                    all_ingredients.append(ingredient)
        all_ingredients.sort(key=lambda ingredient: (ingredient.ingredient.category, ingredient.ingredient.name))
        list_store.add_ingredients(all_ingredients)


@vue_class
class GroceriesPage:
    options = {
        'template': '#groceries'
    }

    def __init__(self):
        self.state = list_store.state

    @property
    def list(self, *args):
        return self.state.list

    def add_items(self, *args):
        store.push_page(AddItemsPage)

    def remove_item(self, item):
        def handle_response(response):
            if response:
                list_store.remove(item)
        self['$ons'].notification.confirm(f'Remove {item.name}?').then(handle_response)

    def save_item(self, item, event):
        item.checked = event.value
        list_store.save_item(item)