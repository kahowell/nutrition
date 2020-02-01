import json
from fractions import Fraction

from vue import *
from recipe import *
from plan import *
from groceries import *
from js import VueOnsen, Vue, eval, document, console, PouchDB, window
from store import store


@vue_class
class InitializingPage:
    options = {
        'template': '#initializing',
        'key': 'initializing',
    }

    def __init__(self):
        store.load_db()

    @property
    def message(self, _):
        return store.state.message


@vue_class
class MainPage:
    options =  {
        'template': '#main',
        'key': 'main',
    }

    def __init__(self):
        self.tabs = [
            {
                'icon': 'md-book',
                'label': 'Recipes',
                'page': RecipePage,
            },
            {
                'icon': 'md-calendar',
                'label': 'Meal Plan',
                'page': PlansPage,
            },
            {
                'icon': 'md-shopping-cart', 
                'label': 'Groceries',
                'page': GroceriesPage,
            },
        ]
        console.log(self.tabs)
        self.index = 0

    @property
    def title(self, *args):
        return self.tabs[self.index]['label']

    def update_index(self, index):
        self.index = index

@vue_class
class NutritionApp:
    options = {
        'el': '#app',
        'template': '#navigator',
    }

    def __init__(self):
        self.state = store.state  # track store.state
        store.push_page(InitializingPage)

    @property
    def page_stack(self, *args):
        return store.state.page_stack


if not VueOnsen.platform.isIPhone() and not VueOnsen.platform.isIPad() and '?platform' not in document.URL:
    VueOnsen.platform.select('android')

store.main_page = MainPage

Vue.use(VueOnsen)
Vue.new(NutritionApp)
document.getElementById('loading').remove()
