import json
from fractions import Fraction
from itertools import permutations

from vue import *
from js import VueOnsen, Vue, document, console, window

from recommendations import drv
from store import store, foods_db, recipes_db

class RecipeEntryStore(VueStore):
    def __init__(self):
        super().__init__()
        self.state.recipe = None

    def add_ingredient(self, ingredient_id):
        def on_ingredient_load(error, ingredient):
            self.state.recipe.ingredients.push({
                'ingredient': ingredient,
                'amount': None,
                'portion': None,
            })
        foods_db.get(ingredient_id, on_ingredient_load)

    def reset(self, recipe=None):
        self.state.recipe = recipe or {
            '_id': None,
            'name': None,
            'servings': None,
            'ingredients': [],
            'instructions': [],
            'nutrients_per_serving': {},
        }


recipe_entry_store = RecipeEntryStore()

@vue_class
class RecipePage:
    options = {
        'template': '#recipes'
    }

    def __init__(self):
        print('reloading recipes!')
        store.load_recipes()

    @property
    def recipes(self, *args):
        return store.state.recipes

    def add_recipe(self, *args):
        recipe_entry_store.reset()
        store.push_page(AddRecipePage)

    def remove_recipe(self, recipe):
        def on_removed(*args):
            store.load_recipes()
        def handle_response(response):
            if response:
                recipes_db.remove(recipe, on_removed)
        self['$ons'].notification.confirm(f'Remove {recipe.name}?').then(handle_response)

    def view_recipe(self, recipe_id):
        def on_load(error, result):
            recipe_entry_store.state.recipe = result
            store.push_page(ViewRecipePage)
        recipes_db.get(recipe_id, on_load)


@vue_class
class ViewRecipePage:
    options = {
        'template': '#view-recipe',
        'key': 'view-recipe',
    }

    @property
    def recipe(self, *args):
        return recipe_entry_store.state.recipe

    def edit_recipe(self, *args):
        recipe_entry_store.reset(recipe_entry_store.state.recipe)
        store.push_page(AddRecipePage)


@vue_class
class NutritionFacts:
    options = {
        'template': '#nutfacts',
        'props': ['nutrients', 'servings'],
        'key': 'nutfacts',
    }

    def get_percent(self, value, drv_name):
        value = value or 0.0
        return f'{(value / drv[drv_name]) * 100.0:.0f}'

    def format_amount(self, amount):
        amount = amount or 0
        return f'{float(amount):.0f}'

Vue.component('nutrition-facts', NutritionFacts)


MORE_LETTERS_MESSAGE = 'Please enter at least 3 letters to search ingredients.'

class IngredientSearchStore(VueStore):
    def __init__(self):
        super().__init__()
        self.timeout = None
        self.state.message = MORE_LETTERS_MESSAGE
        self.state.matches = []
        self.state.query = ''
        self.state.categories = {
            "American Indian/Alaska Native Foods": True,
            "Baby Foods": True,
            "Baked Products": False,
            "Beef Products": False,
            "Beverages": False,
            "Breakfast Cereals": False,
            "Cereal Grains and Pasta": False,
            "Dairy and Egg Products": False,
            "Fast Foods": True,
            "Fats and Oils": False,
            "Finfish and Shellfish Products": False,
            "Fruits and Fruit Juices": False,
            "Lamb, Veal, and Game Products": False,
            "Legumes and Legume Products": False,
            "Meals, Entrees, and Side Dishes": False,
            "Nut and Seed Products": False,
            "Pork Products": False,
            "Poultry Products": False,
            "Restaurant Foods": True,
            "Sausages and Luncheon Meats": False,
            "Snacks": True,
            "Soups, Sauces, and Gravies": False,
            "Spices and Herbs": False,
            "Sweets": True,
            "Vegetables and Vegetable Products": False,
        }
    
    def schedule_search(self):
        if self.timeout is not None:
            window.clearTimeout(self.timeout)
        self.timeout = window.setTimeout(self.search, 1000)

    def search(self):
        self.state.matches = []
        def get_disabled_categories():
            disabled = []
            for key, value in self.state.categories:
                if value:
                    disabled.append(key)
            return disabled

        def on_loaded(original_query):
            def _inner(error, result=None):
                if error:
                    console.error(error)
                console.debug('query_result', result)
                if self.state.query != original_query:
                    return
                self.state.message = None
                self.state.matches = result.docs
                if len(self.state.matches) == 0:
                    self.state.message = 'No matches.'
            return _inner

        if len(self.state.query) >= 3:
            print('query looks fine')
            self.state.message = 'Loading...'
            disabled_categories = get_disabled_categories()
            selector = {
                'keywords': {
                    '$all': [keyword.lower() for keyword in self.state.query.split()]
                },
            }
            if len(disabled_categories) > 0:
                selector['category'] = {'$nin': disabled_categories}
            console.debug(selector)
            def find(*args):
                console.debug(args)
                foods_db.find({
                    'selector': selector
                }, on_loaded(self.state.query))
            foods_db.createIndex({
                 'index': {
                     'fields': ['keywords'],
                 }
            }).then(find)
        else:
            self.state.message = MORE_LETTERS_MESSAGE

    def regexify_query(self):
        words = self.state.query.split()
        regexified = '|'.join([word.lower() for word in ['.*'.join(permutation) for permutation in permutations(words)]])
        return regexified


