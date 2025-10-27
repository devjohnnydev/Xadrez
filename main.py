from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import csv
import io
import shutil
import os
from pathlib import Path

from models import (
    init_db, get_db, Competidor, Torneio, Partida,
    Periodo, StatusTorneio, Fase, Resultado
)
from tournament import executar_sorteio, avancar_vencedor, verificar_compatibilidades
from availability import sao_compativeis
from auth import verificar_admin, verificar_credenciais, criar_cookie_sessao, limpar_cookie_sessao

app = FastAPI(title="Torneio de Xadrez SENAI - Morvan Figueiredo")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()


class CompetidorCreate(BaseModel):
    nome: str
    curso: str
    telefone: str
    periodo: Periodo
    dias_semana: str


class CompetidorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nome: str
    curso: str
    telefone: str
    periodo: str
    dias_semana: str
    foto_url: Optional[str]


class TorneioCreate(BaseModel):
    nome: str


class TorneioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nome: str
    status: str
    seed: Optional[int]
    created_at: datetime


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
    jogador1_foto: Optional[str]
    jogador2_nome: Optional[str]
    jogador2_foto: Optional[str]
    data_hora: Optional[datetime]
    local: Optional[str]
    resultado: str
    vencedor_nome: Optional[str]
    observacoes: Optional[str]
    ordem: Optional[int]
    is_bye: bool


class LoginRequest(BaseModel):
    email: str
    senha: str


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("public.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/login")
async def fazer_login(login_data: LoginRequest, response: Response):
    """Endpoint para fazer login"""
    if not verificar_credenciais(login_data.email, login_data.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )
    
    criar_cookie_sessao(response, login_data.email)
    return {"message": "Login realizado com sucesso", "email": login_data.email}


@app.post("/api/logout")
async def fazer_logout(response: Response):
    """Endpoint para fazer logout"""
    limpar_cookie_sessao(response)
    return {"message": "Logout realizado com sucesso"}


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    """Área administrativa - requer autenticação"""
    try:
        admin_email = verificar_admin(request)
        torneios = db.query(Torneio).order_by(Torneio.created_at.desc()).all()
        return templates.TemplateResponse("admin.html", {"request": request, "torneios": torneios, "admin": admin_email})
    except HTTPException:
        # Se não autenticado, redireciona para login
        return RedirectResponse(url="/login", status_code=302)


@app.post("/api/competidores", response_model=CompetidorResponse)
def criar_competidor(request: Request, comp: CompetidorCreate, db: Session = Depends(get_db)):
    verificar_admin(request)
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


@app.post("/api/competidores/form")
async def criar_competidor_form(
    request: Request,
    nome: str = Form(...),
    curso: str = Form(...),
    telefone: str = Form(...),
    periodo: str = Form(...),
    dias_semana: str = Form(...),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    verificar_admin(request)
    foto_url = None
    if foto and foto.filename:
        upload_dir = Path("static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = os.path.splitext(foto.filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{nome.replace(' ', '_')}{file_extension}"
        file_path = upload_dir / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        
        foto_url = f"/static/uploads/{filename}"
    
    novo_comp = Competidor(
        nome=nome,
        curso=curso,
        telefone=telefone,
        periodo=Periodo(periodo),
        dias_semana=dias_semana,
        foto_url=foto_url
    )
    db.add(novo_comp)
    db.commit()
    db.refresh(novo_comp)
    return {"id": novo_comp.id, "nome": novo_comp.nome, "foto_url": foto_url}


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
        query = query.filter(Competidor.dias_semana.contains(dias_semana))
    
    return query.all()


@app.post("/api/importar")
async def importar_csv(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    verificar_admin(request)
    contents = await file.read()
    decoded = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    importados = 0
    erros = []
    
    for row in csv_reader:
        try:
            periodo_str = row['periodo'].strip().lower()
            dias_str = row.get('dias_semana', '').strip()
            
            if not dias_str:
                dias_str = "seg,ter,qua,qui,sex"
            
            periodo = Periodo(periodo_str)
            
            competidor = Competidor(
                nome=row['nome'].strip(),
                curso=row['curso'].strip(),
                telefone=row['telefone'].strip(),
                periodo=periodo,
                dias_semana=dias_str
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
def criar_torneio(request: Request, torneio: TorneioCreate, db: Session = Depends(get_db)):
    verificar_admin(request)
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


@app.get("/api/competidores/compatibilidade")
def verificar_compatibilidade_competidores(request: Request, db: Session = Depends(get_db)):
    verificar_admin(request)
    competidores = db.query(Competidor).all()
    if len(competidores) < 2:
        return {"error": "É necessário pelo menos 2 competidores"}
    return verificar_compatibilidades(competidores)


@app.post("/api/torneios/{torneio_id}/sorteio")
def sortear_torneio(request: Request, torneio_id: int, seed: Optional[int] = None, force: bool = False, db: Session = Depends(get_db)):
    verificar_admin(request)
    resultado = executar_sorteio(db, torneio_id, seed, force)
    if "error" in resultado:
        if "compatibilidade" in resultado:
            return JSONResponse(
                status_code=400,
                content=resultado
            )
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
            jogador1_foto=jogador1.foto_url if jogador1 else None,
            jogador2_nome=jogador2.nome if jogador2 else None,
            jogador2_foto=jogador2.foto_url if jogador2 else None,
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
def atualizar_partida(request: Request, partida_id: int, update: PartidaUpdate, db: Session = Depends(get_db)):
    verificar_admin(request)
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    if update.vencedor_id is not None:
        if partida.data_hora is None:
            raise HTTPException(
                status_code=400, 
                detail="Não é possível registrar resultado sem agendar a partida primeiro"
            )
        
        agora = datetime.now()
        if partida.data_hora > agora:
            raise HTTPException(
                status_code=400,
                detail=f"A partida ainda não aconteceu. Data agendada: {partida.data_hora.strftime('%d/%m/%Y %H:%M')}"
            )
    
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
                "curso": campeao.curso,
                "foto_url": campeao.foto_url
            },
            "finalizado": True
        }
    
    return {"campeao": None, "finalizado": False}


@app.delete("/api/competidores/{competidor_id}")
def deletar_competidor(request: Request, competidor_id: int, db: Session = Depends(get_db)):
    verificar_admin(request)
    competidor = db.query(Competidor).filter(Competidor.id == competidor_id).first()
    if not competidor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    db.delete(competidor)
    db.commit()
    return {"success": True}


@app.get("/api/campeoes")
def listar_campeoes(db: Session = Depends(get_db)):
    """Lista todos os campeões de torneios finalizados"""
    torneios_finalizados = db.query(Torneio).filter(
        Torneio.status == StatusTorneio.FINALIZADO
    ).order_by(Torneio.created_at.desc()).all()
    
    campeoes = []
    for torneio in torneios_finalizados:
        partida_final = db.query(Partida).filter(
            Partida.torneio_id == torneio.id,
            Partida.fase == Fase.FINAL
        ).first()
        
        if partida_final and partida_final.vencedor_id:
            campeao = db.query(Competidor).filter(Competidor.id == partida_final.vencedor_id).first()
            if campeao:
                campeoes.append({
                    "torneio_id": torneio.id,
                    "torneio_nome": torneio.nome,
                    "torneio_data": torneio.created_at,
                    "campeao_id": campeao.id,
                    "campeao_nome": campeao.nome,
                    "campeao_curso": campeao.curso,
                    "campeao_foto": campeao.foto_url
                })
    
    return campeoes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
