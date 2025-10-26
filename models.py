from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


class Periodo(str, enum.Enum):
    MANHA = "manha"
    TARDE = "tarde"
    INTEGRAL = "integral"


class DiasSemana(str, enum.Enum):
    SEGUNDA_A_SEXTA = "segunda a sexta"
    SEGUNDA_E_TERCA = "segunda e terca"
    QUARTA_E_SEXTA = "quarta e sexta"
    SEXTA = "sexta"


class StatusTorneio(str, enum.Enum):
    RASCUNHO = "rascunho"
    SORTEADO = "sorteado"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADO = "finalizado"


class Fase(str, enum.Enum):
    OITAVAS = "oitavas"
    QUARTAS = "quartas"
    SEMIFINAL = "semifinal"
    FINAL = "final"


class Resultado(str, enum.Enum):
    J1 = "j1"
    J2 = "j2"
    EMPATE = "empate"
    PENDENTE = "pendente"


class Competidor(Base):
    __tablename__ = "competidores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    curso = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    periodo = Column(SQLEnum(Periodo), nullable=False)
    dias_semana = Column(SQLEnum(DiasSemana), nullable=False)

    partidas_j1 = relationship("Partida", foreign_keys="[Partida.jogador1_id]", back_populates="jogador1")
    partidas_j2 = relationship("Partida", foreign_keys="[Partida.jogador2_id]", back_populates="jogador2")
    vitorias = relationship("Partida", foreign_keys="[Partida.vencedor_id]", back_populates="vencedor")


class Torneio(Base):
    __tablename__ = "torneios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    status = Column(SQLEnum(StatusTorneio), nullable=False, default=StatusTorneio.RASCUNHO)
    seed = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    partidas = relationship("Partida", back_populates="torneio")


class Partida(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, index=True)
    torneio_id = Column(Integer, ForeignKey("torneios.id"), nullable=False)
    fase = Column(SQLEnum(Fase), nullable=False)
    jogador1_id = Column(Integer, ForeignKey("competidores.id"), nullable=False)
    jogador2_id = Column(Integer, ForeignKey("competidores.id"), nullable=True)
    data_hora = Column(DateTime, nullable=True)
    local = Column(String, nullable=True)
    resultado = Column(SQLEnum(Resultado), nullable=False, default=Resultado.PENDENTE)
    vencedor_id = Column(Integer, ForeignKey("competidores.id"), nullable=True)
    observacoes = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    torneio = relationship("Torneio", back_populates="partidas")
    jogador1 = relationship("Competidor", foreign_keys=[jogador1_id], back_populates="partidas_j1")
    jogador2 = relationship("Competidor", foreign_keys=[jogador2_id], back_populates="partidas_j2")
    vencedor = relationship("Competidor", foreign_keys=[vencedor_id], back_populates="vitorias")


DATABASE_URL = "sqlite:///./torneio_xadrez.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
