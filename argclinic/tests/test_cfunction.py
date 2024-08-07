from argclinic.utils import Config
from argclinic.parser import ParameterKind, ParserFunction, ParserParameter
from argclinic.cfunction import (
    CFunction, CParameter, get_cfunction, get_text_signature,
    MODULE_PARAM)
import unittest


CONFIG = Config()
POSITIONAL_ONLY = ParameterKind.POSITIONAL_ONLY
POSITIONAL_OR_KEYWORD = ParameterKind.POSITIONAL_OR_KEYWORD


class FromParserTests(unittest.TestCase):
    def check_arg(self, arg, expected):
        self.assertEqual(arg.name, expected.name)
        self.assertEqual(arg.type, expected.type)
        self.assertEqual(arg.kind, expected.kind)
        self.assertEqual(arg.default, expected.default)

    def check_func(self, func, expected):
        self.assertEqual(func.name, expected.name)
        self.assertEqual(len(func.params), len(expected.params))
        for func_arg, expected_arg in zip(func.params, expected.params):
            self.check_arg(func_arg, expected_arg)

    def test_get_cfunction(self):
        parser_func = ParserFunction("get_fd")
        parser_func.params = [
            ParserParameter("arg", type="object", kind=POSITIONAL_ONLY),
        ]
        func = get_cfunction(CONFIG, parser_func)

        params = [
            MODULE_PARAM,
            CParameter("arg", type="object", kind=POSITIONAL_ONLY),
        ]
        expected = CFunction(CONFIG, "get_fd", params)
        self.check_func(func, expected)


class CFunctionTests(unittest.TestCase):
    def test_calling_convention(self):
        # METH_NOARGS
        func = CFunction(CONFIG, "func", [MODULE_PARAM])
        self.assertEqual(func.calling_convention.name, "METH_NOARGS")

        # METH_O
        params = [MODULE_PARAM,
                  CParameter("arg", type="object", kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "func", params)
        self.assertEqual(func.calling_convention.name, "METH_O")

        # METH_VARARGS
        params = [MODULE_PARAM,
                  CParameter("arg", type="object", kind=POSITIONAL_ONLY),
                  CParameter("arg2", type="object", kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "func", params)
        self.assertEqual(func.calling_convention.name, "METH_VARARGS")

    def test_signature(self):
        # 0 params
        func = CFunction(CONFIG, "getuid", [MODULE_PARAM])
        self.assertEqual(get_text_signature(func), 'getuid($module, /)')

        # 1 pos only param
        params = [MODULE_PARAM,
                  CParameter('uid', type='uid_t', kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "setuid", params)
        self.assertEqual(get_text_signature(func), 'setuid($module, uid, /)')

        # 1 pos or keyword param
        params = [MODULE_PARAM,
                  CParameter('uid', type='uid_t', kind=POSITIONAL_OR_KEYWORD)]
        func = CFunction(CONFIG, "setuid", params)
        self.assertEqual(get_text_signature(func), 'setuid($module, /, uid)')

        # 2 pos or keyword params with a default value
        params = [MODULE_PARAM,
                  CParameter('fd', type='fildes', kind=POSITIONAL_OR_KEYWORD),
                  CParameter('nstype', type='int', kind=POSITIONAL_OR_KEYWORD,
                             default="0")]
        func = CFunction(CONFIG, "setns", params)
        self.assertEqual(get_text_signature(func), 'setns($module, /, fd, nstype=0)')

    def test_get_min_max_args(self):
        # 0 params
        func = CFunction(CONFIG, "func", [MODULE_PARAM])
        self.assertEqual(func.get_min_max_args(), (0, 0))

        # 1 param
        params = [MODULE_PARAM,
                  CParameter("arg", type="object", kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "func", params)
        self.assertEqual(func.get_min_max_args(), (1, 1))

        # 2 params
        params = [MODULE_PARAM,
                  CParameter("arg", type="object", kind=POSITIONAL_ONLY),
                  CParameter("arg2", type="object", kind=POSITIONAL_ONLY)]
        func = CFunction(CONFIG, "func", params)
        self.assertEqual(func.get_min_max_args(), (2, 2))

        # 1 mandatory param, 1 optional param
        params = [MODULE_PARAM,
                  CParameter("arg", type="object", kind=POSITIONAL_ONLY),
                  CParameter("arg2", type="int", kind=POSITIONAL_ONLY, default="2")]
        func = CFunction(CONFIG, "func", params)
        self.assertEqual(func.get_min_max_args(), (1, 2))


if __name__ == "__main__":
    unittest.main()
