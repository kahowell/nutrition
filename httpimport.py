import sys

from js import console
try:
    from js import XMLHttpRequestOverride as XMLHttpRequest
except ImportError:
    from js import XMLHttpRequest

from importlib.abc import MetaPathFinder, SourceLoader


def module_urls(name, paths=None):
    base = '.'
    if paths:
        base = paths[0]
    return [f'{base}/{name}.py', f'{base}/{name}/__init__.py']


class ModuleHTTPLoader(SourceLoader, MetaPathFinder):
    def __init__(self):
        self.data_cache = {}
        self.url_cache = {}
        
    def get_data(self, path):
        return self.data_cache[path]

    def get_filename(self, fullname):
        return self.url_cache[fullname]

    def find_module(self, fullname, path=None):
        console.debug('finding', fullname, path)
        last_component = fullname.split('.')[-1]
        if fullname in self.url_cache:
            if self.url_cache[fullname] is not None:
                return self
            else:
                return None

        result_data = None
        result_url = None
        for url in module_urls(last_component, paths=path):
            request = XMLHttpRequest.new()
            request.open('GET', url, False)
            request.send(None)
            if request.status == 200:
                result_data = request.responseText.encode('utf-8')
                result_url = url
                break
        self.url_cache[fullname] = result_url
        if result_url is not None:
            self.data_cache[result_url] = result_data
            return self


sys.meta_path.append(ModuleHTTPLoader())
