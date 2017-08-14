from ...relocation import Relocation

# Reference: https://msdn.microsoft.com/en-us/library/ms809762.aspx
class PEReloc(Relocation):
    """
    :ivar is_base_reloc:    These relocations would be ignored by the linker if the executable were
                            loaded at its preferred base address.
    """
    def __init__(self, owner, symbol, addr, resolvewith=None):#, reloc_type=None, next_rva=None): # pylint: disable=unused-argument
        super(PEReloc, self).__init__(owner, symbol, addr)

        self.is_base_reloc = True if symbol is None else False
        self.is_import = not self.is_base_reloc

        self.resolvewith = resolvewith
        if self.resolvewith is not None:
            self.resolvewith = str(self.resolvewith).lower()


    def resolve_symbol(self, solist, bypass_compatibility=False):
        if not bypass_compatibility:
            solist = [x for x in solist if self.resolvewith == x.provides]
        return super(WinReloc, self).resolve_symbol(solist)

    @property
    def value(self):
        if self.resolved:
            return self.resolvedby.rebased_addr

    def relocate(self, solist, bypass_compatibility=False):
        if self.owner_obj.image_base_delta == 0:
            return

        if self.symbol is None:  # relocation described in the DIRECTORY_ENTRY_BASERELOC table
            self.owner_obj.memory.write_bytes(self.relative_addr, self.value)
        else:
            return super(WinReloc, self).relocate(solist, bypass_compatibility)

