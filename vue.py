import asyncio
import time
from inspect import ismethod, isdatadescriptor, isfunction, ismemberdescriptor
from itertools import chain
from collections.abc import MutableSequence, MutableMapping

from js import Vue, console, Object, eval, Promise, window


class JavascriptEventLoop(asyncio.AbstractEventLoop):
    def get_debug(self):
        return False

    def call_soon(self, callback, *args, context=None):
        handle = asyncio.Handle(callback, args, self, context=context)
        window.setTimeout(handle._run)
        return handle

    def call_soon_threadsafe(self, callback, *args, context=None):
        return self.call_soon(callback, *args, context=context)

    def call_later(self, when, callback, *args, context=None):
        handle = asyncio.Handle(callback, args, self, context=context)
        window.setTimeout(handle._run, when * 1000.0)
        return handle

    def call_at(self, when, callback, *args, context=None):
        delay = when - self.time()
        self.call_later(delay, callback, *args, context=context)

    def create_task(self, coro):
        return asyncio.Task(coro, loop=self)

    def create_future(self):
        return asyncio.Future(loop=self)

    def is_running(self):
        return True

    def time(self):
        return time.monotonic()


loop = JavascriptEventLoop()
asyncio.events._set_running_loop(loop)
asyncio.set_event_loop(loop)

# adapt a JS promise to a Python asyncio.Future
class PromiseProxy:
    def __init__(self, promise):
        self.future = loop.create_future()
        promise.then(self.resolve, self.fail)

    def __await__(self):
        return self.future.__await__()

    def resolve(self, result):
        self.future.set_result(result)

    def fail(self, failure):
        self.future.set_exception(failure)


class JsFn:
    def __init__(self, method, this=None, *args):
        self._method = method
        #self.this = ObjectProxy(this)
        self.this = this
        self.args = args

    def call(self, this, *args):  # todo handle args to coroutine?
        def _promise_func(resolve, reject):
            task = asyncio.create_task(self._method(this, *chain(self.args, args)))
            def done(future):
                exception = task.exception()
                if task.exception():
                    reject(exception)
                else:
                    resolve(task.result())
            task.add_done_callback(done)
        if asyncio.iscoroutinefunction(self._method):
            return Promise.new(_promise_func)
        return self._method(this, *chain(self.args, args))
        #return self._method(ObjectProxy(this), *chain(self.args, args))

    def apply(self, args):
        return self.call(*args)

    def __call__(self, *args):
        return self.call(self.this, *args)

    def bind(self, this, *args):
        return JsFn(self._method, this, *args)


def vue_class(cls):
    def data(this, *args):
        new_instance = cls()
        return new_instance.__dict__

    options = {}
    for key, value in cls.options.items():
        options[key] = value

    methods = {}
    computed = {}
    for name in filter(lambda name: not name.startswith('_'), dir(cls)):  # TODO filter out startswith _
        value = getattr(cls, name)
        if isfunction(value):
            methods[name] = JsFn(value)
        elif isdatadescriptor(value):
            computed[name] = JsFn(value.fget)

    options['data'] = JsFn(data)
    options['methods'] = methods
    options['computed'] = computed

    return options


def proxy(value):
    if hasattr(value, 'push'):  # assume it's an array
        return ArrayProxy(value)
    elif hasattr(value, 'typeof'):
        return MappingProxy(value)
    else:
        return value


class MappingProxy(MutableMapping):
    def __init__(self, value):
        self._value = value

    def __getitem__(self, key):
        return proxy(self._value[key])

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        del self._value[key]

    def __iter__(self):
        for key in Object.keys(self._value):
            yield key

    def __len__(self):
        return len(Object.keys(self._value))


class ObjectProxy:
    def __init__(self, value):
        self._value = value

    def __getattribute__(self, key):
        this = object.__getattribute__(self, '_value')
        if key == '_value':
            return this
        else:
            return proxy(getattr(this, key))

    def __setattr__(self, key, value):
        if key == '_value':
            object.__setattr__(self, '_value', value)
        else:
            setattr(object.__getattribute__(self, '_value'), key, value)


class ArrayProxy(MutableSequence):
    def __init__(self, value):
        self.value = value

    def __getitem__(self, key):
        return proxy(self.value[key])

    def __setitem__(self, key, value):
        self.value[key] = value

    def __delitem__(self, key):
        self.value.splice(key, 1)

    def __len__(self):
        return len(self.value)

    def insert(self, index, item):
        self.value.splice(index, 0, item)


class VueStore:
    def __init__(self):
        self.state = Object.new()
