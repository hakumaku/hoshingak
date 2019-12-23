import sys
from hoshingak.core.symbol import SymbolTable
from hoshingak.core.graph import CallGraph


def main(executable_object, finstrument_file):
    # 다양한 경우 돌려보고 족적을 남겨라
    # loop() 만들어서 그거.
    # 그래프 마무리
    # linked 노드
    # color table
    SymbolTable.dump(executable_object)
    table = SymbolTable()
    # table.pretty_print()
    call_graph = CallGraph(table)
    call_graph.create(finstrument_file)
    call_graph.decrease_context_sensitivity(level=1)
    # call_graph.pretty_print()
    # call_graph.check_coverage()
    call_graph.draw('example')


if __name__ == '__main__':
    # Expects two files: executable file and finstrument.txt
    if len(sys.argv) != 3:
        print('Usage: ./main.py a.out finstrument.txt')
        exit(1)

    main(sys.argv[1], sys.argv[2])
