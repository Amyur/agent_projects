from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(
        stop=stop_after_attempt(3),  # Intentarlo un máximo de 3 veces
        wait=wait_fixed(2),          # Esperar 2 segundos entre intentos
        retry_error_callback=lambda retry_state: print(f"No se pudo obtener el formato correcto después de {retry_state.attempt_number} intentos.")
    )
def reintentar(agente, peticion: str, output):
    """
    Función que invoca al agente y valida el formato.
    Si la validación falla, tenacity lo reintentará.
    """
    try:
        print("Intentando invocar al agente...")
        raw_output = agente.invoke({"messages": [{"role": "user", "content": peticion}]})
            
        if not isinstance(raw_output.get("structured_response"), output):
            raise TypeError("La respuesta no es del tipo {output}")

        print("Formato correcto obtenido")
        return raw_output

    except (ValidationError, KeyError, TypeError) as e:
        print(f"Error de formato detectado: {e}. Reintentando...")
        raise  