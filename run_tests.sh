set -e -x
python -m unittest \
    argclinic/tests/test_*.py \
    "$@"
