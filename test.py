#!/usr/bin/env python2
from __future__ import print_function
import unittest
import shutil
import os
import subprocess
import tempfile
from sys import argv

from rop import Rop, F, G, wk_base, Ret
from relocatable import Relocatable as R
from util import u64

g_main_bin = None
g_wk_bin = None

data = R(R.data, 0)

class Test(unittest.TestCase):

	def setUp(self):
		self.rop = Rop()

	def execute(self):
		# this must match test/main.c!
		reloc = {
			1: 0x0100000000, # data
			2: 0x0200000000, # main
			3: 0x0300000000, # wk
		}
		binary = self.rop.generate_binary(reloc)


		tmp = tempfile.mkdtemp()
		rop_bin = os.path.join(tmp, "rop.bin")
		with open(rop_bin, "wb") as fout:
			fout.write(binary)
		os.chdir("test")
		try:
			with open(os.devnull, 'w') as devnull:
				output = subprocess.check_output(["./run.sh", g_main_bin, g_wk_bin, rop_bin], stderr=devnull)
		except Exception as e:
			os.chdir("..")
			raise e
		os.chdir("..")
		
		self.memory = output

		shutil.rmtree(tmp)

	def test_write(self):
		"""" Tests that the write64 gadget works """
		self.rop.write64(0x1234567887654321, data + 0)
		self.rop.write64(0xDEADBEEF, data + 8)
		self.execute()
		self.assertEqual(u64(self.memory, 0), 0x1234567887654321)
		self.assertEqual(u64(self.memory, 8), 0xDEADBEEF)

	def test_func_call(self):
		""" Tests that chaining functions works, and arguments are passed properly """
		self.rop.call(F.setjmp, data + 0, 0x1111111111, 0x2222222222, 0x3333333333, 0x4444444444) # setjmp
		self.rop.write64(0xDEAD, data + 0x50)
		self.rop.call(F.setjmp, data + 0x100, 0x8, 0x7, 0x6, 0x5) # setjmp
		self.execute()
		self.assertEqual(u64(self.memory, 0x8), 0x1111111111)
		self.assertEqual(u64(self.memory, 0x10), 0x2222222222)
		self.assertEqual(u64(self.memory, 0x18), 0x3333333333)
		self.assertEqual(u64(self.memory, 0x20), 0x4444444444)
		self.assertEqual(u64(self.memory, 0x50), 0xDEAD)
		self.assertEqual(u64(self.memory, 0x108), 0x8)
		self.assertEqual(u64(self.memory, 0x110), 0x7)
		self.assertEqual(u64(self.memory, 0x118), 0x6)
		self.assertEqual(u64(self.memory, 0x120), 0x5)

	def test_awrite(self):
		""" Tests that awrite works and is zero-terminated when needed """
		mem1 = self.rop.awrite("such rop") # non zero-terminated
		mem2 = self.rop.awrites("much code exec..")
		mem3 = self.rop.awrite("x")
		mem4 = self.rop.awrite("y")
		mem_last = self.rop.awrite("\x00")
		self.execute()
		wrote = self.memory[mem1.imm:mem_last.imm]
		self.assertEqual(wrote, "such ropmuch code exec..\x00\x00\x00\x00\x00\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00y\x00\x00\x00\x00\x00\x00\x00")

	def test_store_load_ret(self):
		""" Tests that store_ret and load_ret work """
		self.rop.write64(0x8DEADB00B, data)
		self.rop.load_ret(data)
		self.rop.store_ret(data + 8)
		self.rop.load_ret(data + 8)
		self.rop.store_ret(data + 0x50)
		self.execute()
		self.assertEqual(u64(self.memory, 0), 0x8DEADB00B)
		self.assertEqual(u64(self.memory, 8), 0x8DEADB00B)
		self.assertEqual(u64(self.memory, 0x50), 0x8DEADB00B)

	def test_rv_call(self):
		""" Tests that x0 is forwarded properly """
		off = 0x1230
		self.rop.write64(data + off, data)
		self.rop.load_ret(data)
		self.rop.call(F.setjmp, Ret, 1, 2, 3, 4)
		self.execute()
		for x in range(1, 5):
			self.assertEqual(u64(self.memory, off + x * 8), x)

	def test_set_x8(self):
		""" Tests that setting X8 works """
		self.rop.call(F.setjmp, data + 0, 2, 3, x8=0xB00BBABE) # setjmp
		self.execute()
		self.assertEqual(u64(self.memory, 1 * 8), 2)
		self.assertEqual(u64(self.memory, 2 * 8), 3)
		self.assertEqual(u64(self.memory, 8 * 8), 0xB00BBABE)

	def test_v8_call(self):
		""" Tests that calling with a lot of args works """
		self.rop.call(F.setjmp, data + 0, 2, 3, 4, 5, 6, 7, 8) # setjmp
		self.execute()
		for x in range(1, 8):
			self.assertEqual(u64(self.memory, x * 8), x + 1)

	def test_dump_regs(self):
		""" Tests that dumping regs via setjmp works """
		self.rop.call(G.ret, 1, 2, 3, 4, 5, 6, 7, 8)
		self.rop.dump_regs(data, and_store_r0=data + 0x400)
		self.execute()
		self.assertEqual(u64(self.memory, 0x400), 1) # r0
		for x in range(1, 8):
			self.assertEqual(u64(self.memory, x * 8), x + 1)


def main():
	if len(argv) != 3:
		print("Usage: ./test.py main.bin wk.bin")
		return -1

	global g_main_bin
	global g_wk_bin

	g_main_bin = argv[1]
	g_wk_bin = argv[2]
	del argv[1:]

	unittest.main()


if __name__ == "__main__":
	main()
