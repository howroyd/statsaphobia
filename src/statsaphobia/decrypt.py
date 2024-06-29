import hashlib
import pathlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def get_iv(raw_data: bytes, block_size: int) -> bytes:
    """Get the IV from the raw data."""
    return raw_data[:block_size]


def get_cyphertext(raw_data: bytes, block_size: int) -> bytes:
    """Get the cyphertext from the raw data and remove padding."""
    ret = raw_data[block_size:]
    retlen = len(ret) % block_size
    if retlen != 0:
        ret = ret[:-retlen]
    return ret


def make_key(password: str, iv: bytes, block_size: int) -> bytes:
    """Make a key from a password and an IV."""
    return hashlib.pbkdf2_hmac("sha1", password, iv, 100, dklen=block_size)


def decypher(rawdata: bytes, block_size: int, password: bytes) -> bytes:
    iv = get_iv(rawdata, block_size)
    cyphertext = get_cyphertext(rawdata, block_size)
    key = make_key(password, iv, block_size)

    cipher = Cipher(algorithms.AES128(key), modes.CBC(iv))

    decryptor = cipher.decryptor()

    return decryptor.update(cyphertext) + decryptor.finalize()


def do_decrypt(backupfile: pathlib.Path, outdir: pathlib.Path, block_size: int, password: bytes) -> pathlib.Path:
    """Decrypt the save file."""
    rawdata = backupfile.read_bytes()
    decrypted = decypher(rawdata, block_size, password)
    outfile = outdir / (backupfile.stem + ".bin")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_bytes(decrypted)
    return outfile
