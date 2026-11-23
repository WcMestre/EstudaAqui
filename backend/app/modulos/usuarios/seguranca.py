# PROVISÓRIO: substituir pela implementação da issue [1.1]
"""Hash de senha com Argon2 (argon2-cffi). A senha pura nunca é guardada."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

_hasher = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return _hasher.verify(senha_hash, senha)
    except VerificationError:
        return False


# Hash de uma senha qualquer, usado quando o e-mail não existe: assim o login
# leva o mesmo tempo nos dois casos e o tempo não denuncia quem tem conta.
HASH_FICTICIO = gerar_hash_senha("senha-que-nao-pertence-a-ninguem")
