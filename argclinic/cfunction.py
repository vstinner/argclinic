from argclinic.utils import Config, Output
from argclinic.parser import ParameterKind, EMPTY


class CParameter:
    def __init__(self, name: str, *, type: str,
                 kind: ParameterKind, default: str = EMPTY) -> None:
        self.name = name
        self.type = type
        if type == "module":
            self.ctype = "PyObject*"
        else:
            self.ctype = type
        self.kind = kind
        self.default = default

    def can_use_meth_o(self) -> bool:
        return (self.kind == ParameterKind.POSITIONAL_ONLY)

    def is_module(self):
        return (self is MODULE_PARAM)

    def is_optional(self):
        return (self.default is not EMPTY)


MODULE_PARAM = CParameter("module", type="module",
                          kind=ParameterKind.POSITIONAL_ONLY)


class CFunction:
    def __init__(self, config: Config, name: str, params: list[CParameter],
                 *, doc: str = "") -> None:
        self.name = name
        self.func_name = name.replace(".", "_")
        self.impl_name = f"{self.func_name}_impl"
        self.doc_varname = f"{self.func_name}__doc__"
        self.params = params
        self.doc = doc
        self.calling_convention = CallingConvention._get_calling_convention(self)

    def get_min_max_args(self):
        min_nargs = 0
        max_nargs = 0
        for param in self.params:
            if param.is_module():
                continue
            if not param.is_optional():
                min_nargs += 1
            max_nargs += 1
        return (min_nargs, max_nargs)


class CallingConvention:
    def __init__(self, name: str, func: CFunction) -> None:
        self.name = name
        self.func = func

    def __repr__(self) -> str:
        return f"<CallingConvention {self.name}>"

    def get_arg_value(self, index) -> str:
        if self.name == "METH_NOARGS":
            raise Exception("METH_NOARGS has no arguments")
        elif self.name == "METH_O":
            if index > 0:
                raise Exception("METH_O has a single argument")
            return 'arg'
        else:  # METH_VARARGS
            return f'PyTuple_GET_ITEM(args, {index})'

    def write_prototype(self, output: Output) -> None:
        name = self.func.func_name
        first_arg = self.func.params[0].name

        output.write('static PyObject *')
        if self.name == "METH_NOARGS":
            line = f'{name}(PyObject *{first_arg}, PyObject *Py_UNUSED(ignored))'
        elif self.name == "METH_O":
            line = f'{name}(PyObject *{first_arg}, PyObject *arg)'
        else:  # METH_VARARGS
            line = f'{name}(PyObject *{first_arg}, PyObject *args)'
        output.write(line)

    def get_nargs(self) -> str:
        if self.name == "METH_VARARGS":
            return 'nargs'
        else:
            raise ValueError("not implemented")

    def write_check_nargs(self, output: Output) -> None:
        if self.name != "METH_VARARGS":
            # nothing to check
            return

        name = self.func.name
        min_args, max_args = self.func.get_min_max_args()

        output.write(f'if (nargs < {min_args}) {{')
        output.write(f'PyErr_Format(PyExc_TypeError, '
                     f'"{name} expected at least {min_args} arguments, '
                     f'got %zd", nargs);', 1)
        output.write('goto exit;', 1)
        output.write('}')
        output.write()

        output.write(f'if (nargs > {max_args}) {{')
        output.write(f'PyErr_Format(PyExc_TypeError, '
                     f'"{name} expected at most {max_args} arguments, '
                     f'got %zd", nargs);', 1)
        output.write('goto exit;', 1)
        output.write('}')
        output.write()

    def write_nargs(self, output: Output) -> None:
        if self.name == "METH_VARARGS":
            output.write('const Py_ssize_t nargs = PyTuple_GET_SIZE(args);')

    @staticmethod
    def _get_calling_convention(func: CFunction) -> 'CallingConvention':
        params = list(func.params)
        if params and params[0].is_module():
            del params[0]

        if not params:
            return CallingConvention("METH_NOARGS", func)
        elif len(params) == 1 and params[0].can_use_meth_o():
            return CallingConvention("METH_O", func)
        else:
            return CallingConvention("METH_VARARGS", func)


def get_cfunction(config, func):
    params = [
        CParameter(param.name, type=param.type, kind=param.kind,
                          default=param.default)
        for param in func.params]

    params.insert(0, MODULE_PARAM )

    return CFunction(config, func.name, params, doc=func.doc)


def get_text_signature(func: CFunction) -> str:
    sig = [f"{func.name}("]
    slash = False
    comma = False
    for param in func.params:
        if comma:
            sig.append(', ')
        comma = True

        if not slash and param.kind != ParameterKind.POSITIONAL_ONLY:
            sig.append('/, ')
            slash = True

        name = param.name
        if param.is_module():
            name = f'${name}'
        if param.default is not EMPTY:
            sig.append(f'{name}={param.default}')
        else:
            sig.append(f'{name}')

    if not slash:
        sig.append(', /')
    sig.append(')')
    return ''.join(sig)