ingredient_search_store = IngredientSearchStore()

@vue_class
class AddIngredientPage:
    options = {
        'template': '#add-ingredient',
        'key': 'add-ingredient',
    }

    def __init__(self):
        self.state = ingredient_search_store.state

    @property
    def message(self, *args):
        return self.state.message

    @property
    def categories(self, *args):
        return self.state.categories

    @property
    def matches(self, *args):
        return self.state.matches

    def update_search(self, event):
        self.state.query = event.target.value
        ingredient_search_store.schedule_search()

    def schedule_search(self, *args):
        ingredient_search_store.schedule_search()

    def add_ingredient(self, ingredient_id):
        recipe_entry_store.add_ingredient(ingredient_id)
        store.pop_page()


@vue_class
class AddRecipePage:
    options = {
         'template': '#add-recipe', 
         'key': 'add-recipe',
    }

    def __init__(self):
        self.state = recipe_entry_store.state

    @property
    def recipe(self, *args):
        return self.state.recipe

    @property
    def save_disabled(self, *args):
        if not self.state.recipe.name:
            return True
        try:
            float(self.state.recipe.servings)
        except (TypeError, ValueError):
            return True
        for instruction in self.state.recipe.instructions:
            if not instruction:
                return True
        if len(self.state.recipe.ingredients) == 0:
            return True
        for ingredient in self.state.recipe.ingredients:
            try:
                float(ingredient['amount'])
            except (TypeError, ValueError):
                return True
            if not ingredient['portion']:
                return True
        for instruction in self.state.recipe.instructions:
            if not instruction['text']:
                return True
        return False


    def open_ingredients(self, *args):
        store.push_page(AddIngredientPage)

    def remove_ingredient(self, ingredient_index):
        def handle_response(response):
            if response:
                recipe_entry_store.state.recipe.ingredients.splice(ingredient_index, 1)
        ingredient = recipe_entry_store.state.recipe.ingredients[ingredient_index]
        self['$ons'].notification.confirm(f'Remove {ingredient.ingredient.name}?').then(handle_response)

    def add_instruction(self, *args):
        self.state.recipe.instructions.push({'text':''})

    def remove_instruction(self, index):
        def handle_response(response):
            if response:
                self.state.recipe.instructions.splice(index, 1)
        self['$ons'].notification.confirm('Remove instruction line?').then(handle_response)

    def get_nutrition_facts(self, *args):
        console.log('calculating nutrition facts')
        all_nutrients = {}
        for ingredient in self.state.recipe.ingredients:
            # calculate the number of grams this particular ingredient takes up
            amount = ingredient.amount or 0
            if ingredient.portion is None or ingredient.amount is None:
                continue
            portion = ingredient.portion
            portion_record = list(filter(lambda portion_record: portion_record.modifier == portion, ingredient.ingredient.portions))[0]
            servings_ratio = (1.0 / float(self.state.recipe.servings))
            portion_ratio = (portion_record.weight_grams / 100.0) * float(amount)
            ratio = servings_ratio * portion_ratio
            for (nutrient, value) in ingredient.ingredient.nutrients_per_100g:
                effective_value = ratio * value
                if nutrient not in all_nutrients:
                    all_nutrients[nutrient] = 0.0
                all_nutrients[nutrient] += effective_value

        return all_nutrients

    def save(self, *args):
        def on_saved(result):
            self.state.recipe._rev = result.rev
            store.load_recipes()
            store.pop_page()
        self.state.recipe.nutrients_per_serving = self.get_nutrition_facts()
        self.state.recipe._id = self.state.recipe._id or self.state.recipe.name.lower()
        if type(self.state.recipe.servings) == 'str':
            self.state.recipe.servings = float(self.state.recipe.servings)
        recipes_db.put(self.state.recipe).then(on_saved)
