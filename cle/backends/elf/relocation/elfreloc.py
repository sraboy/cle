from ...relocation import Relocation

class ELFReloc(Relocation):
    def __init__(self, owner, symbol, relative_addr, addend=None):
        super(ELFReloc, self).__init__(owner, symbol, relative_addr)

        self._addend = addend

    @property
    def is_rela(self):
        return self._addend is not None

    @property
    def addend(self):
        if self.is_rela:
            return self._addend
        else:
            return self.owner_obj.memory.read_addr_at(self.relative_addr, orig=True)
