from models import init_db, SessionLocal, Competidor, Periodo, DiasSemana

def seed_competidores():
    init_db()
    db = SessionLocal()
    
    competidores_exemplo = [
        {
            "nome": "Enner David Mamani Quispe",
            "curso": "LOG T1",
            "telefone": "11 96549-8578",
            "periodo": Periodo.MANHA,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        },
        {
            "nome": "Wellington de Jesus Andrade",
            "curso": "LOG T1",
            "telefone": "11 94849-0469",
            "periodo": Periodo.MANHA,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        },
        {
            "nome": "Vitor Antonio J. de Souza",
            "curso": "DEV S4",
            "telefone": "11 94947-9289",
            "periodo": Periodo.TARDE,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        },
        {
            "nome": "Cesar Henry Villalobos Gutierrez",
            "curso": "LOG F1",
            "telefone": "11 94882-9588",
            "periodo": Periodo.TARDE,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        },
        {
            "nome": "Nicoly Kelly Villalba Gonsalez",
            "curso": "2BT 4-6E",
            "telefone": "11 94880-6988",
            "periodo": Periodo.TARDE,
            "dias_semana": DiasSemana.QUARTA_E_SEXTA
        },
        {
            "nome": "Gabriel Pedro de Souza",
            "curso": "DEV SESI 4",
            "telefone": "11 98316-1432",
            "periodo": Periodo.INTEGRAL,
            "dias_semana": DiasSemana.SEGUNDA_E_TERCA
        },
        {
            "nome": "Antonio Carlos Coelho Cajutio",
            "curso": "AUTOCAD/Excel",
            "telefone": "11 99264-3674",
            "periodo": Periodo.TARDE,
            "dias_semana": DiasSemana.SEXTA
        },
        {
            "nome": "Maria Silva Santos",
            "curso": "LOG T2",
            "telefone": "11 98765-4321",
            "periodo": Periodo.MANHA,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        },
        {
            "nome": "João Pedro Oliveira",
            "curso": "DEV S3",
            "telefone": "11 97654-3210",
            "periodo": Periodo.TARDE,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        },
        {
            "nome": "Ana Carolina Ferreira",
            "curso": "LOG T3",
            "telefone": "11 96543-2109",
            "periodo": Periodo.INTEGRAL,
            "dias_semana": DiasSemana.SEGUNDA_A_SEXTA
        }
    ]
    
    try:
        for comp_data in competidores_exemplo:
            competidor = Competidor(**comp_data)
            db.add(competidor)
        
        db.commit()
        print(f"✅ {len(competidores_exemplo)} competidores adicionados com sucesso!")
        
        total = db.query(Competidor).count()
        print(f"📊 Total de competidores no banco: {total}")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar competidores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_competidores()
