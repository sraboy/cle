from ....address_translator import AT
from ....errors import CLEOperationError
from ...relocations import Relocation
from ... import Symbol

import struct

import logging
l = logging.getLogger('cle.relocations.generic')

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
    def __init__(self, owner, addr, next_rva):
        super(IMAGE_REL_BASED_HIGHADJ, self).__init__(owner, None, addr)
        self.next_rva = next_rva
    @property
    def value(self):
        """
        In all the other cases, we can ignore the relocation difference part of the
        calculation because we simply use to_mva() to get our rebased address. In this
        case, however, we have to adjust the un-rebased address first.
        """
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 2))
        org_value = struct.unpack('<I', org_bytes)[0]
        adjusted_value = (org_value << 16) + self.next_rva
        adjusted_value = (AT.from_lva(adjusted_value, self.owner_obj) & 0xffff0000) >> 16
        adjusted_bytes = struct.pack('<I', adjusted__value)
        return adjusted_bytes

class IMAGE_REL_BASED_HIGHLOW(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 4))
        org_value = struct.unpack('<I', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        rebased_bytes = struct.pack('<I', rebased_value)
        return rebased_bytes

class IMAGE_REL_BASED_DIR64(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 8))
        org_value = struct.unpack('<Q', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        rebased_bytes = struct.pack('<Q', rebased_value)
        return rebased_bytes

class IMAGE_REL_BASED_HIGH(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 2))
        org_value = struct.unpack('<H', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        adjusted_value = (rebased_value >> 16) & 0xffff
        adjusted_bytes = struct.pack('<H', adjusted_value)
        return adjusted_bytes

class IMAGE_REL_BASED_LOW(WinReloc):
    @property
    def value(self):
        org_bytes = ''.join(self.owner_obj.memory.read_bytes(self.relative_addr, 2))
        org_value = struct.unpack('<H', org_bytes)[0]
        rebased_value = AT.from_lva(org_value, self.owner_obj).to_mva()
        adjusted_value = rebased_value & 0x0000FFFF
        adjusted_bytes = struct.pack('<H', adjusted_value)
        return adjusted_bytes
