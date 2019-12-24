import sys
import os
from hoshingak.core.symbol import SymbolTable


def main(executable_object, finstrument_file):
    SymbolTable.dump(executable_object)
    table = SymbolTable()
    graph = table.create_graph(finstrument_file)
    graph.set_sensitivity(level=2)
    graph.check_coverage()
    graph.draw(f'./test')


if __name__ == '__main__':
    # Expects two files: executable file and finstrument.txt
    if len(sys.argv) != 3:
        print('Usage: ./main.py a.out finstrument.txt')
        exit(1)

    main(sys.argv[1], sys.argv[2])

