#!/usr/bin/env python

import aes_py.aes_functions 

# key is decoded directly as hex for convenience as we use hex values in our sbox and else 
clear_txt = 'clear.txt2'
key = '1234567812345678'
key2 = '123456781234567812345678'
key3 = '12345678123456781234567812345678'
iv = 'a0420abd19e0f34d'
iv2 = 'a0420abd19e0f34dbd86172f'
iv3 = 'a0420abd19e0f34dbd86172f12a46d92'

with open(clear_txt, 'r') as f:
    clear_txt = f.read()

# Create an instance for our aes operations
aes_ops = aes_py.aes_functions.AesDog(clear_txt, '', key3)

# Prepare key
aes_ops.key_expansion()

# Encrypt clear_txt
aes_ops.encrypt('cbc', iv=iv3) # With mode CBC, use a proper IV

# print result
print "Clear text: {0}".format(aes_ops.clear)
print "Encrypted text: {0}".format(aes_ops.encrypted)
print "(base64): {0}".format(aes_ops.encrypted.encode('base64'))
aes_ops.decrypt('cbc', iv=iv3)
print "Entligen... : {0}".format(aes_ops.decrypted)

