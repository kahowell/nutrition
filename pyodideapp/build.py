import base64
import hashlib
import os
import shutil
import subprocess

import requests
from PIL import Image as _Image
from jinja2 import Environment, FileSystemLoader

PYODIDE_URL = 'https://github.com/iodide-project/pyodide/releases/download/0.14.3/pyodide-build-0.14.3.tar.bz2'
PYODIDE_SHA256 = '6ac6020973def85278877fac1433bdd878c89dee6844f29fd57849875acf122e'
CACHE_PATH = os.path.join('build', 'cache')
WWW_PATH = os.path.join('build', 'www')
CORDOVA_PATH = os.path.join('build', 'cordova')
FILE_HACK_LIST = [
    'pyodide.asm.wasm',
    'pyodide.asm.data',
    'packages.json',
]

def sh(command):
    print(f'> {command}')
    subprocess.check_call(command, shell=True)


class SourceFile:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def build(self, root, copy=False, **kwargs):
        destination = os.path.join(root, self.destination)
        if copy and (not os.path.exists(destination) or os.path.getmtime(self.source) > os.path.getmtime(destination)):
            shutil.copy(self.source, destination)
        if not copy and not os.path.exists(destination):
            os.symlink(os.path.abspath(self.source), destination)

    def __repr__(self):
        return f"<File source='{self.source}' destination='{self.destination}'>"


class Template:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def build(self, root, **kwargs):
        destination = os.path.join(root, self.destination)
        env = Environment(loader=FileSystemLoader(os.path.dirname(self.source)))
        template = env.get_template(os.path.basename(self.source))
        with open(destination, 'w') as output:
            output.write(template.render(**kwargs))

    def __repr__(self):
        return f"<Template source='{self.source}'>"


class Directory:
    def __init__(self, path):
        self.path = path

    def build(self, root, **kwargs):
        path = os.path.join(root, self.path)
        if not os.path.exists(path):
            os.makedirs(path)

    def __repr__(self):
        return f"<Directory path='{self.path}'>"


class SourceDirectory:
    def __init__(self, path):
        self.path = path 
        self.sources = []
        for root, dirs, files in os.walk(self.path):
            for name in dirs:
                path = os.path.join(root, name)
                self.sources.append(Directory(name))
            for name in files:
                path = os.path.join(root, name)
                destination = name.rstrip('.j2')
                if path.endswith('.j2'):
                    self.sources.append(Template(path, destination=destination))
                else:
                    self.sources.append(SourceFile(path, destination=destination))

    def build(self, root, **kwargs):
        for source in self.sources:
            source.build(root=root, **kwargs)

    def __repr__(self):
        return f"<SourceDirectory path='{self.path}'>"


class Url:
    def __init__(self, url, sha256sum, filename=None):
        self.url = url
        self.sha256sum = sha256sum
        self.filename = filename

    def build(self, root, copy=False, **kwargs):
        effective_filename = self.filename or os.path.basename(self.url)
        destination = os.path.join(root, effective_filename)
        cache_destination = os.path.join(CACHE_PATH, effective_filename)
        if os.path.exists(destination) and destination != cache_destination:
            return destination
        checksum = hashlib.sha256()
        if not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        if not os.path.exists(os.path.dirname(cache_destination)):
            os.makedirs(os.path.dirname(cache_destination))
        if not os.path.exists(cache_destination):
            print(f'Downloading {self.url}...')
            with open(cache_destination, 'wb') as output:
                r = requests.get(self.url)
                if r.status_code != 200:
                    raise IOError(f'Got HTTP {r.status_code} when trying to download file')
                for chunk in r.iter_content(2048):
                    checksum.update(chunk)
                    output.write(chunk)
        else:
            with open(cache_destination, 'rb') as cached:
                while True:
                    chunk = cached.read(2048)
                    if not chunk:
                        break
                    checksum.update(chunk)
        actual = checksum.hexdigest()
        if actual != self.sha256sum:
            raise SystemError(f'for {effective_filename} expected sha256sum of {self.sha256sum}, got {actual} instead!')
        if cache_destination != destination:
            if copy:
                shutil.copy(cache_destination, destination)
            else:
                os.symlink(os.path.abspath(cache_destination), destination)
        return destination

    def __repr__(self):
        return f"<Url url='self.url' filename='{self.filename}'>"


