import struct
import logging

from . import Relocation
from ...address_translator import AT

l = logging.getLogger('cle.backends.pe.generic_pe')

# Reference: https://msdn.microsoft.com/en-us/library/ms809762.aspx
class WinReloc(Relocation):
    """
    :ivar is_base_reloc:    These relocations would be ignored by the linker if the executable were
                            loaded at its preferred base address.
    """
    def __init__(self, owner, symbol, addr, resolvewith=None):#, reloc_type=None, next_rva=None): # pylint: disable=unused-argument
        super(WinReloc, self).__init__(owner, symbol, addr, None)

        self.is_base_reloc = True if symbol == None else False
        self.is_import = not self.is_base_reloc

        self.resolvewith = resolvewith
        if self.resolvewith is not None:
            self.resolvewith = self.resolvewith.lower()


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

class DllImport(WinReloc):
    """
    There's nothing special to be done for DLL imports but this class
    provides a unique name to the relocation type.
    """
    pass


class IMAGE_REL_BASED_HIGHADJ(WinReloc):
    def __init__(self, owner, symbol, addr, resolvewith, reloc_type=None, next_rva=None):
        super(IMAGE_REL_BASED_HIGHADJ, self).__init__(owner, symbol, addr)
        self.next_rva = next_rva

class IMAGE_REL_BASED_HIGHLOW(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 4))
        org_value = struct.unpack('<I', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        rebased_bytes = struct.pack('<I', rebased_value % 2**32)
        return rebased_bytes

class IMAGE_REL_BASED_DIR64(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 8))
        org_value = struct.unpack('<Q', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        rebased_bytes = struct.pack('<Q', rebased_value)
        #l.debug('Got rebased_bytes %s and rebased_value %s', hex(org_value), hex(rebased_value))
        return rebased_bytes

class IMAGE_REL_BASED_HIGH(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 2))
        org_value = struct.unpack('<I', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        rebased_bytes = struct.pack('<H', rebased_value % 2**16)
        return rebased_bytes

class IMAGE_REL_BASED_LOW(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 4))
        org_value = struct.unpack('<I', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        rebased_bytes = struct.pack('<I', rebased_value & 0x0000FFFF)
        return rebased_bytes
