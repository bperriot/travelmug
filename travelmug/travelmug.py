#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import inspect
import os
import traceback
import cgi
import collections
import functools
import weakref

from flask import Flask, jsonify, render_template, request, Response
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


class FunctionSpecification(object):
    """Store the argument or return value FunctionSpecification

    Used only to resolve the chain of decorators.
    """

    def __init__(self, func):
        self.func = func
        self.argspec = {}
        self.retspec = {}

    def add(self, type_, name, kwargs):
        if type_ == 'arg':
            dct = self.argspec.setdefault(name, {})
        elif type_ == 'return':
            dct = self.retspec
        else:
            raise ValueError("Unsupported type_: %s" % type_)
        dct.update(kwargs)

    @staticmethod
    def wrapper(type_, name, kwargs):
        def wrapper(arg):
            if isinstance(arg, FunctionSpecification):
                spec = arg
            else:  # the wrapper received the decorated function
                spec = FunctionSpecification(arg)
            spec.add(type_, name, kwargs)
            return spec
        return wrapper


class WebFunction(object):
    """A function to be published on the web UI"""

    def __init__(self, func, name, args, return_value, print_name=''):
        super(WebFunction, self).__init__()
        self.func = func
        self.name = name
        self.args = args or []
        for arg in self.args:
            if arg.parent is not None:
                raise ValueError(
                    "The Argument is already associated to another WebFunction (%s)"
                    % arg.parent.name)
            arg.parent = weakref.proxy(self)
        self.return_value = return_value
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
        self.parent = None
        self.type = type_
        self.default = default
        self.help = help_
        self._print_name = print_name

    @property
    def print_name(self):
        return self._print_name or format_name(self.name)

    def input_html(self):
        if self.type == 'file':
            return render_template("file_input.html", webfunc=self.parent, arg=self)
        else:
            return render_template("string_input.html", arg=self)


class ReturnValue(object):
    """Describe the way the return value will be returned"""

    def __init__(self, download=False):
        self.download = download


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
                if callable(arg.type):
                    argvalue = arg.type(argvalue)
                elif arg.type == 'file':
                    argvalue = argvalue
                else:
                    raise ValueError("Unsupported value for arg type (%s)" %
                                     str(arg.type))

            self.kwargs[arg.name] = argvalue

    def run(self):
        r = self.webfunction.func(**self.kwargs)
        if self.webfunction.return_value.download:
            return Response(
                str(r),
                mimetype="text",
                headers={"Content-disposition":
                         "attachment; filename=%s.txt" %
                         self.webfunction.name})
        else:
            return jsonify(success=True, return_html=str(r))


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

    def _add(self, funcspec, print_name=''):
        fname = funcspec.func.__name__
        args = [Argument(argname, **funcspec.argspec.get(argname, {}))
                for argname in inspect.getargspec(funcspec.func).args]
        self._functions[fname] = WebFunction(funcspec.func, fname, args,
                                             ReturnValue(**funcspec.retspec),
                                             print_name)
        return funcspec.func

    def add(self, arg=None, print_name=''):
        """Decorator to add a function to the UI

        It must always be placed before the specification decorator

        Optional decorator arguments
        ============================
        print_name: string used to name the function on the UI
        """
        if arg is None:
            if print_name:
                return functools.partial(self.add, print_name=print_name)
        elif isinstance(arg, FunctionSpecification):
            return self._add(arg, print_name)
        elif callable(arg):
            # add was called without any specification decorator
            return self._add(FunctionSpecification(arg), print_name)
        else:
            raise ValueError("Unsupported type for arg %d" % arg)

    def argspec(self, argname, **kwargs):
        """Specify arguments' attributes

        First argument must be the argument's name

        Optional keyword arguments
        ==========================
        print_name: string used to name the argument on the UI
        type_: type of the argument. Can be callable or 'file'

        Example of use
        ==============
        >>> @mug.add
        ... @mug.argspec('value', print_name="Integer to hexadecimal")
        ... @mug.argspec('value', type_=int)
        ... def convert_to_hex(value):
        ...    return hex(value)
        """
        return FunctionSpecification.wrapper("arg", argname, kwargs)

    def retspec(self, **kwargs):
        """Specify the way of returning the value

        Optional keyword arguments
        ==========================
        download: set to True to download a file instead of printing the value

        Example of use
        ==============
        >>> @mug.add
        ... @mug.retspec(download=True)
        ... def base_gitignore():
        ...     return "*.pyc\n*.egg-info"
        """
        return FunctionSpecification.wrapper("return", '', kwargs)

    def run(self, debug=False):
        """Launch the web server

        Attributes
        ==========
        debug: active Flask's debug mode
        """
        @self.flask_app.route('/_call', methods=['GET', 'POST'])
        def _call():
            fname = request.form.get('_fname')
            wf = self._functions[fname]
            args = {}
            for arg in wf.args:
                if arg.type == 'file':
                    args[arg.name] = request.files.get(arg.name)
                else:
                    args[arg.name] = request.form.get(arg.name)

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
                print(traceback.format_exc())
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
                return r

        @self.flask_app.route('/')
        def index():
            return render_template(
                'index.html',
                title='Travelmug',
                page_title='Travelmug',
                functions=self._functions,
                render_template=render_template)
        self.flask_app.run(debug=debug)
