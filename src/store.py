import json

from js import PouchDB, window

from vue import *

foods_db = PouchDB.new('foods')
recipes_db = PouchDB.new('recipes')
plans_db = PouchDB.new('plans')


class NutritionAppStore(VueStore):
    def __init__(self):
        super().__init__()
        self.state.message = 'Loading...'
        self.state.page_stack = []
        self.state.recipes = []
        self.state.has_no_recipes = False
        self.main_page = None
        window.onpopstate = self.onpopstate

    def load_db(self):
        def on_loaded(error, result):
            def handle_text(text):
                all_foods = json.loads(text)
                foods_db.bulkDocs(all_foods, lambda *args: self.load_main_page())

            def handle_response(response):
                response.text().then(handle_text)
            if result.doc_count > 0:
                self.load_main_page()
            else:
                self.state.message = "Loading foods & nutrition data..."
                window.fetch('all_foods.json').then(handle_response)
        foods_db.info(on_loaded)

    def load_recipes(self):
        def on_loaded(error, result):
            self.state.recipes = list(map(lambda row: row.doc, result.rows))
            if len(self.state.recipes) == 0:
                self.state.has_no_recipes = True
            console.log(self.state.recipes)
        recipes_db.allDocs({'include_docs': True}, on_loaded)

    def load_main_page(self):
        self.state.page_stack = [self.main_page]

    def push_page(self, page):
        self.state.page_stack.push(page)
        #window.history.pushState(len(self.state.page_stack), '')

    def pop_page(self, *args):
        self.state.page_stack.pop()
        #window.history.back()

    def onpopstate(self, *args):
        print('state popped!')
        #self.state.page_stack.pop()

store = NutritionAppStore()

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