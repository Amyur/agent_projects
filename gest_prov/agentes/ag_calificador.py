import os
import logging
import json
import langchain
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
langchain.debug = True # Enable global LangChain debug mode
from pydantic import BaseModel, Field
from typing import Optional
from langchain_anthropic.chat_models import ChatAnthropic
from config.retry import reintentar
from config.estados import Estado
from langchain.agents import create_agent



#Formato de salida
class Calificaciones(BaseModel):
    pagina_web: str = Field(description="Es la pagina web proporcionada.")
    sentimiento: Optional[str] = Field(default=None, description="Sentimiento de las opiniones hacia el proveedor")
    calif_sentimiento : Optional[int] = Field(default=None, description="Calificacion del sentimiento de las opiniones hacia el proveedor")
    metodos_pago: Optional[str] = Field(default=None, description="Metodos de pago que dispone el proveedor en su pagina web.")
    calif_metodos_pago : Optional[int] = Field(default=None, description="Calificacion de los Metodos de pago que dispone el proveedor en su pagina web.")
    principales_promociones: Optional[str] = Field(default=None, description="Principales promociones que tiene el proveedor en relacion al producto buscado en su pagina web.")
    calif_promociones : Optional[int] = Field(default=None, description="Calificacion de las Principales promociones que tiene el proveedor en relacion al producto buscado en su pagina web.")
    calificacion_total: Optional[int] = Field(default=None, description="Es la calificacion total de sumar calif_sentimiento, calif_metodos_pago y calif_promociones.")

class ListaCalificaciones(BaseModel):
    calificaciones : list[Calificaciones] = Field(description="Lista de atributos y su respectiva calificacion")

class AgenteCalificador:

    def __init__(self):
        """
        Modelo llm 
        """
        self.llm = ChatAnthropic(model="claude-haiku-4-5-20251001", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, state:Estado) -> Estado:

        # Consolidar y formatear los datos del estado en un string JSON
        datos_consolidados = {
            "proveedores": state.lista_proveedores,
            "sentimientos_opiniones": state.sentimientos,
            "informacion_general": state.info_general
        }
        info_str = json.dumps(datos_consolidados, indent=2, ensure_ascii=False)

        system_prompt="""

            Eres experto en calificar unos atributos de unos proveedores.
            Te voy a proporcionar un objeto JSON con la información de proveedores y diferentes atributos, los cuales debes calificar siguiendo las
            siguientes indicaciones:
            1)Calificar el sentimiento de 1 a 3, donde 1 es sentimiento negativo, 2 neutro y 3 positivo.
            2)Calificar metodos de pago, de 1 a 5, donde 1 es poca variedad de metodos de pago y 5 es mucha variedad
            3)Calificar las promociones, de 1 a 5, donde 1 es que las promociones son muy malas y 5 que las promociones son muy buenas.
            4)Sumar las calificaciones anteriores, si no hay una calificacion, ignorarla y sumar donde si haya calificacion.

            Restricciones: 
            1)Si no encuentras algun dato, no lo inventes ni lo supongas, deja el campo vacio como ultima opcion.
            
            """
        
        agente = create_agent(self.llm, tools=[], system_prompt=system_prompt, response_format=ListaCalificaciones)

        # Pasar el string JSON como petición al agente
        raw_output = reintentar(agente=agente, peticion=info_str, output=ListaCalificaciones)

        info_general = raw_output["structured_response"].calificaciones
                                                                                            
        output = [p.model_dump() for p in info_general]

        #pasos         
        historial_anterior = state.historial_pasos or []
        historial_actualizado = historial_anterior + ["clasificador"]
        print(historial_actualizado)
        

        new_state = {
            **state.model_dump(),
            "calificaciones": output,
            "historial_pasos": historial_actualizado
        }
        
        return new_state
