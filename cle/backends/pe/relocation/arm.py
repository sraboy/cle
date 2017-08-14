import logging
from . import generic

l = logging.getLogger('cle.relocations.pe.arm')

arch = 'arm'

class IMAGE_REL_BASED_HIGHADJ(generic.IMAGE_REL_BASED_HIGHADJ):
    pass

class IMAGE_REL_BASED_DIR64(generic.IMAGE_REL_BASED_DIR64):
    pass

class IMAGE_REL_BASED_HIGHLOW(generic.IMAGE_REL_BASED_HIGHLOW):
    pass

class IMAGE_REL_BASED_HIGH(generic.IMAGE_REL_BASED_HIGH):
    pass

class IMAGE_REL_BASED_LOW(generic.IMAGE_REL_BASED_LOW):
    pass

class IMAGE_REL_BASED_ARM_MOV32(generic.WinReloc):
    pass

class IMAGE_REL_BASED_THUMB_MOV32(generic.WinReloc):
    pass
