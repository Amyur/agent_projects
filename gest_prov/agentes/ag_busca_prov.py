import os
import logging
import langchain
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
langchain.debug = True # Enable global LangChain debug mode
from pydantic import BaseModel, Field
from langchain_anthropic.chat_models import ChatAnthropic
from config.retry import reintentar
from config.estados import Estado
from langchain.agents import create_agent
from tools.buscador_web import duckduckgo_search_tool
from datetime import date



#Formato de salida
class Proveedores(BaseModel):
    proveedor: str = Field(description="Proveedor que vende el producto buscado")
    pagina_web: str = Field(description="Pagina web del proveedor")

class ListaProveedores(BaseModel):
    proveedores : list[Proveedores] = Field(description="Lista de maximo 3 proveedores con su respectiva pagina web")

class AgenteBuscaProveedores:

    def __init__(self):
        """
        Modelo llm 
        """
        self.llm = ChatAnthropic(model="claude-3-5-haiku-20241022", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, state:Estado) -> Estado:

        solicitud = state.solicitud_usuario

        system_prompt="""

            Eres un experto en búsqueda de proveedores de el producto que se solicite. 

            Tener en cuenta que la fecha de hoy es {date.today()}

            Tu tarea es encontrar 3 proveedores relevantes según la solicitud del usuario.

            Restricciones:
            1)Si no encuentras algun dato, no lo inventes ni lo supongas, deja el campo vacio como ultima opcion.
            2)Haz solo una busqueda web para encontrar todo lo solicitado.

            Utiliza la herramienta 'duckduckgo_search_tool' para encontrar la información más actualizada.
            
            """
        
        agente = create_agent(self.llm, tools=[duckduckgo_search_tool], system_prompt=system_prompt, response_format=ListaProveedores)

        raw_output = reintentar(agente=agente, peticion=solicitud, output=ListaProveedores)

        proveedores = raw_output["structured_response"].proveedores

        #Extract the list of providers from the structured response                                                                                              
        output = [p.model_dump() for p in proveedores]

        #pasos         
        historial_anterior = state.historial_pasos or []
        historial_actualizado = historial_anterior + ["buscar_lista_proveedores"]
        print(historial_actualizado)
        

        new_state = {
            **state.model_dump(),
            "lista_proveedores": output,
            "historial_pasos": historial_actualizado
        }
        
        return new_state


