from ...relocation import Relocation

# Reference: https://msdn.microsoft.com/en-us/library/ms809762.aspx
class PEReloc(Relocation):
    def __init__(self, owner, symbol, addr, resolvewith=None):#, reloc_type=None, next_rva=None): # pylint: disable=unused-argument
        super(PEReloc, self).__init__(owner, symbol, addr)

        self.resolvewith = resolvewith
        if self.resolvewith is not None:
            self.resolvewith = str(self.resolvewith).lower()

    def resolve_symbol(self, solist, bypass_compatibility=False):
        if not bypass_compatibility:
            solist = [x for x in solist if self.resolvewith == x.provides]
        return super(PEReloc, self).resolve_symbol(solist)

    def relocate(self, solist, bypass_compatibility=False):
        if self.owner_obj.image_base_delta == 0:
            return

        if self.symbol is None:  # relocation described in the DIRECTORY_ENTRY_BASERELOC table
            self.owner_obj.memory.write_bytes(self.relative_addr, self.value)
        else:
            return super(PEReloc, self).relocate(solist, bypass_compatibility)

    @property
    def value(self):
        if self.resolved:
            return self.resolvedby.rebased_addr

    @property
    def is_base_reloc(self):
        """
        These relocations are ignored by the linker if the executable
        is loaded at its preferred base address. There is no associated
        symbol with base relocations.
        """
        return True if self.symbol is None else False

    @property
    def is_import(self):
        return not self.is_base_reloc
