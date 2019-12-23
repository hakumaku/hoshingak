from collections import MutableMapping
from itertools import islice
from os import PathLike
from subprocess import check_call
from typing import Union, List, Dict, Iterable,\
    Tuple, ValuesView, ItemsView, KeysView


class Symbol:
    NUM_SYMBOL = 0

    def __init__(self, prefix: str, tokens: List[str]):
        """
        :param prefix: is a name of .c file that hold the given function.
        :param tokens: [address, scope, kind, section, range, name]
        """
        self.address = int(tokens[0], 16)
        self.scope = 'static' if tokens[1] == 'l' else 'global'
        self.kind = tokens[2]
        self.section = tokens[3]
        self.offset = int(tokens[4], 16)
        self.prefix = prefix
        self.fn_number = self._get_fn_number_counter()
        self.name = tokens[5]
        self.call_count = 0

    def __str__(self):
        return f'{self.prefix}/{self.name}'

    def is_caller(self, address):
        if self.address <= address <= self.address + self.offset:
            return True
        else:
            return False

    def _get_fn_number_counter(self):
        number = self.NUM_SYMBOL
        Symbol.NUM_SYMBOL += 1
        return number


class SymbolTable(MutableMapping):
    OBJDUMP_SYMBOLS = 'symbols.objdump'
    OBJDUMP_DECODED = 'debug_line.objdump'

    def __init__(self, symbol_file=OBJDUMP_SYMBOLS,
                 decoded_file=OBJDUMP_DECODED, *args, **kwargs):
        self.prefixes: Dict[str, (int, int)] = dict()
        self._name_table: Dict[int, Symbol] = dict()

        if decoded_file:
            self.read_decoded_line(decoded_file)

        if symbol_file:
            self.read_symbol_table(symbol_file)

        self.update(dict(*args, **kwargs))

    def __getitem__(self, k: int) -> Symbol:
        return self._name_table[k]

    def __setitem__(self, k: int, v: Symbol) -> None:
        self._name_table[k] = v

    def __delitem__(self, k: int) -> None:
        del self._name_table[k]

    def __contains__(self, item) -> bool:
        return item in self._name_table

    def __iter__(self) -> Iterable:
        return iter(self._name_table.items())

    def __len__(self) -> int:
        return len(self._name_table.values())

    def keys(self) -> KeysView[int]:
        return self._name_table.keys()

    def values(self) -> ValuesView[Symbol]:
        return self._name_table.values()

    def items(self) -> ItemsView[int, Symbol]:
        return self._name_table.items()

    def get(self, address: int, default=None) -> Symbol:
        return self._name_table.get(address)

    def update(self, item: Dict[int, Symbol],
               **kwargs: Dict[int, Symbol]) -> None:
        self._name_table.update(item, **kwargs)

    def pop(self, address: int) -> Symbol:
        return self._name_table.pop(address)

    def popitem(self) -> Tuple[int, Symbol]:
        return self._name_table.popitem()

    def clear(self) -> None:
        self._name_table.clear()

    @classmethod
    def dump(cls, obj):
        cmd = ['objdump', '-t', f'{obj}']
        with open(cls.OBJDUMP_SYMBOLS, 'w') as output:
            check_call(cmd, stdout=output)

        with open(cls.OBJDUMP_DECODED, 'w') as output:
            cmd[1] = '-WL'
            check_call(cmd, stdout=output)

    def read_decoded_line(self, file: Union[str, int, bytes, PathLike]):
        # Parse source code file address generated from 'objdump - Wl'.
        with open(file, 'r') as fp:
            source_code_name = None
            start_addr = None
            token_list = [line.split() for line in fp.readlines()]
            del token_list[:5]
            for index, tokens in enumerate(token_list):
                if not tokens:
                    continue

                # e.g) CU: test/example.c:
                if tokens[0].startswith('CU'):
                    # Skip the first entrance.
                    if index >= 3:
                        end_addr = int(token_list[index - 3][2], 16)
                        self.prefixes[source_code_name] = (start_addr, end_addr)
                    source_code_name = tokens[1].rstrip('.c:').lstrip('./')
                    start_addr = int(token_list[index + 2][2], 16)
            else:
                end_addr = int(token_list[index - 2][2], 16)
                self.prefixes[source_code_name] = (start_addr, end_addr)

    def read_symbol_table(self, file: Union[str, int, bytes, PathLike]):
        assert len(self.prefixes) != 0,\
            f'self.prefixes is not initialized.\nYou must call ' \
            f'{self.__class__.__name__}.read_decoded_line() prior to ' \
            f'{self.__class__.__name__}.read_symbol_table().'

        # Parse symbol table generated from 'objdump -t'.
        with open(file, 'r') as fp:
            token_list = (line.split() for line in fp.readlines())
            for tokens in token_list:
                if len(tokens) != 6:
                    continue

                # Condition of function
                if tokens[2] == 'F' and tokens[3] == '.text':
                    address = int(tokens[0], 16)
                    symbol = Symbol(self.find_prefix(address), tokens)
                    self[address] = symbol

    def find_prefix(self, address: int) -> str:
        for prefix, (start_addr, end_addr) in self.prefixes.items():
            if start_addr <= address <= end_addr:
                return prefix

        return 'Unknown'

    def find_caller(self, call_site):
        """
        :param call_site:
        :return:
        """
        for symbol in self.values():
            if symbol.is_caller(call_site):
                return symbol

        return None

    def pretty_print(self):
        for k, v in self.items():
            print(f'{v} at {hex(k)}')