class Archive:
    def __init__(self, source, files=[]):
        self.source = source
        self.files = files

    def build(self, root, copy=False, **kwargs):
        archive_path = self.source.build(root=CACHE_PATH, **kwargs)
        sha256sum = hashlib.sha256()
        sha256sum.update(archive_path.encode('utf-8'))
        cache_destination = os.path.join(CACHE_PATH, sha256sum.hexdigest())
        if not os.path.exists(cache_destination):
            os.makedirs(cache_destination)
            shutil.unpack_archive(archive_path, cache_destination)

        for file in self.files:  # TODO handle self.files=None, directories, globs
            source = os.path.join(cache_destination, file)
            destination = os.path.join(root, file)
            if not os.path.exists(destination):
                if copy:
                    shutil.copy(source, destination)
                else:
                    os.symlink(os.path.abspath(source), destination)
        return cache_destination

    def __repr__(self):
        return f"<Archive source='{self.source}' #files='{len(self.files)}'>"


class Image:
    def __init__(self, source, size, filename=None):
        self.source = source
        self.size = size
        self.filename = filename or os.path.basename(source)

    def build(self, root, **kwargs):
        destination = os.path.join(root, self.filename)
        if os.path.exists(destination):
            return
        print(f'Resizing {self.source.url} into {self.filename} ({self.size})')
        path = self.source.build(root=CACHE_PATH, **kwargs)
        image = _Image.open(path)
        image = image.resize(self.size)
        image.save(destination)


class PyodideRelease:
    def __init__(self, pyodide_reqs, url=PYODIDE_URL, sha256sum=PYODIDE_SHA256, initial_memory=5242880):
        self.pyodide_reqs = pyodide_reqs
        self.files = [
            'pyodide.js',
            'pyodide.asm.wasm',
            'pyodide.asm.data.js',
            'pyodide.asm.data',
            'pyodide.asm.js',
            'packages.json',
        ] + self.pyodide_reqs
        self.source_archive = Archive(Url(url, sha256sum=sha256sum), files=self.files)

    def build(self, root, copy=False, **kwargs):
        cache_destination = os.path.join(CACHE_PATH, 'pyodide')
        if not os.path.exists(cache_destination):
            os.makedirs(cache_destination)
        self.source_archive.build(root=cache_destination)
        for file in self.files:
            source = os.path.join(cache_destination, file)
            destination = os.path.join(root, file)
            if not os.path.exists(destination):
                if copy:
                    shutil.copy(source, destination)
                else:
                    os.symlink(os.path.abspath(source), destination)


