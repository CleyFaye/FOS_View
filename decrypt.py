from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

# Informations taken from FOSDecrypt.cs
# (original author: superkhung@vnsecurity.net)
class cryptoInfo(object):
    initVector = 'tu89geji340t89u2'
    passPhrase = 'UGxheWVy'
    keySize = 256

def decrypt(srcFile):
    # cipher = BASE64(decode, srcFile)
    # key = PBKDF2(passPhrase,IV)
    # ctx = CBC(AES,key,IV)
    # plain = ctx.decipher(cipher)
    try:
        rawData = srcFile.read()
    except Exception:
        with open(srcFile, 'r') as srcStream:
            rawData = srcStream.read()
    cipher = b64decode(rawData)
    key = PBKDF2(cryptoInfo.passPhrase, cryptoInfo.initVector, cryptoInfo.keySize / 8)
    ctx = AES.new(key, AES.MODE_CBC, cryptoInfo.initVector)
    return ctx.decrypt(cipher).replace('\x04', '')

if __name__ == '__main__':
    raise Exception('This program cannot be run in DOS mode')

