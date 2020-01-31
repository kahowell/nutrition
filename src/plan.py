from datetime import datetime
import json
from fractions import Fraction
from itertools import permutations

from vue import *
from js import VueOnsen, Vue, document, console, window

from recommendations import drv, nutrient_names, nutrient_names_lookup
from recommendations import nutrient_units as _nutrient_units
from store import store, foods_db, recipes_db, plans_db


class MealPlansStore(VueStore):
    def __init__(self):
        super().__init__()
        self.state.plans = []
        self.load_plans()

    def load_plans(self):
        def on_loaded(error, result):
            self.state.plans = list(map(lambda row: row.doc, result.rows))
        plans_db.allDocs({'include_docs': True}, on_loaded)

meal_plans_store = MealPlansStore()

class PlanStore(VueStore):
    def __init__(self):
        super().__init__()
        self.state.plan = None
        self.state.day_index = 0
        self.state.meal = None

    def new_day(self):
        return {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': [],
        }

    def new_plan(self):
        self.state.plan = {
            '_id': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'name': datetime.now().strftime('%Y-%m-%d'),
            'days': [self.new_day() for i in range(7)]
        }

    def adjust_number_days(self, value):
        while self.state.plan.days.length > value:
            self.state.plan.days.pop()
        while self.state.plan.days.length < value:
            self.state.plan.days.push(self.new_day())

    def load_plan(self, plan_id):
        def on_loaded(error, plan):
            self.state.plan = plan
        plans_db.get(plan_id, on_loaded)

plan_store = PlanStore()

class ChooseRecipeStore(VueStore):
    def __init__(self):
        super().__init__()
        self.state.recipes = []

choose_recipe_store = ChooseRecipeStore()

@vue_class
class ChooseRecipePage:
    options = {
        'template': '#choose-recipe'
    }

    def __init__(self):
        self.recipes_state = store.state
        self.plan_state = plan_store.state
        self.state = choose_recipe_store.state

    @property
    def recipes(self, *args):
        return store.state.recipes

    @property
    def plan(self, *args):
        return plan_store.state.plan

    @property
    def day(self, *args):
        return plan_store.state.day_index + 1

    @property
    def meal(self, *args):
        return plan_store.state.meal

    def add_recipe(self, recipe_id):
        def on_loaded(error, recipe):
            plan_store.state.plan.days[plan_store.state.day_index][plan_store.state.meal].push(recipe)
            console.log(plan_store.state.plan.days)
            store.pop_page()
        recipes_db.get(recipe_id, on_loaded)


@vue_class
class PlanPage:
    options = {
        'template': '#plan',
    }

    def __init__(self):
        self.state = plan_store.state
        self.carousel_index = 0

    @property
    def plan(self, *args):
        return self.state.plan

    def adjust_number_days(self, event):
        new_value = int(event.target.value)
        plan_store.adjust_number_days(new_value)

    def total_calories(self, day_index):
        day = self.state.plan.days[day_index]
        total_calories = 0
        for (meal, foods) in day:
            for food in foods:
                total_calories += food.nutrients_per_serving.Energy
        return total_calories

    def format_amount(self, amount):
        amount = amount or 0
        return f'{float(amount):.0f}'

    @property
    def daily_nutrients(self, *args):
        all_nutrients = {}
        for day in self.state.plan.days:
            for (meal, foods) in day:
                for food in foods:
                    for nutrient in nutrient_names:
                        stored_name = nutrient_names_lookup.get(nutrient)
                        console.log(food.nutrients_per_serving)
                        if hasattr(food.nutrients_per_serving, stored_name):
                            all_nutrients[nutrient] = all_nutrients.get(nutrient, 0.0) + food.nutrients_per_serving[stored_name]
        for nutrient in all_nutrients:
            all_nutrients[nutrient] = all_nutrients[nutrient] / float(self.state.plan.days.length)
        return all_nutrients

    def nutrient_percentage(self, amount, nutrient):
        amount = amount or 0
        needed = drv[nutrient]
        return float(amount) / float(needed) * 100.0

    @property
    def nutrient_list(self, *args):
        return nutrient_names
        
    @property
    def nutrient_units(self, *args):
        return _nutrient_units

    def save(self, *args):
        def on_saved(*args):
            meal_plans_store.load_plans()
            store.pop_page()
        plans_db.put(self.state.plan).then(on_saved)

@vue_class
class PlansPage:
    options = {
        'template': '#mealplans'
    }

    def __init__(self):
        self.state = meal_plans_store.state

    @property
    def plans(self, *args):
        return self.state.plans

    def add_plan(self, *args):
        plan_store.new_plan()
        store.push_page(PlanPage)

    def view_plan(self, plan_id):
        def on_loaded(error, plan):
            plan_store.state.plan = plan
            store.push_page(PlanPage)
        plans_db.get(plan_id, on_loaded)

@vue_class
class FoodsDisplay:
    options = {
        'template': '#foods',
        'props': ['day', 'day_index', 'meal', 'title']
    }

    def __init__(self):
        self.state = plan_store.state

    def add_recipe(self, day_index, meal):
        plan_store.state.day_index = day_index
        plan_store.state.meal = meal
        store.push_page(ChooseRecipePage)

    def format_amount(self, amount):
        amount = amount or 0
        return f'{float(amount):.0f}'

Vue.component('foods', FoodsDisplay)