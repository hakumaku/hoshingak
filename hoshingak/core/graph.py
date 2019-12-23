from __future__ import annotations

import copy
import sys
from typing import Union, List, Dict, Type

from hoshingak.core.symbol import SymbolTable, Symbol
from graphviz import Digraph


class CallGraphBaseNode:
    def __init__(self, symbol: Symbol, call_site: int):
        self.symbol = symbol
        self.call_site = call_site
        self.incoming_nodes: Dict[int, Type[CallGraphBaseNode]] = dict()
        self.outgoing_nodes: Dict[int, Type[CallGraphBaseNode]] = dict()
        self.order = 0
        self.stime = 0
        self.etime = 0
        self._actual_elapsed = None

    def __str__(self):
        return f'{self.basename}/{self.symbol.name}#{self.call_site}'

    @property
    def call_count(self):
        return self.symbol.call_count

    @property
    def basename(self):
        return self.symbol.prefix

    @property
    def name(self):
        return f'{self.basename}/{self.symbol.name}({self.call_count})' \
               f'#{self.call_site}'

    @property
    def color_index(self):
        return self.symbol.fn_number

    @property
    def is_root(self):
        return True if self.call_site == 0 else False

    @property
    def address(self):
        return self.symbol.address

    @property
    def elapsed(self):
        return self.etime - self.stime

    @property
    def actual_elapsed(self):
        if not self._actual_elapsed:
            self._actual_elapsed = self.elapsed - sum(
                node.elapsed for node in self.outgoing_nodes.values())
        return self._actual_elapsed

    def link(self, node: CallGraphBaseNode):
        """
        self -> node.
        self is a incoming node of 'node'.
        'node' is a outgoing node of self.
        """
        self.outgoing_nodes[node.call_site] = node
        node.incoming_nodes[self.call_site] = self

    def dislink(self, node: CallGraphBaseNode):
        self.outgoing_nodes.pop(node.call_site)
        node.incoming_nodes.pop(self.call_site)

    def inc_count(self):
        self.symbol.call_count += 1

    def pretty_print(self):
        print(f'{self}\n'
              f'\torder: {self.order}\n'
              f'\tcount: {self.call_count}\n'
              f'\telapsed time: {self.elapsed}ns\n'
              f'\tactual running time: {self.actual_elapsed}ns\n'
              f'\tcalled by:')
        if not self.incoming_nodes.values():
            print('\t\tNone')
        else:
            for i, v in enumerate(self.incoming_nodes.values()):
                print(f'\t\t{i + 1}. {v}')


class CallGraphMultipleNodes(CallGraphBaseNode):
    def __init__(self, *args: CallGraphNode):
        if not self.check_condition(*args):
            raise TypeError
        first_node = args[0]
        for k, v in first_node.__dict__.items():
            self.__dict__[k] = copy.deepcopy(v)
        self.nodes: List[CallGraphNode] = [*args]

    def check_condition(self, *args: CallGraphNode):
        raise Exception('self.check_condition is not implemented.')

    def pretty_print(self):
        super().pretty_print()
        print(f'\tHaving:')
        for node in self.nodes:
            print(f'\t\t{node}', end=', ')
        else:
            print()


class CallGraphNode(CallGraphBaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.basename}/{self.symbol.name}#{self.call_site}'

    def __add__(self, node: CallGraphNode) -> Union[CallGraphMergedNode,
                                                    CallGraphLinkedNode]:
        # Return CallGraphMergedNode
        if self.symbol == node.symbol:
            try:
                return CallGraphMergedNode(self, node)

            except TypeError:
                print(f'{self} and {node} does not meet'
                      f' requirements for addition.')
                sys.exit(1)

        else:
            try:
                return CallGraphLinkedNode(self, node)

            except TypeError:
                print(f'{self} and {node} does not meet'
                      f' requirements for addition.')
                sys.exit(1)


class CallGraphMergedNode(CallGraphMultipleNodes):
    """
    It is a group of nodes, each of which has the same information
    (the same function), different call site and
    only one outgoing edge pointing to the same node.
    This is generated at context sensitivity 1.
    """

    def __init__(self, *args: CallGraphNode):
        super().__init__(*args)
        # Re-link all incoming nodes.
        # 1. Combine all incoming nodes.
        # 2. Set outgoing_node of the incoming nodes to this.
        first_node = self.nodes[0]
        for node in self.nodes:
            for inode in list(node.incoming_nodes.values()):
                inode.dislink(node)
                inode.link(self)
        # Dislink the outgoing node.
        outgoing_node = next(iter(first_node.outgoing_nodes.values()))
        for node in list(outgoing_node.incoming_nodes.values()):
            node.dislink(outgoing_node)
        self.link(outgoing_node)

    def __str__(self):
        return f'{self.basename}/{self.symbol.name}#Merged'

    def check_condition(self, *args: CallGraphNode) -> bool:
        node = args[0]
        symbol = node.symbol
        if len(node.outgoing_nodes) != 1:
            return False
        outgoing_node = list(node.outgoing_nodes.values())[0]

        others = args[1:]
        other: CallGraphNode
        for other in others:
            if node == other:
                return False

            if symbol != other.symbol:
                return False

            if len(other.outgoing_nodes) != 1:
                return False

            if outgoing_node != list(other.outgoing_nodes.values())[0]:
                return False

        return True


