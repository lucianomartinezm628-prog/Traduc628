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
        if not text:
            return ""
        # Eliminar números entre corchetes tipo [1] o [Page 2]
        clean_text = re.sub(r'\[.*?\]', '', text)
        # Eliminar puntuación latina básica para tokenización limpia
        clean_text = re.sub(r'[;,\.]', '', clean_text)
        # Normalizar espacios
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        self.source_text = clean_text
        return clean_text

    def p8_a_analisis_lexico(self):
        """Protocolo 8.A: Tokenización y Registro Inicial."""
        if not self.source_text:
            return "No hay texto fuente cargado."
        
        tokens = self.source_text.split(' ')
        nuevos = 0
        for i, token in enumerate(tokens):
            if not token: continue # Saltar vacíos
            
            if token not in self.glossary:
                # Protocolo 1.A.4: Clasificación inicial básica
                # Si tiene más de 3 letras asumimos NUCLEO por defecto, si no PARTICULA
                categoria = "PARTICULA" if len(token) < 4 else "NUCLEO"
                self.glossary[token] = {
                    "token_src": token,
                    "token_tgt": "", 
                    "categoria": categoria,
                    "status": "PENDIENTE",
                    "ocurrencias": [i]
                }
                nuevos += 1
            else:
                self.glossary[token]["ocurrencias"].append(i)
                
        self.status = "P8_A_COMPLETO"
        return f"Análisis P8.A completado. {nuevos} términos nuevos registrados."

    def p8_ia_autocompletar(self, api_key):
        """
        Usa IA para sugerir traducciones a los núcleos vacíos (PENDIENTE).
        """
        try:
            import google.generativeai as genai
        except ImportError:
            return "Error: Librería google-generativeai no instalada en requirements.txt"

        # Filtrar solo lo que falta por traducir
        terminos_vacios = [k for k, v in self.glossary.items() if v['token_tgt'] == ""]
        
        if not terminos_vacios:
            return "El glosario ya está completo."

        # Configurar la IA
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Actúa como un Traductor Isomórfico Estricto.
        Traduce estas palabras del Latín al Español.
        REGLAS:
        1. Literalidad etimológica.
        2. Un solo término (1:1).
        3. Formato: token=traducción
        
        LISTA:
        {", ".join(terminos_vacios)}
        """

        try:
            response = model.generate_content(prompt)
            texto_respuesta = response.text
            contador = 0
            
            for linea in texto_respuesta.split('\n'):
                if "=" in linea:
                    parts = linea.split("=")
                    token = parts[0].strip()
                    trad = parts[1].strip()
                    
                    if token in self.glossary and self.glossary[token]['token_tgt'] == "":
                        self.glossary[token]['token_tgt'] = trad
                        self.glossary[token]['status'] = "SUGERIDO_IA"
                        contador += 1
            
            return f"IA completó {contador} términos."
            
        except Exception as e:
            return f"Error IA: {str(e)}"

    def p3_traduccion(self):
        """Protocolo 3: Core (Control de Flujo)."""
        # Protocolo 2.3: Verificación de Integridad
        faltantes = [k for k, v in self.glossary.items() if v['status'] == 'PENDIENTE' and v['categoria'] == 'NUCLEO' and v['token_tgt'] == ""]
        
        if faltantes:
            # FALLO CRÍTICO si hay núcleos vacíos
            raise ProtocoloError(f"REGISTRO INCOMPLETO: {faltantes[:5]}... (Total: {len(faltantes)})")

        tokens = self.source_text.split(' ')
        self.mtx_t = []

        for token in tokens:
            if not token: continue
            
            entry = self.glossary.get(token)
            if not entry:
                # Caso raro: token no estaba en glosario (ej. modificado post-analisis)
                self.mtx_t.append(f"{{{token}}}")
                continue

            if entry['categoria'] == 'NUCLEO':
                val = entry['token_tgt'] if entry['token_tgt'] else f"{{{token}}}"
                self.mtx_t.append(val)
            else:
                # Partículas: Si está vacía, se deja el original entre llaves o se aplica lógica P5
                val = entry['token_tgt'] if entry['token_tgt'] else f"[{token}]"
                self.mtx_t.append(val)

        self.status = "TRADUCIDO"
        return "CORE-OK: Traducción terminada."

    def p10_b_renderizado(self):
        """Protocolo 10.B: Post-procesamiento."""
        return " ".join(self.mtx_t)
