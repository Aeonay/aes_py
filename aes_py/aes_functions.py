'''
AesDog class for encrypting and decrypting in AES 128/192/256 bits.
Greatly inspired by https://gist.github.com/bonsaiviking/5571001
'''

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def xor(s1, s2):
    return tuple(a ^ b for a, b in zip(s1, s2))

def xtime(a):
    '''xtime multiplies bitwisely by two in the Gallois field GF(2^8)'''
    return ((a << 1) % 256) ^ (((a >> 7) & 1) * 0x1B)

def gf_mul(x, y):
    '''
    gfmul, for Gallois field multiplication.
    The biggest factor y that can be is 14 = 0x0E = (1110). (y>>4) is the
    maximum right shift we need for AesDog.
    '''
    return (
        ((y & 1) * x) ^
        ((y >> 1 & 1) * xtime(x)) ^
        ((y >> 2 & 1) * xtime(xtime(x))) ^
        ((y >> 3 & 1) * xtime(xtime(xtime(x)))) ^
        ((y >> 4 & 1) * xtime(xtime(xtime(xtime(x)))))
        )


class AesDog(object):
    '''AesDog class for AES encrypting/decrypting.'''
    # Rcon matrix. aes128 only uses up to rcon[10] for there are 11 round key
    # steps. In other variants with bigger blocks, aes uses up to rcon[29]
    # cells.
    rcon = (
        0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a,
        0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39,
        0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a,
        0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8,
        0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef,
        0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc,
        0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b,
        0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3,
        0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94,
        0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20,
        0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35,
        0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f,
        0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04,
        0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63,
        0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd,
        0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d
        )

    sbox = (
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
        )
    sbox_rev = (
        0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
        0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
        0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
        0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
        0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
        0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
        0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
        0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
        0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
        0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
        0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
        0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
        0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
        0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
        0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
        )

    clear = ''
    encrypted = decrypted = ''
    key = round_key = None
    state = []
    nb = nk = nr = 0
    iv = ''

    def __init__(self, clear, encrypted, key):
        self.key = key  # tuple(list(key))
        if not self.key:
            logger.error("key is undefined")
            exit(1)
        if len(self.key) == 128 / 8:
            self.nb = self.nk = 4
            self.nr = 10
        elif len(self.key) == 192 / 8:
            self.nb = self.nk = 6
            self.nr = 12
        elif len(self.key) == 256 / 8:
            self.nb = self.nk = 8
            self.nr = 14
        else:
            logger.error('Bad key length.')
            exit(1)
        if not len(encrypted) % (self.nb * 4) == 0:
            logger.error('Encrypted text has a wrong length (not of the block \
                        size nb*4).')
            exit(1)
        else:
            self.encrypted = encrypted
        self.clear = clear


    def padding(self, s):
        '''
       	Padding is used to have every block (namely, the last one) of the same
       	proper block length.  We use PKCS#7: the size of the padding (bytes) is
       	used for padding. e.g.: 04 04 04 04 for four padding bytes.
       	'''
        n = len(s) % (self.nb*4)
        if n == 0:
            return s
        else:
            n = self.nb*4 - n
            return s + chr(n)*n

    def rm_padding(self, s):
        n = ord(s[-1])
        if n < self.nb*4:
            return s[0:-n]
        else:
            return s

    def encrypt(self, mode, **kwparams):
        '''Encrypt the data using block cipher mode'''
        if 'iv' in kwparams:
            self.iv = kwparams['iv']
        self.clear = self.padding(self.clear)
        func = getattr(self, 'bmode_'+mode+'_enc')
        func()

    def decrypt(self, mode, **kwparams):
        if not len(self.encrypted) % (self.nb*4) == 0:
            logger.error('Bad length for encrypted value.')
            exit(1)
        if 'iv' in kwparams:
            self.iv = kwparams['iv']
        func = getattr(self, 'bmode_'+mode+'_dec')
        func()
        self.decrypted = self.rm_padding(self.decrypted)

    def check_iv(self):
        if not len(self.iv) == self.nb * 4:
            logger.error('IV missing or bad length, abort.')
            exit(1)


    def bmode_ecb_enc(self):
        '''
       	Basic mode for encrypting: each block is encrypted in the same way.
       	Comparing the result with an image, the resulting 'encrypted' image
       	would still be recognizable for each block would correspond to the
       	original clear text.
       	'''
        for i in range(len(self.clear) / (4*self.nb)):
            self.encrypted += self.cipher(self.clear[4*self.nb*i:4*self.nb*
                                                     (i+1)])

    def bmode_ecb_dec(self):
        for i in range(len(self.encrypted) / (4*self.nb)):
            self.decrypted += self.decipher(self.encrypted[4 * self.nb * i:4 *
                                                           self.nb * (i+1)])

    def bmode_cbc_enc(self):
        '''Mode CBC, safer than weak ECB (yet not always safe)'''
        self.check_iv()
        n = self.nb*4
        vector = self.iv
        for i in range(len(self.clear) / n):
            vector = cipher = self.cipher([chr(ord(a) ^ ord(b)) for a, b in
                                           zip(self.clear[n*i:n*(i+1)],
                                               vector)])
            self.encrypted += cipher

    def bmode_cbc_dec(self):
        self.check_iv()
        n = 4*self.nb
        vector = self.iv
        for i in range(len(self.encrypted) / n):
            self.decrypted += ''.join([chr(ord(a) ^ ord(b)) for a, b in
                                       zip(self.decipher(self.encrypted[n*i:n*(i+1)]),
                                           vector)])
            vector = self.encrypted[n*i:n*(i+1)]

    def cipher(self, block):
        '''Following key size, encrypt in 128, 192 or 256 bits'''
        self.state = map(ord, block)
        self.add_round_key(self.round_key[0:self.nb*4])
        for r in range(1, self.nr):
            self.sub_byte()
            self.shift_rows()
            self.mix_columns()
            self.add_round_key(self.round_key[self.nb*4*r:self.nb*4*(r+1)])
        self.sub_byte()
        self.shift_rows()
        self.add_round_key(self.round_key[self.nb*4*self.nr:self.nb*4*
                                          (self.nr+1)])
        return ''.join(map(chr, self.state))

    def decipher(self, block):
        self.state = map(ord, block)
        self.add_round_key(self.round_key[self.nb*4*self.nr:self.nb*4*
                                          (self.nr+1)])
        for r in range(self.nr-1, 0, -1):
            self.rev_shift_rows()
            self.rev_sub_byte()
            self.add_round_key(self.round_key[self.nb*4*r:self.nb*4*(r+1)])
            self.rev_mix_columns()
        self.rev_shift_rows()
        self.rev_sub_byte()
        self.add_round_key(self.round_key[0:self.nb*4])
        return ''.join(map(chr, self.state))

    def add_round_key(self, round_key):
        '''add_round_key performs a xor on the current round_key and the state'''
        for i, b in enumerate(round_key):
            self.state[i] ^= b

    def sub_byte(self):
        for i, b in enumerate(self.state):
            self.state[i] = AesDog.sbox[b]

    def rev_sub_byte(self):
        for i, b in enumerate(self.state):
            self.state[i] = AesDog.sbox_rev[b]

    def shift_rows(self):
        '''
       	The rows of the state are cyclically shifted over different offsets.
       	Row 0 is not shifted, Row 1,2,3 are shifted according the block length
       	nb.
       	'''
        rows = []
        rows.append(self.state[0::4])
        rows.append(self.state[1::4])
        rows[1] = rows[1][1:] + rows[1][:1]
        for r in range(2, 4):
            rows.append(self.state[r::4])
            if self.nb == 4 or self.nb == 6:
                rows[r] = rows[r][r:] + rows[r][:r]
            elif self.nb == 8:
                rows[r] = rows[r][r+1:] + rows[r][:r+1]
        self.state = [r[c] for c in range(self.nb) for r in rows]

    def rev_shift_rows(self):
        '''The reverse version of shift_rows, we rotate in the other way'''
        rows = []
        rows.append(self.state[0::4])
        rows.append(self.state[1::4])
        rows[1] = rows[1][self.nb-1:] + rows[1][:self.nb-1]
        for r in range(2, 4):
            rows.append(self.state[r::4])
            if self.nb == 4 or self.nb == 6:
                rows[r] = rows[r][self.nb-r:] + rows[r][:self.nb-r]
            elif self.nb == 8:
                rows[r] = rows[r][self.nb-r-1:] + rows[r][:self.nb-r-1]
        self.state = [r[c] for c in range(self.nb) for r in rows]

    def mix_columns(self):
        '''
       	For each column (nb columns), we diffuse the cipher by the following
       	operation:
       	    b0 = 2a0 ^ 3a1 ^ a2 ^ a3
       	    b1 = a0 ^ 2a1 ^ 3a2 ^ a3
       	    b2 = a0 ^ a1 ^ 2a2 ^ 3a3
       	    b3 = 3a0 ^ a1 ^ a2 ^ 2a3
       	Returns a modified value of the state.
       	'''
        temp = []
        for i in range(self.nb):
            c = self.state[i*4:(i+1)*4]
            temp.extend((
                gf_mul(c[0], 0x02) ^ gf_mul(c[1], 0x03) ^ c[2] ^ c[3],
                c[0] ^ gf_mul(c[1], 0x02) ^ gf_mul(c[2], 0x03) ^ c[3],
                c[0] ^ c[1] ^ gf_mul(c[2], 0x02) ^ gf_mul(c[3], 0x03),
                gf_mul(c[0], 0x03) ^ c[1] ^ c[2] ^ gf_mul(c[3], 0x02)
            ))
        self.state = temp

    def rev_mix_columns(self):
        temp = []
        for i in range(self.nb):
            c = self.state[i*4:(i+1)*4]
            temp.extend((
                gf_mul(c[0], 0x0e) ^ gf_mul(c[1], 0x0b) ^ gf_mul(c[2], 0x0d) ^ gf_mul(c[3], 0x09),
                gf_mul(c[0], 0x09) ^ gf_mul(c[1], 0x0e) ^ gf_mul(c[2], 0x0b) ^ gf_mul(c[3], 0x0d),
                gf_mul(c[0], 0x0d) ^ gf_mul(c[1], 0x09) ^ gf_mul(c[2], 0x0e) ^ gf_mul(c[3], 0x0b),
                gf_mul(c[0], 0x0b) ^ gf_mul(c[1], 0x0d) ^ gf_mul(c[2], 0x09) ^ gf_mul(c[3], 0x0e)
            ))
        self.state = temp

    def key_expansion(self):
        '''
    	The following functions are used to generate the expended key,
    	composed of the key and its derivatives, the round keys.
        '''
        words = []
        # The first round key (word) is the key itsefl
        words.extend(map(ord, self.key))
        logger.debug('Enterring key_expansion process, key used: %s', self.key)
        for i in range(self.nk, (self.nb * (self.nr + 1))):
            # We recuperate the precedent round_key (precedent word)
            temp = words[(i - 1)*4:i*4]
            # For words of position multiple of nk, we use rotword and then
            # subword functions on the preceding word
            if i % self.nk == 0:
                temp = xor(self.sub_word(self.rot_word(temp)),
                           (self.rcon[i / self.nk], 0, 0, 0))
            elif self.nk > 6 and i % self.nk == 4:
                temp = self.sub_word(temp)

            words.extend(xor(words[(i - self.nk) * 4: (i - self.nk + 1) * 4],
                             temp))
        self.round_key = words

    @staticmethod
    def rot_word(word):
        '''
       	rot_word performs a circular left shift on an input word and returns the
       	modified word: [b0, b1, b2, b3] => [b1, b2, b3, b0]
       	'''
        if not len(word) == 4:
            logger.error('word for rot_byte function of length other than 4.')
            exit(1)
        return word[1:] + word[:1]

    @staticmethod
    def sub_word(word):
        '''sub_word substitues the values of the input by values in the SBox'''
        if not len(word) == 4:
            logger.error('word for syb_byte function of length other than 4.')
            exit(1)
        return (AesDog.sbox[b] for b in word)
