import sys

from js import python_files, console

from importlib.abc import MetaPathFinder, SourceLoader

python_files_paths = set(path for path in dir(python_files) if path.endswith('.py'))

def module_urls(name, paths=None):
    base = '.'
    if paths:
        base = paths[0]
    return [f'{base}/{name}.py', f'{base}/{name}/__init__.py']


class ModulePrefetchLoader(SourceLoader, MetaPathFinder):
    def __init__(self):
        self.data_cache = {}
        self.url_cache = {}
        
    def get_data(self, path):
        return self.data_cache[path].encode('utf-8')

    def get_filename(self, fullname):
        return self.url_cache[fullname]

    def match(self, url):
        if url in python_files_paths:
            return url

    def find_module(self, fullname, path=None):
        last_component = fullname.split('.')[-1]
        if fullname in self.url_cache:
            if self.url_cache[fullname] is not None:
                return self
            else:
                return None

        result_data = None
        result_url = None
        for url in module_urls(last_component, paths=path):
            matching_key = self.match(url)
            if matching_key:
                result_data = python_files[matching_key]
                result_url = url
                break
        self.url_cache[fullname] = result_url
        if result_url is not None:
            self.data_cache[result_url] = result_data
            return self


sys.meta_path.append(ModulePrefetchLoader())
