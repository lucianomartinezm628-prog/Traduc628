import re

class ProtocoloError(Exception):
    """Error crítico que detiene el flujo."""
    pass

class STI_Core:
    def __init__(self):
        self.glossary = {} 
        self.source_text = ""
        self.mtx_t = []     
        self.status = "ESPERA"

    def p10_a_limpieza(self, text):
        """Limpieza P10.A"""
        if not text: return ""
        # Limpiar referencias tipo [1] o [Page 2]
        clean = re.sub(r'\[.*?\]', '', text)
        # Limpiar puntuación básica
        clean = re.sub(r'[;,\.]', '', clean)
        # Normalizar espacios
        clean = re.sub(r'\s+', ' ', clean).strip()
        self.source_text = clean
        return clean

    def p8_a_analisis_lexico(self):
        """Análisis P8.A"""
        if not self.source_text:
            return "No hay texto fuente."
        
        tokens = self.source_text.split(' ')
        nuevos = 0
        for i, token in enumerate(tokens):
            if not token: continue
            
            if token not in self.glossary:
                cat = "PARTICULA" if len(token) < 4 else "NUCLEO"
                self.glossary[token] = {
                    "token_src": token,
                    "token_tgt": "", 
                    "categoria": cat,
                    "status": "PENDIENTE",
                    "ocurrencias": [i]
                }
                nuevos += 1
            else:
                self.glossary[token]["ocurrencias"].append(i)
        
        self.status = "P8_A_COMPLETO"
        return f"Análisis completado. {nuevos} términos nuevos."

    def p8_ia_autocompletar(self, api_key):
        """Autocompletado IA"""
        try:
            import google.generativeai as genai
        except ImportError:
            return "Error: Falta google-generativeai en requirements.txt"

        pendientes = [k for k,v in self.glossary.items() if v['token_tgt'] == ""]
        if not pendientes: return "Glosario ya está completo."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"Traduce del Latín al Español. Literalidad estricta 1:1. Formato: token=traduccion. Lista: {', '.join(pendientes)}"
        
        try:
            res = model.generate_content(prompt)
            count = 0
            for line in res.text.split('\n'):
                if "=" in line:
                    t, trad = line.split("=", 1)
                    t = t.strip()
                    if t in self.glossary:
                        self.glossary[t]['token_tgt'] = trad.strip()
                        self.glossary[t]['status'] = "SUGERIDO_IA"
                        count += 1
            return f"IA completó {count} términos."
        except Exception as e:
            return f"Error IA: {str(e)}"

    def p3_traduccion(self):
        """Core de Traducción P3"""
        # Verificación de integridad
        vacios = [k for k,v in self.glossary.items() if v['categoria'] == 'NUCLEO' and v['token_tgt'] == ""]
        if vacios:
            raise ProtocoloError(f"REGISTRO INCOMPLETO: Faltan {len(vacios)} núcleos (ej: {vacios[:3]}).")

        self.mtx_t = []
        tokens = self.source_text.split(' ')
        
        for token in tokens:
            if not token: continue
            entry = self.glossary.get(token)
            
            if not entry:
                self.mtx_t.append(f"{{{token}}}") # Token desconocido
                continue

            if entry['categoria'] == 'NUCLEO':
                self.mtx_t.append(entry['token_tgt'])
            else:
                # Partícula: Si vacía -> original entre corchetes
                val = entry['token_tgt'] if entry['token_tgt'] else f"[{token}]"
                self.mtx_t.append(val)
        
        self.status = "TRADUCIDO"
        return "Traducción finalizada."

    def p10_b_renderizado(self):
        return " ".join(self.mtx_t)
