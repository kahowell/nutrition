from vue import *
from store import store, meal_plans_store
from groceries import list_store
from js import localStorage, JSON, PouchDB, eval


def load_config():
    config = None
    config_str = localStorage.getItem('config')
    if config_str:
        config = JSON.parse(config_str)
    config = config or {
        'use_tls': True,
        'couch_host': '',
        'couch_port': '',
        'couch_username': '',
        'couch_password': '',
        'sync_enabled': True,
    }
    return config

def save_config(config):
    localStorage.setItem('config', JSON.stringify(config))
    sync.configure(config)


def update_recipes_callback(*args):
    console.log('recips_updated!')
    store.load_db()

def update_plans_callback(*args):
    console.log('plans updated!')
    meal_plans_store.load_plans()

def update_groceries_callback(*args):
    console.log('groceries updated!')
    list_store.load_list()


class Sync:
    def __init__(self, config):
        self.syncs = []
        self.configure(config)

    def configure(self, config):
        self.stop()
        if not config['couch_host'] or not config['couch_port']:
            return
        if not config['sync_enabled']:
            return
        couch_location = f"{config['couch_host']}:{config['couch_port']}"
        creds = ''
        if config['couch_username'] and config['couch_password']:
            creds = f"{config['couch_username']}:{config['couch_password']}@"
        protocol = 'https' if config['use_tls'] else 'http'
        couch_prefix = f'{protocol}://{creds}{couch_location}'
        for db in ['groceries', 'recipes', 'plans']:
            url = f'{couch_prefix}/{db}'
            # XXX working around some pyodide js bridge weirdness
            sync = eval(f"sync = PouchDB.sync('{db}', '{url}', {{live:true,retry:true}})")
            eval(f"update_{db}_callback = pyodide.runPython('from config import update_{db}_callback; update_{db}_callback')")
            eval(f"sync.on('change', () => update_{db}_callback())")
            self.syncs.append(sync)

        console.log(self.syncs)

    def stop(self):
        for sync in self.syncs:
            sync.cancel()
        self.syncs = []

config = load_config()
sync = Sync(config)


@vue_class
class ConfigurationPage:
    options = {'template': '#configuration-page'}
    def __init__(self):
        self.config = config

    def save_config(self):
        save_config(config)
        store.pop_page()