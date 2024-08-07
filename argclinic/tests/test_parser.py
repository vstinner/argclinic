from argclinic.parser import ParseFunction, ParserFunction, ParserParameter, ParameterKind, EMPTY
from textwrap import dedent
import unittest


POSITIONAL_OR_KEYWORD = ParameterKind.POSITIONAL_OR_KEYWORD
POSITIONAL_ONLY = ParameterKind.POSITIONAL_ONLY
KEYWORD_ONLY = ParameterKind.KEYWORD_ONLY


def parse_func(text):
    text = dedent(text).strip()
    return ParseFunction().parse(text)


class ParseFuncTests(unittest.TestCase):
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

    def test_parser(self):
        func = parse_func("""
            get_fd

                fd: int
        """)
        expected = ParserFunction("get_fd")
        expected.params = [
            ParserParameter("fd", type="int", kind=POSITIONAL_OR_KEYWORD),
        ]
        self.check_func(func, expected)

    def test_pos_only(self):
        func = parse_func("""
            get_fd

                fd: int
                /

            Return the name of the terminal device connected to 'fd'.
        """)
        expected = ParserFunction("get_fd")
        expected.doc = "Return the name of the terminal device connected to 'fd'."
        expected.params = [
            ParserParameter("fd", type="int", kind=POSITIONAL_ONLY),
        ]
        self.check_func(func, expected)

    def test_default(self):
        func = parse_func("""
            dup2

                fd1: int
                fd2: int = 2
        """)
        expected = ParserFunction("dup2")
        expected.params = [
            ParserParameter("fd1", type="int", kind=POSITIONAL_OR_KEYWORD),
            ParserParameter("fd2", type="int", default="2",
                            kind=POSITIONAL_OR_KEYWORD),
        ]
        self.check_func(func, expected)

    def test_default(self):
        func = parse_func("""
            os.stat

                path : path_t
                *
                dir_fd : dir_fd = None
                follow_symlinks: bool = True

            Perform a stat system call on the given path.
        """)
        expected = ParserFunction("os.stat")
        expected.doc = "Perform a stat system call on the given path."
        expected.params = [
            ParserParameter("path", type="path_t", kind=POSITIONAL_OR_KEYWORD),
            ParserParameter("dir_fd", type="dir_fd", default="None",
                            kind=KEYWORD_ONLY),
            ParserParameter("follow_symlinks", type="bool", default="True",
                            kind=KEYWORD_ONLY),
        ]
        self.check_func(func, expected)


if __name__ == "__main__":
    unittest.main()
