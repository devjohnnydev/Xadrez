import csv
from models import init_db, SessionLocal, Partida, Competidor
from datetime import datetime

def exportar_partidas_csv(torneio_id: int = None, filename: str = None):
    init_db()
    db = SessionLocal()
    
    if filename is None:
        filename = f"partidas_agendadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        query = db.query(Partida)
        if torneio_id:
            query = query.filter(Partida.torneio_id == torneio_id)
        
        query = query.filter(Partida.data_hora.isnot(None))
        partidas = query.all()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'torneio_id', 'fase', 'ordem',
                'jogador1_nome', 'jogador1_telefone',
                'jogador2_nome', 'jogador2_telefone',
                'data_hora', 'local', 'resultado', 'vencedor_nome', 'observacoes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for partida in partidas:
                jogador1 = db.query(Competidor).filter(Competidor.id == partida.jogador1_id).first()
                jogador2 = db.query(Competidor).filter(Competidor.id == partida.jogador2_id).first() if partida.jogador2_id else None
                vencedor = db.query(Competidor).filter(Competidor.id == partida.vencedor_id).first() if partida.vencedor_id else None
                
                writer.writerow({
                    'torneio_id': partida.torneio_id,
                    'fase': partida.fase.value,
                    'ordem': partida.ordem or '',
                    'jogador1_nome': jogador1.nome if jogador1 else '',
                    'jogador1_telefone': jogador1.telefone if jogador1 else '',
                    'jogador2_nome': jogador2.nome if jogador2 else 'BYE',
                    'jogador2_telefone': jogador2.telefone if jogador2 else '',
                    'data_hora': partida.data_hora.strftime('%Y-%m-%d %H:%M') if partida.data_hora else '',
                    'local': partida.local or '',
                    'resultado': partida.resultado.value,
                    'vencedor_nome': vencedor.nome if vencedor else '',
                    'observacoes': partida.observacoes or ''
                })
        
        print(f"✅ {len(partidas)} partidas exportadas para {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao exportar partidas: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    torneio_id = None
    if len(sys.argv) > 1:
        try:
            torneio_id = int(sys.argv[1])
            print(f"📋 Exportando partidas do torneio {torneio_id}...")
        except ValueError:
            print("❌ ID do torneio inválido. Use: python export_csv.py [torneio_id]")
            sys.exit(1)
    else:
        print("📋 Exportando todas as partidas agendadas...")
    
    exportar_partidas_csv(torneio_id)
