from ..regions import Section

class PESection(Section):
    """
    Represents a section for the PE format.
    """
    def __init__(self, pe_section, remap_offset=0, align=None):
        super(PESection, self).__init__(
            pe_section.Name,
            pe_section.Misc_PhysicalAddress,
            pe_section.VirtualAddress + remap_offset,
            pe_section.Misc_VirtualSize,
        )

        self.characteristics = pe_section.Characteristics
        self.align           = align

    #
    # Public properties
    #

    @property
    def is_readable(self):
        return self.characteristics & 0x40000000 != 0

    @property
    def is_writable(self):
        return self.characteristics & 0x80000000 != 0

    @property
    def is_executable(self):
        return self.characteristics & 0x20000000 != 0
