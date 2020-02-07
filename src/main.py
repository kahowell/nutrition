import json
from fractions import Fraction

from vue import *
from recipe import *
from plan import *
from groceries import *
from config import *
from js import VueOnsen, Vue, JSON, eval, document, console, PouchDB, window, URL, Blob, FileReader
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
        self.index = 0
        self.open_side = False

    @property
    def title(self, *args):
        return self.tabs[self.index]['label']

    def update_index(self, index):
        self.index = index

    def open_extra_menu(self):
        self.open_side = not self.open_side

    def load_import(self):
        document.getElementById('import_input').click()

    def import_data(self):
        reader = FileReader.new()
        def remove_rev(document):
            del document['_rev']
            return document
        def on_recipes_loaded(error, result=None):
            if error:
                console.log('error', error)
            store.load_db()
        def on_plans_loaded(error, result=None):
            if error:
                console.log('error', error)
            meal_plans_store.load_plans()
        def on_lists_loaded(error, result=None):
            if error:
                console.log('error', error)
            list_store.load_list()
        def _import_data(*args):
            value = json.loads(reader.result)
            recipes_db.bulkDocs([remove_rev(recipe) for recipe in value['recipes']], on_recipes_loaded)
            plans_db.bulkDocs([remove_rev(plan) for plan in value['plans']], on_plans_loaded)
            groceries_db.bulkDocs([remove_rev(list) for list in value['groceries']], on_lists_loaded)
        file_input = document.getElementById('import_input')
        for file in file_input.files:
            reader.onload = _import_data
            reader.readAsText(file)

    async def export_data(self):
        data = {}
        for db_name in ['recipes', 'plans', 'groceries']:
            all_docs = await PromiseProxy(PouchDB.new(db_name).allDocs({'include_docs': True}))
            data[db_name] = [row.doc for row in all_docs.rows]
        blob = Blob.new([JSON.stringify(data)], {'type': 'application/json'})
        print('blob made', blob)
        url = URL.createObjectURL(blob)
        print('made url', url)
        link = document.createElement('a')
        link.setAttribute('href', url)
        link.setAttribute('download', 'nutrition_export.json')
        document.body.appendChild(link)
        link.click()
        link.remove()
        URL.revokeObjectURL(url)

    def open_configuration(self):
        store.push_page(ConfigurationPage)

    async def reset_caches(self):
        confirm = await PromiseProxy(self['$ons'].notification.confirm('Reset caches?'))
        if confirm:
            console.log('removing serviceworker registrations')
            registrations = await PromiseProxy(window.navigator.serviceWorker.getRegistrations())
            for registration in registrations:
                await PromiseProxy(registration.unregister())
            console.log('removing foods DB')
            await PromiseProxy(foods_db.destroy())
            console.log('removing window caches')
            await PromiseProxy(window.caches.delete('nutrition'))
            console.log('reloading')
            window.location.reload()

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

