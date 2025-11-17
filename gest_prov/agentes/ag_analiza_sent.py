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
class Sentimiento(BaseModel):
    proveedor: str = Field(description="Proveedor que vende el producto buscado")
    categoria_sentimiento: Optional[str] = Field(default=None, description="Categoria de sentimiento atribuido al analizar las opiniones de los clientes de los proveedores. Por ejemplo: Positivo")

class ListaSentimiento(BaseModel):
    proveedores : list[Sentimiento] = Field(description="Lista de proveedores con sentimiento")

class AgenteBuscaSentimiento:

    def __init__(self):
        """
        Modelo llm 
        """
        self.llm = ChatAnthropic(model="claude-haiku-4-5-20251001", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, state:Estado) -> Estado:

        proveedores = [item["proveedor"] for item in state.lista_proveedores]

        system_prompt="""

            Eres un experto en analisis de sentimiento.
            Te voy a proporcionar una lista de proveedores.
            Tu tarea es buscar en la web las diferentes opiniones que los clientes le han realizado a los proveedores.

            Tener en cuenta que la fecha de hoy es 16-11-2025.

            Debes clasificar el sentimiento encontrado en las opiniones por proveedor de la siguiente manera:
            Negativo: Si las opiniones son negativas.
            Neutro: Si las opiniones son neutras.
            Positivo: Si las opciones son positivas.

            Restricciones: 
            1)Solo puedes hacer maximo 3 busquedas web por cada proveedor.
            2)Si no encuentras algun dato, no lo inventes ni lo supongas, deja el campo vacio como ultima opcion.

            Utiliza la herramienta 'duckduckgo_search_tool' para encontrar la información en la web.
            
            """
        
        agente = create_agent(self.llm, tools=[duckduckgo_search_tool], system_prompt=system_prompt, response_format=ListaSentimiento)

        raw_output = reintentar(agente=agente, peticion=proveedores, output=ListaSentimiento)

        proveedores = raw_output["structured_response"].proveedores

        #Extract the list of providers from the structured response                                                                                              
        output = [p.model_dump() for p in proveedores]

        #pasos         
        historial_anterior = state.historial_pasos or []
        historial_actualizado = historial_anterior + ["buscar_sentimiento"]
        print(historial_actualizado)
        

        new_state = {
            **state.model_dump(),
            "sentimientos": output,
            "historial_pasos": historial_actualizado
        }
        
        return new_state
