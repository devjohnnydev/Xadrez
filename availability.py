from typing import Set
from models import Competidor, DiasSemana, Periodo


def mapear_dias(dias_semana: DiasSemana) -> Set[str]:
    mapeamento = {
        DiasSemana.SEGUNDA_A_SEXTA: {"seg", "ter", "qua", "qui", "sex"},
        DiasSemana.SEGUNDA_E_TERCA: {"seg", "ter"},
        DiasSemana.QUARTA_E_SEXTA: {"qua", "sex"},
        DiasSemana.SEXTA: {"sex"},
    }
    return mapeamento[dias_semana]


def mapear_periodos(periodo: Periodo) -> Set[str]:
    mapeamento = {
        Periodo.MANHA: {"manha"},
        Periodo.TARDE: {"tarde"},
        Periodo.INTEGRAL: {"manha", "tarde"},
    }
    return mapeamento[periodo]


def sao_compativeis(comp1: Competidor, comp2: Competidor) -> bool:
    dias1 = mapear_dias(comp1.dias_semana)
    dias2 = mapear_dias(comp2.dias_semana)
    
    periodos1 = mapear_periodos(comp1.periodo)
    periodos2 = mapear_periodos(comp2.periodo)
    
    intersecao_dias = dias1.intersection(dias2)
    intersecao_periodos = periodos1.intersection(periodos2)
    
    return len(intersecao_dias) > 0 and len(intersecao_periodos) > 0


def obter_chave_disponibilidade(comp: Competidor) -> str:
    dias = mapear_dias(comp.dias_semana)
    periodos = mapear_periodos(comp.periodo)
    dias_str = "-".join(sorted(dias))
    periodos_str = "-".join(sorted(periodos))
    return f"{periodos_str}_{dias_str}"
