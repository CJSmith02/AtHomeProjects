"""Assignment 1: Cryptography for CS41 Winter 2020.

Name: Caleb Smith
SUNet: <SUNet ID>

Replace this placeholder text with a description of this module.
"""
import utils
import string
import random

ALPHA = string.ascii_uppercase
#################
# CAESAR CIPHER #
#################


def encrypt_caesar(plaintext):
    """Encrypt a plaintext using a Caesar cipher.

    Add more implementation details here.

    :param plaintext: The message to encrypt.
    :type plaintext: str

    :returns: The encrypted ciphertext.
    """
    plaintext = plaintext.upper()
    ciphertext = ""
    
    for char in plaintext:
        i = ALPHA.find(char)
        if i == -1:
            ciphertext += char
        else:
            ciphertext += ALPHA[(i+3)%26]
    return ciphertext
    
def decrypt_caesar(ciphertext):
    """Decrypt a ciphertext using a Caesar cipher.

    Add more implementation details here.

    :param ciphertext: The message to decrypt.
    :type ciphertext: str

    :returns: The decrypted plaintext.
    """
    
    plaintext = ""
    
    for char in ciphertext:
        i = ALPHA.find(char)
        if i == -1:
            plaintext += char
        else:
            plaintext += ALPHA[i-3]
    return plaintext
    

###################
# VIGENERE CIPHER #
###################

def encrypt_vigenere(plaintext, keyword):
    """Encrypt plaintext using a Vigenere cipher with a keyword.

    Add more implementation details here.

    :param plaintext: The message to encrypt.
    :type plaintext: str
    :param keyword: The key of the Vigenere cipher.
    :type keyword: str

    :returns: The encrypted ciphertext.
    """
    ciphertext = ""
    
    for i in range(len(plaintext)):
        plainnum = ALPHA.find(plaintext[i])
        keynum = ALPHA.find(keyword[i%len(keyword)])
        if plainnum == -1:
            ciphertext += plaintext[i]
        else:
            ciphertext += ALPHA[(plainnum+keynum)%26]
    return ciphertext


      
def decrypt_vigenere(ciphertext, keyword):
    """Decrypt ciphertext using a Vigenere cipher with a keyword.

    Add more implementation details here.

    :param ciphertext: The message to decrypt.
    :type ciphertext: str
    :param keyword: The key of the Vigenere cipher.
    :type keyword: str

    :returns: The decrypted plaintext.
    """
    plaintext = ""
    
    for i in range(len(ciphertext)):
        ciphernum = ALPHA.find(ciphertext.upper()[i])
        keynum = ALPHA.find(keyword[i%len(keyword)])
        if ciphernum == -1:
            plaintext += ciphertext[i]
        else:
            plaintext += ALPHA[(ciphernum-keynum)%26]
    return plaintext
    
    
    raise NotImplementedError('decrypt_vigenere is not yet implemented!')


########################################
# MERKLE-HELLMAN KNAPSACK CRYPTOSYSTEM #
########################################

def generate_private_key(n=8):
    """Generate a private key to use with the Merkle-Hellman Knapsack Cryptosystem.

    Following the instructions in the handout, construct the private key
    components of the MH Cryptosystem. This consists of 3 tasks:

    1. Build a superincreasing sequence `w` of length n
        Note: You can double-check that a sequence is superincreasing by using:
            `utils.is_superincreasing(seq)`
    2. Choose some integer `q` greater than the sum of all elements in `w`
    3. Discover an integer `r` between 2 and q that is coprime to `q`
        Note: You can use `utils.coprime(r, q)` for this.

    You'll also need to use the random module's `randint` function, which you
    will have to import.

    Somehow, you'll have to return all three of these values from this function!
    Can we do that in Python?!

    :param n: Bitsize of message to send (defaults to 8)
    :type n: int

    :returns: 3-tuple private key `(w, q, r)`, with `w` a n-tuple, and q and r ints.
    """
    total = 1
    l = []
    for i in range(n):
        new = random.randint(total, 2*total)
        total += new
        l.append(new)
    w = tuple(l)
    q = random.randint(total+1, 2*total)
    
    for r in range(2,q-1):
        if utils.coprime(r,q):
            break
    return w, q, r


def create_public_key(private_key):
    """Create a public key corresponding to the given private key.

    To accomplish this, you only need to build and return `beta` as described in
    the handout.

        beta = (b_1, b_2, ..., b_n) where b_i = r × w_i mod q

    Hint: this can be written in one or two lines using list comprehensions.

    :param private_key: The private key created by generate_private_key.
    :type private_key: 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.

    :returns: n-tuple public key
    """
    w, q, r = private_key
    beta = tuple([r*w_i % q for w_i in w])
    return beta


def encrypt_mh(message, public_key):
    """Encrypt an outgoing message using a public key.

    Following the outline of the handout, you will need to:
    1. Separate the message into chunks based on the size of the public key.
        In our case, that's the fixed value n = 8, corresponding to a single
        byte. In principle, we should work for any value of n, but we'll
        assert that it's fine to operate byte-by-byte.
    2. For each byte, determine its 8 bits (the `a_i`s). You can use
        `utils.byte_to_bits(byte)`.
    3. Encrypt the 8 message bits by computing
         c = sum of a_i * b_i for i = 1 to n
    4. Return a list of the encrypted ciphertexts for each chunk of the message.

    Hint: Think about using `zip` and other tools we've discussed in class.

    :param message: The message to be encrypted.
    :type message: bytes
    :param public_key: The public key of the message's recipient.
    :type public_key: n-tuple of ints

    :returns: Encrypted message bytes represented as a list of ints.
    """
    c_array = []
    for char in message: #message is already in bytes
        alpha = utils.byte_to_bits(char)
        c = 0
        for a_i, b_i in zip(alpha, public_key):
            c += a_i * b_i
        c_array.append(c)
    return c_array


def decrypt_mh(message, private_key):
    """Decrypt an incoming message using a private key.

    Following the outline of the handout, you will need to:
    1. Extract w, q, and r from the private key.
    2. Compute s, the modular inverse of r mod q, using the Extended Euclidean
        algorithm (implemented for you at `utils.modinv(r, q)`)
    3. For each byte-sized chunk, compute
         c' = cs (mod q)
    4. Solve the superincreasing subset sum problem using c' and w to recover
        the original plaintext byte.
    5. Reconstitute the decrypted bytes to form the original message.

    :param message: Encrypted message chunks.
    :type message: list of ints
    :param private_key: The private key of the recipient (you).
    :type private_key: 3-tuple of w, q, and r

    :returns: bytearray or str of decrypted characters
    """
    #remember that the largest element in w is always the last one (index = -1)
    w, q, r = private_key
    s = utils.modinv(r,q)
    decoded = ['']
    for c in message:
        c_prime = (c * s)%q
        a=[]
        for i in range(len(w)-1, -1, -1):
            #a is the binary bits, but will be created backwards and then reversed
            if w[i] > c_prime:
                a.append(0)
            else:
                a.append(1)
                c_prime -= w[i]
            """
            poss = [elem for elem in w if elem <= remainder]
            biggest = max(poss)
            indexes.append(poss.index(biggest))
            remainder -= biggest
            print(remainder, biggest)
        print (indexes)
        """
        a.reverse()
        decoded.append(chr(utils.bits_to_byte(tuple(a))))
    return ''.join(decoded)