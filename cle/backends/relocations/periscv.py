import logging
from . import generic_pe

l = logging.getLogger('cle.relocations.periscv')

arch = 'peRISCV'

class IMAGE_REL_BASED_HIGHADJ(generic_pe.IMAGE_REL_BASED_HIGHADJ):
    pass

class IMAGE_REL_BASED_DIR64(generic_pe.IMAGE_REL_BASED_DIR64):
    pass

class IMAGE_REL_BASED_HIGHLOW(generic_pe.IMAGE_REL_BASED_HIGHLOW):
    pass

class IMAGE_REL_BASED_HIGH(generic_pe.IMAGE_REL_BASED_HIGH):
    pass

class IMAGE_REL_BASED_LOW(generic_pe.IMAGE_REL_BASED_LOW):
    pass

class IMAGE_REL_BASED_RISCV_HIGH20(generic_pe.WinReloc):
    pass

class IMAGE_REL_BASED_RISCV_LOW12I(generic_pe.WinReloc):
    pass

class IMAGE_REL_BASED_RISCV_LOW12S(generic_pe.WinReloc):
    pass
