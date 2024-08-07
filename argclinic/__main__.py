from argclinic.utils import Config, hash_text
from argclinic.parser import ParseFunction
from argclinic.cfunction import get_cfunction
from argclinic.clanguage import (
    Output, write_pydoc, write_methoddef, write_impl, write_impl_prototype,
    write_function)


def write(config, out, clinic_out, text):
    parser_func = ParseFunction().parse(text)
    func = get_cfunction(config, parser_func)

    output = Output()
    write_pydoc(output, func)
    output.write()
    write_methoddef(output, func)
    output.write()
    write_impl_prototype(output, func)
    output.write()
    write_function(output, func)

    for line in output.output:
        print(line, file=clinic_out)

    output = Output()
    write_impl(output, func)
    in_hash = hash_text(text)
    out_hash = hash_text('\n'.join(output.output))
    output.write(f'/*[clinic end generated code: output={out_hash} input={in_hash}]*/')
    for line in output.output:
        print(line, file=out)


def main():
    config = Config()

    filename = "file.c"
    filename2 = "file2.c"
    filename3 = "file2.clinic.c"
    with (open(filename) as fp,
          open(filename2, "w") as out,
          open(filename3, "w") as clinic_out):
        parse = False
        to_parse = None
        for line in fp:
            out.write(line)

            if line == "/*[clinic input]\n":
                parse = True
                to_parse = []
            elif line == "[clinic start generated code]*/\n":
                parse = False

                text = '\n'.join(to_parse)
                write(config, out, clinic_out, text)
            elif parse:
                to_parse.append(line)

main()