class App:
    def __init__(self, id, name, sources, initial_memory=5242880):
        self.id = id
        self.name = name
        self.pyodide_reqs = detect_pyodide_python_requirements()
        self.sources = sources + [
            PyodideRelease(pyodide_reqs=self.pyodide_reqs, initial_memory=initial_memory),
            SourceFile(os.path.join('pyodideapp', 'bootstrap.js'), 'bootstrap.js'),
            SourceFile(os.path.join('pyodideapp', 'httpimport.py'), 'httpimport.py'),
            SourceFile(os.path.join('pyodideapp', 'sw.js'), 'sw.js'),
            SourceFile(os.path.join('pyodideapp', 'fetchimport.py'), 'fetchimport.py'),
         ]

    def build(self, root, enable_file_hack=False, copy=False, **kwargs):
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)
        if not os.path.exists(root):
            os.makedirs(root)
        for source in self.sources:
            source.build(root=root, pyodide_packages=set(package.rstrip('.data').rstrip('.js') for package in self.pyodide_reqs), copy=copy, **kwargs)
        python_requirements = subprocess.check_output('pipenv lock -r', shell=True).decode('utf-8').split('\n')
        pyodide_provided = set(file.rstrip('.data').rstrip('.js').lower() for file in self.pyodide_reqs)
        python_requirements = filter(lambda item: item.split('==')[0].lower() not in pyodide_provided, python_requirements)
        python_requirements = '\n'.join(python_requirements)
        requirements_path = os.path.join(CACHE_PATH, 'requirements.txt')
        with open(requirements_path, 'w') as output:
            output.write(python_requirements)
        sh(f'pipenv run pip install --no-deps -r {requirements_path} --target {root}')
        config = Template(os.path.join('pyodideapp', 'pyodide_config.js.j2'), 'pyodide_config.js')
        template_args = dict(kwargs)
        template_args['enable_file_hack'] = enable_file_hack  # TODO necessary?
        # get list of files in the build root

        www_files =  [os.path.relpath(os.path.join(root2, name), root) for root2, _, files in os.walk(root) for name in files]
        template_args['www_files'] = www_files
        config.build(root, **template_args)
        if enable_file_hack:
            file_hack_files = []
            file_hack_up_to_date = True
            file_hack_mtime = None
            if os.path.exists(os.path.join(root, 'file_hack.js')):
                file_hack_mtime = os.path.getmtime(os.path.join(root, 'file_hack.js'))
            else:
                file_hack_up_to_date = False
            for root2, dirs, files in os.walk(root):
                for name in files:
                    if name.endswith('.py') or name in FILE_HACK_LIST or name in self.pyodide_reqs:
                        path = os.path.join(root2, name)
                        file_hack_files.append({
                            'name': f'./{name}',
                            'path': path,
                        })
                        if file_hack_mtime is not None and os.path.getmtime(path) > file_hack_mtime:
                            file_hack_up_to_date = False
            if not file_hack_up_to_date:
                print('Writing file hack. This will take a bit...')
                for info in file_hack_files:
                    info['contents'] = base64.b64encode(open(info['path'], 'rb').read()).decode('utf-8')
                loader = FileSystemLoader(searchpath="pyodideapp")
                env = Environment(loader=loader)

                template = env.get_template('file_hack.js.j2')
                with open(os.path.join(root, 'file_hack.js'), 'w') as output:
                    output.write(template.render(files=file_hack_files))

    def build_web(self, **kwargs):
        self.build(root=WWW_PATH)

    def build_cordova(self, electron=False, android=False, ios=False, **kwargs):
        platforms = []
        if electron:
            platforms.append('electron')
        if android:
            platforms.append('android')
        if ios:
            platforms.append('ios')
        print(f"Building via cordova for {', '.join(platforms)}")
        self.build(root=os.path.join(CORDOVA_PATH, 'www'), enable_file_hack=True)
        os.chdir(CORDOVA_PATH)
        if not os.path.exists('app'):
            sh(f'cordova --no-telemetry create app {self.id} {self.name}')
            shutil.rmtree(os.path.join('app', 'www'))
            os.symlink(os.path.abspath('www'), os.path.join('app', 'www'))
        os.chdir('app')
        for platform in platforms:
            if not os.path.exists(os.path.join('platforms', platform)):
                sh(f'cordova --no-telemetry platform add {platform}')
                sh(f'npm install cordova-{platform} -D')
        sh('cordova --no-telemetry build')

    def main(self):
        import argparse
        parser = argparse.ArgumentParser(description="Build a pyodide-based app.")
        parser.set_defaults(func=lambda *args, **kwargs: parser.print_usage())
        subparsers = parser.add_subparsers(description='commands')
        web_parser = subparsers.add_parser('web', help='Build a standard static web app')
        web_parser.set_defaults(func=self.build_web)
        cordova_parser = subparsers.add_parser('cordova', help='Build a cordova-based mobile or electron app')
        cordova_parser.add_argument('--electron', action='store_true', help='include an electron app build')
        cordova_parser.add_argument('--android', action='store_true', help='include an android app build')
        cordova_parser.add_argument('--ios', action='store_true', help='include an ios app build')
        cordova_parser.set_defaults(func=self.build_cordova)
        args = parser.parse_args()
        args.func(**vars(args))

    def serve(self):
        import mimetypes

        from flask import Flask

        self.build_web()
        mimetypes.add_type('application/wasm', '.wasm')
        app = Flask('app', static_folder='build/www', static_url_path='/')

        @app.route('/')
        def root():
            return app.send_static_file('index.html')

        app.run()

    def __repr__(self):
        return f"<App #sources='{len(self.sources)}'>"


def detect_pyodide_python_requirements():
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    pyodide_path = Archive(Url(PYODIDE_URL, PYODIDE_SHA256), files=[]).build(root=WWW_PATH)  # download and extract pyodide
    pyodide_provided = set([name.lower().rstrip('.data') for name in os.listdir(pyodide_path) if name.endswith('.data')])
    python_requirements = subprocess.check_output('pipenv lock -r', shell=True).decode('utf-8').split('\n')
    pyodide_fulfilled = list(filter(lambda item: not item.startswith('-') and item in pyodide_provided, map(lambda item: item.split('==')[0], python_requirements)))
    return [path for path in os.listdir(pyodide_path) if path.rstrip('.js').rstrip('.data').lower() in pyodide_fulfilled]
