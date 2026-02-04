import re

class ProtocoloError(Exception):
    """Protocolo 0.5: Error que detiene el proceso hasta intervención."""
    pass

class STI_Core:
    def __init__(self):
        self.glossary = {}  # Protocolo 8
        self.source_text = ""
        self.mtx_t = []     # Protocolo 3: Mtx_T
        self.status = "ESPERA"

    def p10_a_limpieza(self, text):
        """Protocolo 10.A: Filtro de ruido y normalización."""
        clean_text = re.sub(r'\d+', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        self.source_text = clean_text
        return clean_text

        # ... (código anterior) ...

    def p8_ia_autocompletar(self, api_key):
        """
        Usa IA para sugerir traducciones a los núcleos vacíos (PENDIENTE).
        Respeta Protocolo 4: Jerarquía Etimológica.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            return "Error: Librería google-generativeai no instalada."

        # Filtrar solo lo que falta por traducir
        terminos_vacios = [k for k, v in self.glossary.items() if v['token_tgt'] == ""]
        
        if not terminos_vacios:
            return "El glosario ya está completo."

        # Configurar la IA
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Prompt estricto basado en tus Protocolos
        prompt = f"""
        Actúa como un Traductor Isomórfico Estricto (Protocolo 4).
        Tu tarea es traducir la siguiente lista de palabras del Latín al Español.
        
        REGLAS INVIOLABLES:
        1. Literalidad extrema y etimológica.
        2. Un solo término en español por cada término en latín (1:1).
        3. Mantén la categoría gramatical (Sustantivo->Sustantivo, Verbo->Verbo).
        4. NO uses sinónimos ni parafrasees.
        5. Formato de salida estricto: token_origen=traducción
        
        LISTA A TRADUCIR:
        {", ".join(terminos_vacios)}
        """

        try:
            response = model.generate_content(prompt)
            # Procesar respuesta de la IA
            texto_respuesta = response.text
            contador = 0
            
            for linea in texto_respuesta.split('\n'):
                if "=" in linea:
                    parts = linea.split("=")
                    token = parts[0].strip()
                    trad = parts[1].strip()
                    
                    # Solo actualizamos si el token existe y está vacío
                    if token in self.glossary and self.glossary[token]['token_tgt'] == "":
                        self.glossary[token]['token_tgt'] = trad
                        self.glossary[token]['status'] = "SUGERIDO_IA" # Nuevo estado temporal
                        contador += 1
            
            return f"IA completó {contador} términos. Por favor, revísalos."
            
        except Exception as e:
            return f"Error al conectar con la IA: {str(e)}"


    def p3_traduccion(self):
        """Protocolo 3: Core (Control de Flujo)."""
        # Protocolo 2.3: Prohibido avanzar sin registro completo
        faltantes = [k for k, v in self.glossary.items() if v['status'] == 'PENDIENTE' and v['categoria'] == 'NUCLEO']
        if faltantes:
            raise ProtocoloError(f"REGISTRO INCOMPLETO: {faltantes}")

        tokens = self.source_text.split(' ')
        self.mtx_t = []

        for token in tokens:
            entry = self.glossary.get(token)
            if entry['categoria'] == 'NUCLEO':
                # Protocolo 1.A.7: Paridad léxica 1:1
                self.mtx_t.append(entry['token_tgt'])
            else:
                # Protocolo 5: Correspondencia funcional para partículas
                val = entry['token_tgt'] if entry['token_tgt'] else f"{{{token}}}"
                self.mtx_t.append(val)

        self.status = "TRADUCIDO"
        return "CORE-OK: Traducción terminada."

    def p10_b_renderizado(self):
        """Protocolo 10.B: Post-procesamiento."""
        return " ".join(self.mtx_t)
