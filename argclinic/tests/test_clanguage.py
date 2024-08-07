from argclinic.utils import Config
from argclinic.parser import ParameterKind
from argclinic.cfunction import MODULE_PARAM, CFunction, CParameter
from argclinic.clanguage import (
    escape_string, Output, write_pydoc, write_methoddef, write_function,
    write_impl_prototype)
import unittest


CONFIG = Config()
POSITIONAL_ONLY = ParameterKind.POSITIONAL_ONLY


class Tests(unittest.TestCase):
    maxDiff = 80 * 100

    def test_escape_string(self):
        self.assertEqual(escape_string('abc'),
                         '"abc"')
        self.assertEqual(escape_string('Hello "World".'),
                         '"Hello \\"World\\"."')

    def create_func(self):
        params = [MODULE_PARAM,
                  CParameter('fd', type='int', kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "get_fd", params)
        func.doc = "Documentation.\nMultiline."
        return func

    def test_write_pydoc(self):
        func = self.create_func()
        output = Output()
        write_pydoc(output, func)
        self.assertEqual(output.output,
                         ['PyDoc_STRVAR(get_fd__doc__,',
                          '"get_fd($module, fd, /)\\n"',
                          '"--\\n"',
                          '"\\n"',
                          '"Documentation.\\n"',
                          '"Multiline.");'])

    def test_write_methoddef(self):
        func = self.create_func()
        output = Output()
        write_methoddef(output, func)
        self.assertEqual(output.output,
            ['#define GET_FD_METHODDEF    \\',
             '    {"get_fd", (PyCFunction)get_fd, METH_O, get_fd__doc__},'])

    def test_write_function(self):
        func = self.create_func()
        output = Output()
        write_function(output, func)
        self.assertEqual(output.output,
            ['static PyObject *',
             'get_fd(PyObject *module, PyObject *arg)',
             '{',
             '    PyObject *return_value = NULL;',
             '',
             '    int fd = PyLong_AsInt(arg);',
             '    if (fd == -1 && PyErr_Occurred()) {',
             '        goto exit;',
             '    }',
             '',
             '    return_value = get_fd_impl(module, fd);',
             '',
             'exit:',
             '    return return_value;',
             '}'])

    def test_write_function(self):
        params = [MODULE_PARAM,
                  CParameter('fd', type='int', kind=POSITIONAL_ONLY),
                  CParameter('arg', type='bool', kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "get_fds", params)
        output = Output()
        write_function(output, func)

        self.assertEqual(output.output,
            ['static PyObject *',
             'get_fds(PyObject *module, PyObject *args)',
             '{',
             '    PyObject *return_value = NULL;',
             '    const Py_ssize_t nargs = PyTuple_GET_SIZE(args);',
             '',
             '    if (nargs < 2) {',
             '        PyErr_Format(PyExc_TypeError, "get_fds expected at least 2 arguments, got %zd", nargs);',
             '        goto exit;',
             '    }',
             '',
             '    if (nargs > 2) {',
             '        PyErr_Format(PyExc_TypeError, "get_fds expected at most 2 arguments, got %zd", nargs);',
             '        goto exit;',
             '    }',
             '',
             '    int fd = PyLong_AsInt(PyTuple_GET_ITEM(args, 0));',
             '    if (fd == -1 && PyErr_Occurred()) {',
             '        goto exit;',
             '    }',
             '',
             '    bool arg = PyObject_IsTrue(PyTuple_GET_ITEM(args, 1));',
             '    if (arg == -1 && PyErr_Occurred()) {',
             '        goto exit;',
             '    }',
             '',
             '    return_value = get_fds_impl(module, fd, arg);',
             '',
             'exit:',
             '    return return_value;',
             '}'])

    def test_write_impl_prototype(self):
        # 1 param
        params = [MODULE_PARAM,
                  CParameter('fd', type='int', kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "get_fds", params)
        output = Output()
        write_impl_prototype(output, func)
        self.assertEqual(output.output,
            ['static PyObject *',
             'get_fds_impl(PyObject *module, int fd);'])

        # 2 params
        params = [MODULE_PARAM,
                  CParameter('fd', type='int', kind=POSITIONAL_ONLY),
                  CParameter('arg', type='bool', kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "get_fds", params)
        output = Output()
        write_impl_prototype(output, func)
        self.assertEqual(output.output,
            ['static PyObject *',
             'get_fds_impl(PyObject *module, int fd, bool arg);'])


if __name__ == "__main__":
    unittest.main()
