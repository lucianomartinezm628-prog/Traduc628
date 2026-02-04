import re

class ProtocoloError(Exception):
    """Para Fallos Críticos definidos en el documento."""
    pass

class STI_Core:
    def __init__(self):
        # Estado del sistema
        self.glossary = {}  # Estructura P8
        self.source_text = ""
        self.mtx_s = []     # Matriz Fuente (P3)
        self.mtx_t = []     # Matriz Target (P3)
        self.status = "ESPERA" # Fases: ESPERA, P8_A, TRADUCCION, FINAL

    def p10_a_limpieza(self, text):
        [span_0](start_span)"""PROTOCOLO 10.A: Limpieza y Normalización[span_0](end_span)"""
        # Eliminar números de página y ruido simple
        clean_text = re.sub(r'\d+', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        self.source_text = clean_text
        return clean_text

    def p8_a_analisis_lexico(self):
        [span_1](start_span)"""PROTOCOLO 8.A: Tokenización y Registro Inicial[span_1](end_span)"""
        if not self.source_text:
            return "No hay texto cargado."
            
        # Tokenización simple (espacios)
        tokens = self.source_text.split(' ')
        
        # Registro en glosario (Estado PENDIENTE por defecto)
        for i, token in enumerate(tokens):
            if token not in self.glossary:
                # Determinamos si es núcleo o partícula (simulado)
                # En un caso real, esto requeriría una base de datos morfológica
                categoria = "PARTICULA" if len(token) < 4 else "NUCLEO"
                
                self.glossary[token] = {
                    "token_src": token,
                    "token_tgt": "", # Vacío inicialmente
                    "categoria": categoria,
                    [span_2](start_span)"status": "PENDIENTE", #[span_2](end_span)
                    "ocurrencias": [i]
                }
            else:
                self.glossary[token]["ocurrencias"].append(i)
        
        self.status = "P8_A_COMPLETO"
        return "Análisis P8.A completado. Glosario generado."

    def verificar_integridad_glosario(self):
        [span_3](start_span)"""Verifica FALLO CRÍTICO por registro incompleto[span_3](end_span)"""
        faltantes = [k for k, v in self.glossary.items() if v['status'] == 'PENDIENTE' and v['categoria'] == 'NUCLEO']
        if faltantes:
            return False, f"FALLO CRÍTICO: Núcleos sin definir: {faltantes}"
        return True, "Glosario Sellado."

    def p3_traduccion(self):
        [span_4](start_span)"""PROTOCOLO 3: Core de Traducción[span_4](end_span)"""
        # 1. Verificar integridad antes de arrancar
        ok, msg = self.verificar_integridad_glosario()
        if not ok:
            raise ProtocoloError(msg)

        tokens = self.source_text.split(' ')
        self.mtx_t = []

        for i, token in enumerate(tokens):
            entry = self.glossary.get(token)
            
            # [span_5](start_span)P4: Núcleos (Invariables)[span_5](end_span)
            if entry['categoria'] == 'NUCLEO':
                traduccion = entry['token_tgt']
                self.mtx_t.append(traduccion)
            
            # [span_6](start_span)P5: Partículas (Polivalentes/Automáticas)[span_6](end_span)
            else:
                # Si el usuario no definió la partícula, el sistema "decide" (simulado)
                if entry['token_tgt'] == "":
                    # Aquí iría la lógica compleja de P5. 
                    # Simulación: devolver el token original entre corchetes si no hay data
                    self.mtx_t.append(f"[{token}]") 
                else:
                    self.mtx_t.append(entry['token_tgt'])

        self.status = "TRADUCIDO"
        return "Traducción P3 completada."

    def p10_b_renderizado(self):
        [span_7](start_span)"""PROTOCOLO 10.B: Salida[span_7](end_span)"""
        # Serialización manteniendo isomorfismo
        return " ".join(self.mtx_t)