class CallGraphLinkedNode(CallGraphMultipleNodes):
    """
    It is a group of nodes, each of which has only one outgoing edge
    and one incoming edge.
    This is generated at context sensitivity 2.
    """

    def __init__(self, *args: CallGraphNode):
        super().__init__(*args)
        # inode -> node1 -> node2 -> node3 -> onode
        # becomes the following.
        # inode -> node1 [node1, node2, node3] -> onode
        last_node = self.nodes[-1]
        onode = next(iter(last_node.outgoing_nodes.values()))

        # Remove all links in self.nodes
        for node in self.nodes:
            node.incoming_nodes.popitem()
            node.outgoing_nodes.popitem()

        # Link properly
        onode.incoming_nodes.pop(last_node.call_site)
        onode.incoming_nodes[self.call_site] = self.nodes[0]
        self.outgoing_nodes[onode.call_site] = onode

    def __str__(self):
        return f'{self.basename}/{self.symbol.name}#Linked'

    def check_condition(self, *args: CallGraphNode) -> bool:
        node = args[0]
        if len(node.outgoing_nodes) != 1:
            if (len(node.incoming_nodes) != 1
                    or len(node.outgoing_nodes) != 1):
                return False

        next_nodes = args[1:]
        next_node: CallGraphNode
        for next_node in next_nodes:
            if (len(next_node.incoming_nodes) != 1
                    or len(next_node.outgoing_nodes) != 1):
                return False

            if node.outgoing_nodes[next_node.call_site] != next_node:
                return False

            node = next_node

        return True


