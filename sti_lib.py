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

    def p8_a_analisis_lexico(self):
        """Protocolo 8.A: Tokenización y Registro Inicial."""
        if not self.source_text:
            return "No hay texto fuente."
        
        tokens = self.source_text.split(' ')
        for i, token in enumerate(tokens):
            if token not in self.glossary:
                # Protocolo 1.A.4: Clasificación inicial
                categoria = "PARTICULA" if len(token) < 4 else "NUCLEO"
                self.glossary[token] = {
                    "token_src": token,
                    "token_tgt": "", 
                    "categoria": categoria,
                    "status": "PENDIENTE",
                    "ocurrencias": [i]
                }
        self.status = "P8_A_COMPLETO"
        return "Análisis léxico completado (P8.A)."

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
