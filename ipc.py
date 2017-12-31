        self.c = []
    def add_raw_32(self, val):
        self.raw += struct.pack('<I', val)
    def _add_c(self, buf, size): # Must be called after all other add_raw* calls.
        self.add_raw_32(size & 0xFFFF)
        flags = (((buf >> 32) & 0xFFFF)) | (size << 16)
        #word0 = 0x5 #size
        self.c.append(struct.pack('<II', buf & 0xFFFFFFFF, flags)) #originally III

    def add_8_2(self, buf, size):
        return self._add_c(buf, size)

        c_bufs = ''.join(self.c)

        #print len(self.raw)
        return header + self.raw + c_bufs
        #c.x(cmdbuf, 0x100)
