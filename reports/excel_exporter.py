import pandas as pd
import os
from typing import List, Dict, Any

def export_to_excel(documents: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Exporta uma lista de documentos fiscais filtrados para uma planilha Excel formatada (.xlsx).
    """
    if not documents:
        return False
        
    try:
        # 1. Converter lista de dicts para DataFrame do Pandas com colunas limpas
        data = []
        for doc in documents:
            modelo = doc.get("modelo")
            mod_str = "NF-e (55)" if modelo == 55 else "NFC-e (65)" if modelo == 65 else "CT-e (57)" if modelo == 57 else str(modelo)
            
            tipo = doc.get("tipo_nf")
            tipo_str = "Entrada" if tipo == 0 else "Saída" if tipo == 1 else "N/A"
            
            data.append({
                "Chave de Acesso": doc.get("chave_acesso"),
                "Modelo": mod_str,
                "Número": doc.get("numero"),
                "Série": doc.get("serie"),
                "Tipo": tipo_str,
                "Data Emissão": doc.get("data_emissao"),
                "CNPJ Emitente": doc.get("cnpj_emitente"),
                "Nome Emitente": doc.get("nome_emitente"),
                "CNPJ Destinatário": doc.get("cnpj_destinatario"),
                "Nome Destinatário": doc.get("nome_destinatario"),
                "Valor Total (R$)": doc.get("valor_total"),
                "Caminho do Arquivo": doc.get("caminho_arquivo")
            })
            
        df = pd.DataFrame(data)
        
        # 2. Exportar para Excel usando openpyxl para estilização básica
        # Se for arquivo .csv, exporta como CSV
        if output_path.lower().endswith('.csv'):
            df.to_csv(output_path, index=False, encoding='utf-8-sig', sep=';')
            return True
            
        # Gravar Excel com formatações
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="XMLs Exportados")
            
            # Ajustar tamanho das colunas automaticamente
            workbook = writer.book
            worksheet = writer.sheets["XMLs Exportados"]
            
            for col in worksheet.columns:
                max_len = 0
                col_letter = col[0].column_letter
                for cell in col:
                    val_str = str(cell.value or '')
                    if len(val_str) > max_len:
                        max_len = len(val_str)
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 10)
                
        return True
    except Exception as e:
        print(f"Erro ao exportar planilha Excel: {e}")
        return False
