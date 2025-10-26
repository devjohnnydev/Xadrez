from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import csv
import io

from models import (
    init_db, get_db, Competidor, Torneio, Partida,
    Periodo, DiasSemana, StatusTorneio, Fase, Resultado
)
from tournament import executar_sorteio, avancar_vencedor
from availability import sao_compativeis

app = FastAPI(title="Torneio de Xadrez SENAI - Morvan Figueiredo")

templates = Jinja2Templates(directory="templates")

init_db()


class CompetidorCreate(BaseModel):
    nome: str
    curso: str
    telefone: str
    periodo: Periodo
    dias_semana: DiasSemana


class CompetidorResponse(BaseModel):
    id: int
    nome: str
    curso: str
    telefone: str
    periodo: str
    dias_semana: str

    class Config:
        from_attributes = True


class TorneioCreate(BaseModel):
    nome: str


class TorneioResponse(BaseModel):
    id: int
    nome: str
    status: str
    seed: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class PartidaUpdate(BaseModel):
    data_hora: Optional[datetime] = None
    local: Optional[str] = None
    resultado: Optional[Resultado] = None
    vencedor_id: Optional[int] = None
    observacoes: Optional[str] = None


class PartidaResponse(BaseModel):
    id: int
    torneio_id: int
    fase: str
    jogador1_nome: str
    jogador2_nome: Optional[str]
    data_hora: Optional[datetime]
    local: Optional[str]
    resultado: str
    vencedor_nome: Optional[str]
    observacoes: Optional[str]
    ordem: Optional[int]
    is_bye: bool


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    torneios = db.query(Torneio).order_by(Torneio.created_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "torneios": torneios})


@app.post("/api/competidores", response_model=CompetidorResponse)
def criar_competidor(comp: CompetidorCreate, db: Session = Depends(get_db)):
    novo_comp = Competidor(
        nome=comp.nome,
        curso=comp.curso,
        telefone=comp.telefone,
        periodo=comp.periodo,
        dias_semana=comp.dias_semana
    )
    db.add(novo_comp)
    db.commit()
    db.refresh(novo_comp)
    return novo_comp


@app.get("/api/competidores", response_model=List[CompetidorResponse])
def listar_competidores(
    periodo: Optional[str] = None,
    dias_semana: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Competidor)
    
    if periodo:
        query = query.filter(Competidor.periodo == periodo)
    if dias_semana:
        query = query.filter(Competidor.dias_semana == dias_semana)
    
    return query.all()


@app.post("/api/importar")
async def importar_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    decoded = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    importados = 0
    erros = []
    
    for row in csv_reader:
        try:
            periodo_str = row['periodo'].strip().lower()
            dias_str = row['dias_semana'].strip().lower()
            
            periodo = Periodo(periodo_str)
            dias_semana = DiasSemana(dias_str)
            
            competidor = Competidor(
                nome=row['nome'].strip(),
                curso=row['curso'].strip(),
                telefone=row['telefone'].strip(),
                periodo=periodo,
                dias_semana=dias_semana
            )
            db.add(competidor)
            importados += 1
        except Exception as e:
            erros.append(f"Erro na linha {row}: {str(e)}")
    
    db.commit()
    
    return {
        "importados": importados,
        "erros": erros
    }


@app.post("/api/torneios", response_model=TorneioResponse)
def criar_torneio(torneio: TorneioCreate, db: Session = Depends(get_db)):
    novo_torneio = Torneio(
        nome=torneio.nome,
        status=StatusTorneio.RASCUNHO
    )
    db.add(novo_torneio)
    db.commit()
    db.refresh(novo_torneio)
    return novo_torneio


@app.get("/api/torneios", response_model=List[TorneioResponse])
def listar_torneios(db: Session = Depends(get_db)):
    return db.query(Torneio).order_by(Torneio.created_at.desc()).all()


@app.post("/api/torneios/{torneio_id}/sorteio")
def sortear_torneio(torneio_id: int, seed: Optional[int] = None, db: Session = Depends(get_db)):
    resultado = executar_sorteio(db, torneio_id, seed)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado


@app.get("/api/torneios/{torneio_id}/partidas")
def listar_partidas(torneio_id: int, db: Session = Depends(get_db)):
    partidas = db.query(Partida).filter(Partida.torneio_id == torneio_id).order_by(Partida.fase, Partida.ordem).all()
    
    resultado = []
    for partida in partidas:
        jogador1 = db.query(Competidor).filter(Competidor.id == partida.jogador1_id).first()
        jogador2 = db.query(Competidor).filter(Competidor.id == partida.jogador2_id).first() if partida.jogador2_id else None
        vencedor = db.query(Competidor).filter(Competidor.id == partida.vencedor_id).first() if partida.vencedor_id else None
        
        resultado.append(PartidaResponse(
            id=partida.id,
            torneio_id=partida.torneio_id,
            fase=partida.fase.value,
            jogador1_nome=jogador1.nome if jogador1 else "N/A",
            jogador2_nome=jogador2.nome if jogador2 else None,
            data_hora=partida.data_hora,
            local=partida.local,
            resultado=partida.resultado.value,
            vencedor_nome=vencedor.nome if vencedor else None,
            observacoes=partida.observacoes,
            ordem=partida.ordem,
            is_bye=partida.jogador2_id is None
        ))
    
    return resultado


@app.patch("/api/partidas/{partida_id}")
def atualizar_partida(partida_id: int, update: PartidaUpdate, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    if update.data_hora is not None:
        partida.data_hora = update.data_hora
    if update.local is not None:
        partida.local = update.local
    if update.resultado is not None:
        partida.resultado = update.resultado
    if update.observacoes is not None:
        partida.observacoes = update.observacoes
    
    db.commit()
    
    if update.vencedor_id is not None:
        resultado = avancar_vencedor(db, partida_id, update.vencedor_id)
        return resultado
    
    return {"success": True}


@app.get("/api/torneios/{torneio_id}/campeao")
def obter_campeao(torneio_id: int, db: Session = Depends(get_db)):
    torneio = db.query(Torneio).filter(Torneio.id == torneio_id).first()
    if not torneio:
        raise HTTPException(status_code=404, detail="Torneio não encontrado")
    
    if torneio.status != StatusTorneio.FINALIZADO:
        return {"campeao": None, "finalizado": False}
    
    partida_final = db.query(Partida).filter(
        Partida.torneio_id == torneio_id,
        Partida.fase == Fase.FINAL
    ).first()
    
    if partida_final and partida_final.vencedor_id:
        campeao = db.query(Competidor).filter(Competidor.id == partida_final.vencedor_id).first()
        return {
            "campeao": {
                "id": campeao.id,
                "nome": campeao.nome,
                "curso": campeao.curso
            },
            "finalizado": True
        }
    
    return {"campeao": None, "finalizado": False}


@app.delete("/api/competidores/{competidor_id}")
def deletar_competidor(competidor_id: int, db: Session = Depends(get_db)):
    competidor = db.query(Competidor).filter(Competidor.id == competidor_id).first()
    if not competidor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    db.delete(competidor)
    db.commit()
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
