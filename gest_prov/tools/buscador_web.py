from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import logging

# Get a logger instance for this module
logger = logging.getLogger(__name__)

@tool
def duckduckgo_search_tool(query: str) -> str:
    """
    Util para buscar en internet información relevante usando DuckDuckGo.
    No requiere API Key y es ideal para búsquedas generales.
    """
    logger.info(f"Ejecutando búsqueda en DuckDuckGo con la consulta: '{query}'")

    try:
        search = DuckDuckGoSearchRun()
        resultados = search.run(query)

        if not resultados:
            logger.info(f"La búsqueda de DuckDuckGo para '{query}' no devolvió resultados.")
            return "No se encontraron resultados con DuckDuckGo."

        logger.info(f"Búsqueda de DuckDuckGo exitosa para '{query}'.")
        return resultados

    except Exception as e:
        logger.error(f"Error inesperado al realizar la búsqueda con DuckDuckGo para '{query}': {e}", exc_info=True)
        return f"Error al realizar la búsqueda con DuckDuckGo: {e}"