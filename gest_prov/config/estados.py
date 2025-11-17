from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Estado(BaseModel):
    """
    Representa el estado compartido que fluye a través del grafo de agentes.
    Cada campo es opcional porque se va llenando a medida que los agentes completan su trabajo.
    """

    solicitud_usuario: str = Field(description='Solicitud del usuario')

    lista_proveedores: Optional[List[Dict[str, Any]]] = Field(default=None, description="Lista de proveedores.")

    sentimientos: Optional[List[Dict[str, Any]]] = Field(default=None, description="Sentimiento de los clientes hacia el proveedor determinado mediante el analisis de sus opiniones.")

    info_general: Optional[List[Dict[str, Any]]] = Field(default=None, description="Contiene informacion de metodos de pago y principales promociones del proveedor con respecto al producto buscado.")

    calificaciones: Optional[List[Dict[str, Any]]] = Field(default=None, description="Base final con la lista de proveedores, atributos y calificaciones.")

    historial_pasos: Optional[list[str]] = Field(default=None, description="Historial de los pasos que se van ejecutando en el grafo.")



