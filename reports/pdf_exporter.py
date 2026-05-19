import os
from typing import Optional
# Tenta importar da biblioteca brazilfiscalreport
try:
    from brazilfiscalreport.danfe import Danfe
    from brazilfiscalreport.dacte import Dacte
    BFR_AVAILABLE = True
except ImportError:
    BFR_AVAILABLE = False
    print("Aviso: brazilfiscalreport não está instalado corretamente ou suas dependências estão ausentes.")

def generate_pdf_from_xml(xml_path: str, model: int, output_pdf_path: str) -> bool:
    """
    Gera um arquivo PDF oficial (DANFE/DACTE) a partir de um arquivo XML
    usando a biblioteca brazilfiscalreport.
    """
    if not os.path.exists(xml_path):
        print(f"Erro: Arquivo XML não encontrado em {xml_path}")
        return False
        
    if not BFR_AVAILABLE:
        print("Erro: brazilfiscalreport não está disponível.")
        return False
        
    try:
        if model in (55, 65): # NF-e ou NFC-e
            # Inicializa o gerador DANFE da brazilfiscalreport
            danfe = Danfe(xml=xml_path)
            danfe.output(output_pdf_path)
            return True
        elif model == 57: # CT-e
            # Inicializa o gerador DACTE
            dacte = Dacte(xml=xml_path)
            dacte.output(output_pdf_path)
            return True
        else:
            print(f"Modelo {model} não suportado para geração de PDF oficial.")
            return False
            
    except Exception as e:
        print(f"Erro ao gerar PDF para {xml_path} (Modelo {model}): {e}")
        # Fallback simples em caso de falha de layout da biblioteca
        return False
