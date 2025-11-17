import os
import logging
import langchain
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
langchain.debug = True # Enable global LangChain debug mode
from pydantic import BaseModel, Field
from typing import Optional
from langchain_anthropic.chat_models import ChatAnthropic
from config.retry import reintentar
from config.estados import Estado
from langchain.agents import create_agent
from tools.buscador_web import duckduckgo_search_tool



#Formato de salida
class InfoGeneral(BaseModel):
    pagina_web: str = Field(description="Es la pagina web proporcionada.")
    tel_contacto: Optional[str] = Field(default=None, description="Telefono o celular de contacto del proveedor.")
    direccion: Optional[str] = Field(default=None, description="Direccion del proveedor")
    metodos_pago: Optional[str] = Field(default=None, description="Metodos de pago que dispone el proveedor en su pagina web.")
    principales_promociones: Optional[str] = Field(default=None, description="Principales promociones que tiene el proveedor en relacion al producto buscado en su pagina web.")

class ListaInfoGeneral(BaseModel):
    info_general : list[InfoGeneral] = Field(description="Lista de metodos de pagos y de principales promociones.")

class AgenteInfoGeneral:

    def __init__(self):
        """
        Modelo llm 
        """
        self.llm = ChatAnthropic(model="claude-haiku-4-5-20251001", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, state:Estado) -> Estado:

        pag_web = [item["pagina_web"] for item in state.lista_proveedores]

        system_prompt="""

            Eres un experto en busqueda de informacion web.

            Tener en cuenta que la fecha de hoy es 16-11-2025.
            
            Te voy a proporcionar una lista de paginas web.
            Tu tarea es buscar en la web:
            1)los metodos de pagos.
            2)principales promociones que hay en ellas.
            3)buscar el telefono o celular de contacto.
            4)direccion del proveedor.

            

            Restricciones: 
            1)Si no encuentras algun dato, no lo inventes ni lo supongas, deja el campo vacio como ultima opcion.

            Utiliza la herramienta 'duckduckgo_search_tool' para encontrar la información más actualizada.
            
            """
        
        agente = create_agent(self.llm, tools=[duckduckgo_search_tool], system_prompt=system_prompt, response_format=ListaInfoGeneral)

        raw_output = reintentar(agente=agente, peticion=pag_web, output=ListaInfoGeneral)

        info_general = raw_output["structured_response"].info_general
                                                                                            
        output = [p.model_dump() for p in info_general]

        #pasos         
        historial_anterior = state.historial_pasos or []
        historial_actualizado = historial_anterior + ["buscar_info_general"]
        print(historial_actualizado)
        

        new_state = {
            **state.model_dump(),
            "info_general": output,
            "historial_pasos": historial_actualizado
        }
        
        return new_state
