#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import inspect
import os
import traceback
import cgi
import collections
import functools

from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap


def format_name(str_):
    str_ = str_.replace('_', ' ')
    return str_.capitalize()


def format_doc(docstring):
    text = cgi.escape(docstring, quote=True)
    text = re.split('(?:\r|\n|\r\n)[ \t]*(?:\r|\n|\r\n)', text)
    return '<p>' + '</p><p>'.join(text) + '</p>'


def escape_html(text):
    text = cgi.escape(text, quote=True)
    text = text.replace(os.linesep, '<br/>')
    return text.replace(' ', '&nbsp')


class WebFunction(object):
    """A function to be published on the web UI"""

    def __init__(self, func, name, args=None, print_name=''):
        super(WebFunction, self).__init__()
        self.func = func
        self.name = name
        self.args = args or []
        self.help_message = format_doc(func.__doc__)
        self._print_name = print_name

    def arg_names(self):
        return [arg.name for arg in self.args]

    @property
    def print_name(self):
        return self._print_name or format_name(self.name)


class Argument(object):
    """Describe one argument of a function"""

    def __init__(self, name, type_=None, default='', help_='', print_name=''):
        super(Argument, self).__init__()
        self.name = name
        self.type = type_
        self.default = default
        self.help = help_
        self._print_name = print_name

    @property
    def print_name(self):
        return self._print_name or format_name(self.name)


class WebFunctionWorker(object):
    """One instance of the function execution"""
    def __init__(self, webfunction):
        self.webfunction = webfunction
        self.kwargs = None

    def set_args(self, **kwargs):
        self.kwargs = {}
        for arg in self.webfunction.args:
            argvalue = kwargs[arg.name]
            if arg.type:
                argvalue = arg.type(argvalue)
            self.kwargs[arg.name] = argvalue

    def run(self):
        return self.webfunction.func(**self.kwargs)


class TravelMug(object):
    """Create a web interface for a set of python functions.

    Example of use
    ==============
    >>> mug = travelmug.TravelMug()
    >>> @mug.add
    ... def my_func(arg1, arg2):
    ....... return arg1 + arg2
    >>> mug.run()

    """

    def __init__(self):
        self.flask_app = Flask(__name__)
        Bootstrap(self.flask_app)
        self.flask_app.config['BOOTSTRAP_SERVE_LOCAL'] = True
        self._functions = collections.OrderedDict()

    def _add(self, func, print_name='', argspec=None):
        fname = func.__name__
        argspec = argspec or {}
        args = [Argument(arg, **argspec.get(arg, {}))
                 for arg in inspect.getargspec(func).args]
        self._functions[fname] = WebFunction(func, fname, args, print_name)
        return func

    def add(self, func=None, print_name=''):
        """Decorator to add a function to the UI

        Optional decorator arguments
        ============================
        print_name: string used to name the function on the UI
        """
        if func is None:
            if print_name:
                return functools.partial(self.add, print_name=print_name)
        elif callable(func):
            # add was called without self.argspec
            return self._add(func, print_name)
        elif len(func) == 2:
            # we're receiving a tuple from self.argspec instead of a func
            return self._add(func[0], print_name, argspec=func[1])
        else:
            raise ValueError("Unsupported type for func %d" % func)

    def argspec(self, argname, **kwargs):
        """Specify arguments' attributes

        First argument must be the argument's name

        Optional keyword arguments
        ==========================
        print_name: string used to name the argument on the UI
        type_: type of the argument (must be callable)

        Example of use
        ==============
        >>> @mug.add
        ... @mug.argspec('value', print_name="Integer to hexadecimal")
        ... @mug.argspec('value', type_=int)
        ... def convert_to_hex(value):
        ...    return hex(value)
        """
        spec = {argname: kwargs}

        def wrapper(arg):
            if callable(arg):
                func = arg
            elif len(arg) == 2:
                func = arg[0]
                for key, value in arg[1].items():
                    if key in spec:
                        spec[key].update(value)
                    else:
                        spec[key] = value
            return (func, spec)
        return wrapper

    def run(self, debug=False):
        """Launch the web server

        Attributes
        ==========
        debug: active Flask's debug mode
        """
        @self.flask_app.route('/_call')
        def _call():
            fname = request.args.get('fname')
            wf = self._functions[fname]
            args = {}
            for argname in wf.arg_names():
                args[argname] = request.args.get(argname)

            worker = WebFunctionWorker(wf)
            try:
                worker.set_args(**args)
            except Exception as e:
                error_msg = '<p><strong>Type Error</strong><br/>'
                error_msg += escape_html(str(e))
                error_msg += '</p>'
                return jsonify(success=False, error_msg=error_msg)

            try:
                r = worker.run()
            except Exception as e:
                print (traceback.format_exc())
                error_msg = '<p><strong>'
                error_msg += 'The function raised the following exception:'
                error_msg += '</strong><br/>'
                if debug:
                    error_msg += escape_html(traceback.format_exc())
                else:
                    error_msg += escape_html(str(e))
                error_msg += '</p>'

                return jsonify(success=False, error_msg=error_msg)
            else:
                return jsonify(success=True, return_html=str(r))

        @self.flask_app.route('/')
        def index():
            return render_template(
                'index.html',
                title='Travelmug',
                page_title='Travelmug',
                functions=self._functions,
                render_template=render_template)
        self.flask_app.run(debug=debug)
