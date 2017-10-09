#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import inspect

from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap


def format_name(str_):
    str_ = str_.replace('_', ' ')
    return str_.capitalize()


def format_doc(docstring):
    text = re.split('(?:\r|\n|\r\n)[ \t]*(?:\r|\n|\r\n)', docstring)
    return '<p>' + '</p><p>'.join(text) + '</p>'


class WebFunction(object):
    """A function to be published on the web UI"""
    def __init__(self, func, name, args=[], print_name=''):
        super(WebFunction, self).__init__()
        self.func = func
        self.name = name
        self.args = args
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


class TravelMug(object):
    """Create a web interface for a set of python functions.

    Example of use
    ==============
    >>> mug = travelmug.TravelMug()
    >>> @mug.add
    >>> def my_func(arg1, arg2):
    >>> ... return arg1 + arg2
    >>> mug.run()

    """
    def __init__(self):
        self.flask_app = Flask(__name__)
        Bootstrap(self.flask_app)
        self.flask_app.config['BOOTSTRAP_SERVE_LOCAL'] = True
        self._functions = {}

    def add(self, func):
        """Decorator to add a function to the UI"""
        fname = func.__name__
        args = [Argument(arg) for arg in inspect.getargspec(func).args]

        self._functions[fname] = (WebFunction(func, fname, args))
        return func

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
            for arg in wf.arg_names():
                args[arg] = request.args.get(arg)

            return jsonify(return_html=str(wf.func(**args)))

        @self.flask_app.route('/')
        def index():
            return render_template(
                'index.html',
                title='Travelmug',
                page_title='Travelmug',
                functions=self._functions,
                render_template=render_template)
        self.flask_app.run(debug=debug)
