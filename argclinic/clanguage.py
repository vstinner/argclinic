from argclinic.utils import Output
from argclinic.cfunction import CFunction, CParameter, get_text_signature


def escape_string(text: str) -> str:
    text = text.replace('"', '\\"')
    return f'"{text}"'


def write_pydoc(output: Output, func: CFunction) -> None:
    doc = func.doc

    newline = "\\n"
    output.write(f"PyDoc_STRVAR({func.doc_varname},")
    output.write(escape_string(get_text_signature(func) + newline))
    output.write(escape_string("--" + newline))
    if doc:
        output.write(escape_string(newline))
        lines = doc.splitlines()
        for index, line in enumerate(lines):
            if index != len(lines) - 1:
                output.write(escape_string(line + newline))
            else:
                output.write(escape_string(line) + ");")
    else:
        output.write(escape_string(newline) + ");")


def write_methoddef(output: Output, func: CFunction) -> None:
    name = func.func_name
    line = f'#define {name.upper()}_METHODDEF    \\'
    output.write(line)

    calling_convention = func.calling_convention
    line = f'{{"{name}", (PyCFunction){name}, {calling_convention.name}, {func.doc_varname}}},'
    output.write(line, 1)


class Converter:
    def __init__(self, output: Output, param: CParameter,
                 arg: str) -> None:
        self.output = output
        self.param = param
        self.arg = arg

    def _write(self, line: str = "", level: int = 0) -> None:
        self.output.write(line, level)

    def parse_param(self) -> None:
        raise NotImplementedError


class BoolConverter(Converter):
    def parse_param(self):
        var_name = self.param.name
        line = f'{self.param.type} {var_name} = PyObject_IsTrue({self.arg});'
        self._write(line)
        line = f'if ({var_name} == -1 && PyErr_Occurred()) {{'
        self._write(line)
        self._write('goto exit;', 1)
        self._write('}')
        self._write()


class IntConverter(Converter):
    def parse_param(self):
        var_name = self.param.name
        line = f'{self.param.type} {var_name} = PyLong_AsInt({self.arg});'
        self._write(line)
        line = f'if ({var_name} == -1 && PyErr_Occurred()) {{'
        self._write(line)
        self._write('goto exit;', 1)
        self._write('}')
        self._write()


CONVERTERS = {
    'bool': BoolConverter,
    'int': IntConverter,
}


def format_param_type(ctype: str, name: str) -> str:
    if ctype == 'PyObject*':
        return f'PyObject *{name}'
    else:
        return f'{ctype} {name}'


def write_impl_prototype(output: Output, func: CFunction) -> None:
    output.write('static PyObject *')
    args = [format_param_type(param.ctype, param.name)
            for param in func.params]
    line = f'{func.impl_name}({", ".join(args)});'
    output.write(line)


def write_impl(output: Output, func: CFunction) -> None:
    output.write('static PyObject *')
    args = [format_param_type(param.ctype, param.name)
            for param in func.params]
    line = f'{func.impl_name}({", ".join(args)})'
    output.write(line)


def write_function(output: Output, func: CFunction) -> None:
    calling_convention = func.calling_convention
    calling_convention.write_prototype(output)

    output.write('{')

    with output.indent():
        output.write('PyObject *return_value = NULL;')
        calling_convention.write_nargs(output)
        output.write()

        calling_convention.write_check_nargs(output)

        arg_index = 0
        for param in func.params:
            if param.is_module():
                continue
            converter = CONVERTERS.get(param.type, None)
            if converter is None:
                raise ValueError("no converter for type: {param.type!r}")

            arg = calling_convention.get_arg_value(arg_index)
            arg_index += 1
            conv = converter(output, param, arg)
            conv.parse_param()

        args = ', '.join(param.name for param in func.params)
        output.write(f'return_value = {func.impl_name}({args});')

    output.write()
    output.write('exit:')
    output.write('return return_value;', 1)
    output.write('}')