class CallGraph:
    COLOR_TABLE = [
        '#fc0303', '#fca103', '#fcfc03', '#8cfc03',
        '#14fc03', '#03fcad', '#03fcf8', '#03c6fc',
        '#0356fc', '#4e03fc', '#ad03fc', '#fc03f4',
        '#fc0398', '#fc0339', '#b1fc03', '#613387',
    ]

    def __init__(self, symtab: SymbolTable):
        self.symtab = symtab
        self.nodes: Dict[int, Type[CallGraphBaseNode]] = dict()
        self.root = None

    @property
    def size(self):
        return len(self.nodes)

    def create(self, call_trace):
        """
        :param call_trace: file of addresses
                    generated by GCC -finstrument-functions with injection code.
        """
        # For measuring elapsed time.
        stack = []

        with open(call_trace) as fp:
            first_tokens = fp.readline().split()

            # Push the first node (Must be main function in C).
            callee_info = self.get_callee(int(first_tokens[0], 16))
            # To indicate that it is main function, pass call_site as 0
            self.root = self.set_node(callee_info, 0)
            self.root.stime = int(first_tokens[3])
            self.root.order = 1
            stack.append(self.root)

            # The first node in the stack starts with 1.
            order = 2
            # Note that all tokens separated here are all type of String.
            tokens = (line.split() for line in fp.readlines())
            for addr, call_site, flag, time in tokens:
                deci_addr = int(addr, 16)
                deci_call_site = int(call_site, 16)
                # On enter
                if flag == 'E':
                    callee = self.get_callee(deci_addr)
                    # The top node in the stack must be the caller.
                    caller_node = stack[-1]
                    callee_node = self.set_node(callee, deci_call_site)
                    if not callee_node.order:
                        callee_node.order = order
                        order += 1

                    callee_node.stime = int(time)
                    # Link as 'caller_node -> callee_node'
                    caller_node.link(callee_node)
                    stack.append(callee_node)

                # On exit
                else:
                    node = stack.pop(-1)
                    node.etime = int(time)

    def get_callee(self, address: int) -> Symbol:
        return self.symtab[address]

    def get_caller(self, call_site: int) -> Symbol:
        return self.symtab.find_caller(call_site)

    def get_node(self, symbol: Symbol) -> Type[CallGraphBaseNode]:
        return self.nodes[symbol.address]

    def set_node(self, symbol: Symbol, call_site: int):
        try:
            node = self.nodes[call_site]

        except KeyError:
            node = CallGraphNode(symbol, call_site)
            self.nodes[call_site] = node

        node.inc_count()
        return node

    def resolve_multiple_nodes(self, multiple_nodes: Type[CallGraphMultipleNodes]):
        for node in multiple_nodes.nodes:
            self.nodes.pop(node.call_site)
        self.nodes[multiple_nodes.call_site] = multiple_nodes

    def decrease_context_sensitivity(self, level=0):
        if level == 0:
            pass

        elif level == 1:
            self._merge_nodes()

        elif level == 2:
            self._merge_nodes()
            self._link_nodes()

        elif level == 3:
            pass

        else:
            pass

    def _merge_nodes(self):
        # Do 'Group by' and merge them.
        group: Dict[int, List[Type[CallGraphBaseNode]]] = dict()
        for node in self.nodes.values():
            incoming_nodes = list(node.incoming_nodes.values())
            # Nothing to decrease
            if len(incoming_nodes) == 1:
                continue

            for inode in incoming_nodes:
                try:
                    group[inode.symbol.address].append(inode)
                except KeyError:
                    group[inode.symbol.address] = [inode]

        for members in group.values():
            try:
                merged_node = CallGraphMergedNode(*members)
                self.resolve_multiple_nodes(merged_node)
            except TypeError:
                continue

    def _link_nodes(self):
        # Try get all the nodes having one incoming node and one outgoing node.
        nodes: Dict[int, Type[CallGraphBaseNode]] = dict()
        for node in self.nodes.values():
            if (len(node.incoming_nodes.values()) == 1
                    and len(node.outgoing_nodes.values()) == 1):
                nodes[node.call_site] = node

        # Figure out a linked list.
        while len(nodes) > 0:
            key, node = nodes.popitem()
            linked_node = [node]

            current_node = node
            while True:
                inode = next(iter(current_node.incoming_nodes.values()))
                try:
                    linked_node.insert(0, nodes.pop(inode.call_site))
                    current_node = inode
                except KeyError:
                    break

            current_node = node
            while True:
                onode = next(iter(node.outgoing_nodes.values()))
                try:
                    linked_node.append(nodes.pop(onode.call_site))
                    current_node = onode
                except KeyError:
                    break

            if len(linked_node) > 1:
                linked_node = CallGraphLinkedNode(*linked_node)
                self.resolve_multiple_nodes(linked_node)

    def draw(self, name):
        dot = Digraph(
            name=f'Call graph by GCC of {name}',
            comment='Call Tree',
            strict=True,
            format='PDF',
            graph_attr={
                'ordering': 'out',
                'compound': 'true'
            })
        self.normalize_frequency()
        for node in self.nodes.values():
            label_contents = f''
            if isinstance(node, CallGraphMergedNode):
                label_contents = f'Merged Node'

            elif isinstance(node, CallGraphLinkedNode):
                label_contents = f'Linked Node'

            else:
                pass

            dot.node(name=f'{node.name}', xlabel=f'{label_contents}',
                     fontname='NanumSquare', width='2', height='1', shape='box',
                     penwidth=f'{self.get_penwidth(node)}', color='#ff0000',
                     style='filled',
                     fillcolor=f'{self.get_color(node.color_index)}')

            for edge in node.incoming_nodes.values():
                dot.edge(str(edge.name), str(node.name), label=str(node.order))

        dot.render()

    def get_color(self, index):
        return CallGraph.COLOR_TABLE[index % 16]

    def normalize_frequency(self, step=10):
        """
        Get minimum call count and maximum call count.
        Divide them into 10 sections.
        """
        functions = [v.call_count for k, v in self.symtab]
        min_call_count = min(functions)
        max_call_count = max(functions)
        step_value = int((max_call_count - min_call_count) / step)
        self.frequency = [v for v in range(min_call_count, max_call_count, step_value)]

    def get_penwidth(self, node: Type[CallGraphBaseNode]):
        for index, level in enumerate(self.frequency):
            if not node.symbol.call_count >= level:
                return index

        return len(self.frequency) * 2

    def check_coverage(self):
        total = len(self.symtab)
        called_count = 0
        uncalled_count = 0
        v: Symbol
        for k, v in self.symtab:
            if v.call_count == 0:
                uncalled_count += 1
        called_count = total - uncalled_count

        print(f'Coverage: {called_count} out of {total} '
              f'({round((called_count / total) * 100, 2)}%).')
        print(f'Function not invoked: {uncalled_count}')
        print(f'Details:')
        for k, v in self.symtab:
            if v.call_count == 0:
                print(f'\t{v}')

    def pretty_print(self):
        for v in self.nodes.values():
            v.pretty_print()
