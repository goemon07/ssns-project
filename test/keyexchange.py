import struct
from secrets import token_bytes

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization, hmac
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def send(msg):
    print(sum(map(lambda x: len(x), msg)), msg)


curve = ec.SECP256R1
backend = default_backend()

# Server setup
s_secret = ec.generate_private_key(curve, backend)
s_public = s_secret.public_key()

# Client setup
c_serial = b'\000' + token_bytes(15)
c_secret = ec.generate_private_key(curve, backend)
c_public = c_secret.public_key()
c_nonce = token_bytes(32)

# Client hello
c_sk1 = HKDF(hashes.SHA256(), 64, None, None, backend).derive(c_secret.exchange(ec.ECDH(), s_public))
tmp0 = Cipher(algorithms.AES(c_sk1[:16]), modes.CBC(c_sk1[16:32]), backend)
tmp1 = tmp0.encryptor()
m1 = ('HELO', c_serial,
      c_public.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint),
      tmp1.update(c_nonce) + tmp1.finalize())
send(m1)

# Server hello
s_sk1 = HKDF(hashes.SHA256(), 64, None, None, backend).derive(s_secret.exchange(ec.ECDH(), c_public))
s_nonce = token_bytes(32)
tmp1 = Cipher(algorithms.AES(s_sk1[:16]), modes.CBC(s_sk1[16:32]), backend).decryptor()
tmp1 = tmp1.update(m1[3]) + tmp1.finalize() + s_nonce + m1[1]
tmp2 = hmac.HMAC(s_sk1, hashes.SHA256(), backend)
tmp2.update(tmp1)
tmp1 = tmp2.finalize()
s_sk2 = tmp1[:16]
s_sk3 = tmp1[16:]
tmp1 = Cipher(algorithms.AES(s_sk1[:16]), modes.CBC(s_sk1[16:32]), backend).encryptor()
m2 = ('HELO', tmp1.update(s_nonce) + tmp1.finalize())
send(m2)

# Client key derivation
tmp1 = tmp0.decryptor()
tmp2 = hmac.HMAC(c_sk1, hashes.SHA256(), backend)
tmp2.update(c_nonce + tmp1.update(m2[1]) + tmp1.finalize() + c_serial)
tmp1 = tmp2.finalize()
c_sk2 = tmp1[:16]
c_sk3 = tmp1[16:]

# Send message
tmp0 = Cipher(algorithms.AES(c_sk2), modes.CTR(c_sk3), backend).encryptor()
tmp1 = tmp0.update(struct.pack('fffff', 0.1, 3.141, -13, 0, float('nan'))) + tmp0.finalize()
m3 = ('DATA', c_serial, tmp1, c_secret.sign(tmp1, ec.ECDSA(hashes.SHA256())))
send(m3)

# Read message
c_public.verify(m3[3], m3[2], ec.ECDSA(hashes.SHA256()))
tmp0 = Cipher(algorithms.AES(s_sk2), modes.CTR(s_sk3), backend).decryptor()
tmp1 = struct.unpack('fffff', tmp0.update(m3[2]) + tmp0.finalize())
print(tmp1)


if __name__ == '__main__':
    pass
