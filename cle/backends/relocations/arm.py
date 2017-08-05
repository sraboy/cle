from . import generic
from . import generic_elf
from . import Relocation
from ...address_translator import AT

import logging
l = logging.getLogger('cle.relocations.arm')

arch = 'ARM'

'''
Reference: "ELF for the ARM Architecture ABI r2.10"
    http://infocenter.arm.com/help/topic/com.arm.doc.ihi0044e/IHI0044E_aaelf.pdf
'''

class ARMRelocation:
    """
    Some items shared across ARM relocations. Eventually, much more can
    be put in here...
    """
    @staticmethod
    def _applyReloc(inst, result, mask=0xFFFFFFFF):
        assert not (result & ~mask)
        return ((inst & ~mask) | (result & mask))
        
    @staticmethod
    def _isThumbFunc(symbol, addr):
        return (addr % 2 == 1) and symbol.is_function

'''
With thanks to LLVM and Apple...
https://opensource.apple.com/source/clang/clang-137/src/lib/Target/ARM/ARMJITInfo.cpp

'''
class R_ARM_CALL(Relocation):
    """
    This class directly handles R_ARM_CALL and R_ARM_PC24 relocations. The
    formula is ((S + A) | T) - P.
     - S is the address of the symbol
     - A is the addend
     - P is the target location (place being relocated)
     - T is 1 if the symbol is of type STT_FUNC and addresses a Thumb instruction
    """
    #def _fixAddend(self, oldAddend):
    #    isBLX = (oldAddend & 0xF0000000) == 0xF0000000
    #    if isBLX: l.debug('BLX?! Are you sure?')
    #    bit_h = ((oldAddend & 0x1000000) >> 24) if isBLX else 0x00000000
    #    result = (((oldAddend & 0xFFFFFF) << 2) | (bit_h << 1))
    #    l.debug("2 A = self.addend = %s", hex(result))
    #    if result & 0x04000000: result |= 0xF0000000
    #    l.debug("3 A = self.addend = %s", hex(result))
    #    return result
        
    @property
    def value(self):
        P = self.rebased_addr                           # Location of this instruction
        A = inst = self.addend                          # The instruction
        S = self.resolvedby.rebased_addr                # The symbol's "value", where it points to
        T = ARMRelocation._isThumbFunc(self.symbol, S)
        
        l.debug("((S + A)) | T - P")
        l.debug("P = self.rebased_addr = %s", hex(self.rebased_addr))
        l.debug("A = self.addend = %s", hex(A))
        l.debug("S = self.resolvedby.rebased_addr = %s", hex(self.resolvedby.rebased_addr))
        l.debug("T = %s" % hex(T))
        
        if inst & 0x00800000:                           # Sign extend to 32-bits
            l.debug('**** Sign extending A ****')
            A |= 0xFF000000
            l.debug("A = self.addend = %s", hex(self.addend))
        #A = self._fixAddend(A)
        
        #l.debug("4 A = self.addend = %s", hex(A))
        
        result = ((S + A) | T) - P                      # Do the initial work
        imm24 = (result & 0x03FFFFFC) >> 2              # Sign_extend(inst[25:2])
        #l.debug('Assert: %x', imm24 >= -33554432 and imm24 <= 33554428) # Check for overflow
        
        
        if T:                                           # Do Thumb relocation
            mask = 0xFF000000
            bit_h = (result & 0x02) >> 1
            result = ARMRelocation._applyReloc(inst, (0xFA | bit_h), mask)
        else:                                           # Do ARM relocation
            mask = 0xFFFFFF
            result = ARMRelocation._applyReloc(inst, imm24, mask)
            
        
        
        self.owner_obj.memory.write_addr_at(AT.from_lva(self.addr, self.owner_obj).to_rva(), result)
        
        self.resolve(None)
        l.debug("%s relocated with new instruction: 0x%x", self.symbol.name, result)
        return True

'''       
class R_ARM_JUMP24(Relocation):
    """
    The same as R_ARM_CALL but without the Thumb mode check at the end
    """
    @property
    def value(self):

        P = self.rebased_addr
        A = self.addend
        S = self.resolvedby.rebased_addr
        T = (P % 2 == 1) and self.symbol.is_function
        
        if A & 0x00800000:
            l.debug('**** Sign extended ****')
            A |= 0xFF000000
        
        result = ((S + A) | T) - P
        imm24 = (result & 0x03FFFFFC) >> 2
        result = ARMRelocation._applyReloc(P, imm24, 0xFFFFFF)
        l.debug("%s relocated to: %s", self.symbol.name, hex(result))
        return result
        
class R_ARM_PREL31(Relocation):
    @property
    def value(self):
        P = self.rebased_addr
        A = self.addend
        S = self.resolvedby.rebased_addr
        T = (P % 2 == 1) and self.symbol.is_function
        #l.debug("((S + A)) | T - P")
        #l.debug("P = self.rebased_addr = %s", hex(self.rebased_addr))
        #l.debug("A = self.addend = %s", hex(self.addend))
        #l.debug("S = self.resolvedby.rebased_addr = %s", hex(self.resolvedby.rebased_addr))
        #l.debug("T = %s" % hex(T))
        result = ((S + A) | T) - P
        mask = 0x7FFFFFFF
        rel31 = result & mask
        result = ARMRelocation._applyReloc(P, rel31, 0x7FFFFFFF)
        #l.debug("%s relocated to: %s", self.symbol.name, hex(result))
        return result
'''

R_ARM_COPY          = generic.GenericCopyReloc
R_ARM_GLOB_DAT      = generic.GenericJumpslotReloc
R_ARM_JUMP_SLOT     = generic.GenericJumpslotReloc
R_ARM_RELATIVE      = generic.GenericRelativeReloc
R_ARM_ABS32         = generic.GenericAbsoluteAddendReloc

R_ARM_TLS_DTPMOD32  = generic_elf.GenericTLSModIdReloc
R_ARM_TLS_DTPOFF32  = generic_elf.GenericTLSDoffsetReloc
R_ARM_TLS_TPOFF32   = generic_elf.GenericTLSOffsetReloc

#R_ARM_CALL          = ARMPCRelativeAddendReloc32
R_ARM_JUMP24        = R_ARM_CALL
R_ARM_PC24          = R_ARM_CALL


#R_ARM_PLT32         = ARMPCRelativeAddendReloc32
