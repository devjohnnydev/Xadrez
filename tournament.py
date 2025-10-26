import random
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from models import Competidor, Torneio, Partida, Fase, StatusTorneio, Resultado
from availability import sao_compativeis, obter_chave_disponibilidade


def agrupar_por_disponibilidade(competidores: List[Competidor]) -> dict:
    grupos = {}
    for comp in competidores:
        chave = obter_chave_disponibilidade(comp)
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(comp)
    return grupos


def encontrar_par_compativel(jogador: Competidor, disponiveis: List[Competidor]) -> Optional[Competidor]:
    for candidato in disponiveis:
        if sao_compativeis(jogador, candidato):
            return candidato
    return None


def criar_pares(competidores: List[Competidor], seed: Optional[int] = None) -> List[Tuple[Competidor, Optional[Competidor]]]:
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    grupos = agrupar_por_disponibilidade(competidores)
    
    pares = []
    todos_disponiveis = competidores.copy()
    rng.shuffle(todos_disponiveis)
    
    processados = set()
    
    for grupo_chave, grupo in grupos.items():
        grupo_embaralhado = [c for c in grupo if c.id not in processados]
        rng.shuffle(grupo_embaralhado)
        
        while len(grupo_embaralhado) >= 2:
            j1 = grupo_embaralhado.pop(0)
            j2 = grupo_embaralhado.pop(0)
            pares.append((j1, j2))
            processados.add(j1.id)
            processados.add(j2.id)
        
        if grupo_embaralhado:
            jogador_sozinho = grupo_embaralhado[0]
            disponiveis_outros = [c for c in todos_disponiveis if c.id not in processados]
            
            par = encontrar_par_compativel(jogador_sozinho, disponiveis_outros)
            if par:
                pares.append((jogador_sozinho, par))
                processados.add(jogador_sozinho.id)
                processados.add(par.id)
            else:
                pares.append((jogador_sozinho, None))
                processados.add(jogador_sozinho.id)
    
    return pares


def determinar_fase_inicial(num_jogadores: int) -> Fase:
    if num_jogadores <= 2:
        return Fase.FINAL
    elif num_jogadores <= 4:
        return Fase.SEMIFINAL
    elif num_jogadores <= 8:
        return Fase.QUARTAS
    else:
        return Fase.OITAVAS


def executar_sorteio(db: Session, torneio_id: int, seed: Optional[int] = None) -> dict:
    torneio = db.query(Torneio).filter(Torneio.id == torneio_id).first()
    if not torneio:
        return {"error": "Torneio não encontrado"}
    
    competidores = db.query(Competidor).all()
    if len(competidores) < 2:
        return {"error": "É necessário pelo menos 2 competidores para realizar o sorteio"}
    
    pares = criar_pares(competidores, seed)
    
    num_total = len(competidores)
    fase_inicial = determinar_fase_inicial(num_total)
    
    ordem = 1
    partidas_criadas = []
    for j1, j2 in pares:
        partida = Partida(
            torneio_id=torneio_id,
            fase=fase_inicial,
            jogador1_id=j1.id,
            jogador2_id=j2.id if j2 else None,
            ordem=ordem
        )
        db.add(partida)
        partidas_criadas.append(partida)
        ordem += 1
    
    torneio.status = StatusTorneio.SORTEADO
    if seed is not None:
        torneio.seed = seed
    
    db.commit()
    
    for partida in partidas_criadas:
        if partida.jogador2_id is None:
            partida.vencedor_id = partida.jogador1_id
            partida.resultado = Resultado.J1
            db.commit()
            
            if partida.fase != Fase.FINAL:
                avancar_vencedor(db, partida.id, partida.jogador1_id)
    
    return {
        "success": True,
        "torneio_id": torneio_id,
        "fase_inicial": fase_inicial.value,
        "num_partidas": len(pares),
        "num_byes": sum(1 for _, j2 in pares if j2 is None)
    }


def avancar_vencedor(db: Session, partida_id: int, vencedor_id: int) -> dict:
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        return {"error": "Partida não encontrada"}
    
    partida.vencedor_id = vencedor_id
    
    if partida.resultado == "pendente":
        if vencedor_id == partida.jogador1_id:
            partida.resultado = "j1"
        elif vencedor_id == partida.jogador2_id:
            partida.resultado = "j2"
    
    db.commit()
    
    if partida.fase == Fase.FINAL:
        torneio = db.query(Torneio).filter(Torneio.id == partida.torneio_id).first()
        torneio.status = StatusTorneio.FINALIZADO
        db.commit()
        return {"success": True, "campeao_id": vencedor_id, "torneio_finalizado": True}
    
    proxima_fase = obter_proxima_fase(partida.fase)
    if not proxima_fase:
        return {"success": True}
    
    partidas_fase_atual = db.query(Partida).filter(
        Partida.torneio_id == partida.torneio_id,
        Partida.fase == partida.fase
    ).order_by(Partida.ordem).all()
    
    indice_partida = next((i for i, p in enumerate(partidas_fase_atual) if p.id == partida_id), None)
    if indice_partida is None:
        return {"success": True}
    
    indice_proxima = indice_partida // 2
    
    partida_proxima = db.query(Partida).filter(
        Partida.torneio_id == partida.torneio_id,
        Partida.fase == proxima_fase,
        Partida.ordem == indice_proxima + 1
    ).first()
    
    if not partida_proxima:
        partida_proxima = Partida(
            torneio_id=partida.torneio_id,
            fase=proxima_fase,
            jogador1_id=None,
            jogador2_id=None,
            ordem=indice_proxima + 1
        )
        db.add(partida_proxima)
        db.commit()
    
    if indice_partida % 2 == 0:
        partida_proxima.jogador1_id = vencedor_id
    else:
        partida_proxima.jogador2_id = vencedor_id
    
    db.commit()
    
    return {"success": True, "proxima_partida_id": partida_proxima.id}


def obter_proxima_fase(fase_atual: Fase) -> Optional[Fase]:
    ordem = [Fase.OITAVAS, Fase.QUARTAS, Fase.SEMIFINAL, Fase.FINAL]
    try:
        indice_atual = ordem.index(fase_atual)
        if indice_atual < len(ordem) - 1:
            return ordem[indice_atual + 1]
    except ValueError:
        pass
    return None
