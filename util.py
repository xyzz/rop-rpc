import struct

def u32(b, off=0):
	return struct.unpack("<I", b[off:off+4])[0]

def p32(x):
	return struct.pack("<I", x)

def u64(b, off=0):
	""" Unpack 64-bit """
	return struct.unpack("<Q", b[off:off+8])[0]

def p16(x):
	""" Pack 16-bit """
	return struct.pack("<H", x)

def c_str(b, off=0):
	b = b[off:]
	out = ""
	x = 0
	while b[x] != "\x00":
		out += b[x]
		x += 1
	return out

def isint(x):
    return type(x) is int or type(x) is long

def hexdump( src, length=16, sep='.', start=0 ):
	'''
	@brief Return {src} in hex dump.
	@param[in] length	{Int} Nb Bytes by row.
	@param[in] sep		{Char} For the text part, {sep} will be used for non ASCII char.
	@return {Str} The hexdump

	@note Full support for python2 and python3 !
	'''
	result = [];

	# Python3 support
	try:
		xrange(0,1);
	except NameError:
		xrange = range;

	for i in xrange(0, len(src), length):
		subSrc = src[i:i+length];
		hexa = '';
		isMiddle = False;
		for h in xrange(0,len(subSrc)):
			if h == length/2:
				hexa += ' ';
			h = subSrc[h];
			if not isinstance(h, int):
				h = ord(h);
			h = hex(h).replace('0x','');
			if len(h) == 1:
				h = '0'+h;
			hexa += h+' ';
		hexa = hexa.strip(' ');
		text = '';
		for c in subSrc:
			if not isinstance(c, int):
				c = ord(c);
			if 0x20 <= c < 0x7F:
				text += chr(c);
			else:
				text += sep;
		result.append(('%08X: %-'+str(length*(2+1)+1)+'s  |%s|') % (i+start, hexa, text));

	return '\n'.join(result);


def perm_to_str(perm):
	out = ""
	if perm & 1:
		out += "R"
	else:
		out += "-"
	if perm & 2:
		out += "W"
	else:
		out += "-"
	if perm & 4:
		out += "X"
	else:
		out += "-"
	return out
