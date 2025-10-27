from fastapi import HTTPException, status, Request, Response
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# SECRET_KEY estável - DEVE vir de variável de ambiente em produção
# Em desenvolvimento, usa uma chave fixa (mas diferente para cada projeto)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chave-secreta-fixa-para-desenvolvimento-torneio-xadrez-senai-2024-morvan-figueiredo")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Configuração do hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Credenciais do administrador
# NOTA: Em produção, estas devem vir de variáveis de ambiente
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "Biblioteca@senaimovanfigueiredo.com.br")

# Hash bcrypt da senha "biblioteca103103"
# Gerado com: pwd_context.hash("biblioteca103103")
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    "$2b$12$B9iQVb4U6d1U80WYUTuFnO7bm0UkXovMMSA6KMAt69yXWQ5SJ3erq"
)


def hash_senha(senha: str) -> str:
    """Cria um hash seguro da senha usando bcrypt"""
    return pwd_context.hash(senha)


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(senha_plain, senha_hash)


def criar_token(email: str) -> str:
    """Cria um token JWT para o usuário"""
    expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados = {"sub": email, "exp": expiracao}
    token = jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verificar_credenciais(email: str, senha: str) -> bool:
    """Verifica se as credenciais do administrador estão corretas usando hash bcrypt"""
    # Verifica o email primeiro
    if email != ADMIN_EMAIL:
        return False
    
    # Verifica a senha usando bcrypt hash
    try:
        return verificar_senha(senha, ADMIN_PASSWORD_HASH)
    except Exception as e:
        # Log do erro para debug (em produção, usar logging adequado)
        print(f"Erro na verificação de senha: {e}")
        return False


def obter_usuario_sessao(request: Request) -> str:
    """Obtém o email do usuário da sessão (cookie)"""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Faça login para acessar esta área."
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado ou inválido. Faça login novamente."
        )


def verificar_admin(request: Request) -> str:
    """Verifica se o usuário está autenticado como administrador"""
    return obter_usuario_sessao(request)


def criar_cookie_sessao(response: Response, email: str):
    """Cria um cookie de sessão com o token JWT"""
    token = criar_token(email)
    
    # Em desenvolvimento, secure=False para funcionar sem HTTPS
    # Em produção com HTTPS, SEMPRE usar secure=True
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,  # Protege contra XSS
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",  # Proteção contra CSRF
        secure=is_production  # True apenas em produção com HTTPS
    )


def limpar_cookie_sessao(response: Response):
    """Remove o cookie de sessão"""
    response.delete_cookie(key="session_token")
