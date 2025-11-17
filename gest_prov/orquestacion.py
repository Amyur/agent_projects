from dotenv import load_dotenv
load_dotenv()
from agentes.ag_busca_prov import AgenteBuscaProveedores
from agentes.ag_analiza_sent import AgenteBuscaSentimiento
from agentes.ag_busca_info_gen import AgenteInfoGeneral
from agentes.ag_calificador import AgenteCalificador
from config.estados import Estado
from langgraph.graph import StateGraph, END
import json

# Define los nodos del grafo, donde cada nodo corresponde a la ejecución de un agente.

def nodo_agente_busca_provee(state: Estado):
    """
    Ejecuta el agente que busca proveedores, que inicia el flujo de trabajo.
    """
    agente_busca_provee = AgenteBuscaProveedores()
    salida = agente_busca_provee.run(state)
    return salida

def nodo_agente_busca_sent(state: Estado):
    """
    Ejecuta el agente que busca el sentimiento.
    """
    agente_busca_sent = AgenteBuscaSentimiento()
    salida = agente_busca_sent.run(state)
    return salida

def nodo_agente_info_general(state: Estado):
    """
    Ejecuta el agente que busca el sentimiento.
    """
    agente_info_gen = AgenteInfoGeneral()
    salida = agente_info_gen.run(state)
    return salida

def nodo_agente_calificador(state: Estado):
    """
    Ejecuta el agente que busca el sentimiento.
    """
    agente_calificador = AgenteCalificador()
    salida = agente_calificador.run(state)
    return salida

flujo = StateGraph(Estado)

flujo.add_node("buscar_proveedores", nodo_agente_busca_provee)
flujo.add_node("buscar_sentimiento", nodo_agente_busca_sent)
flujo.add_node("buscar_info_general", nodo_agente_info_general)
flujo.add_node("calificador", nodo_agente_calificador)

flujo.set_entry_point("buscar_proveedores")

flujo.add_edge("buscar_proveedores", "buscar_sentimiento")
flujo.add_edge("buscar_sentimiento", "buscar_info_general")
flujo.add_edge("buscar_info_general", "calificador")
flujo.add_edge("calificador", END)


app = flujo.compile()
salida = app.invoke(Estado(solicitud_usuario="necesito buscar los mejores proveedores de llantas de autos de gama media en medellin, " \
                                          "me interesan aquellos que ofrezcan pago a credito y tengan buenas promociones"))
print(json.dumps(salida, indent=2, ensure_ascii=False))