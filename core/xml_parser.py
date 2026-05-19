import xml.etree.ElementTree as ET
import hashlib
import os
import re
from typing import Dict, Any, Optional

def compute_file_hash(filepath: str) -> str:
    """Calcula o hash MD5 de um arquivo para detectar modificações."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def strip_namespaces(xml_data: str) -> str:
    """Remove namespaces do XML para facilitar a busca de tags sem prefixos/URLs."""
    # Remove declarações xmlns="..." e xmlns:xsi="..." etc
    xml_data = re.sub(r'\sxmlns="[^"]+"', '', xml_data)
    xml_data = re.sub(r'\sxmlns:\w+="[^"]+"', '', xml_data)
    xml_data = re.sub(r'\sxsi:\w+="[^"]+"', '', xml_data)
    
    # Remove prefixos de tags, ex: <nfe:infNFe> -> <infNFe>, </nfe:infNFe> -> </infNFe>
    # Mas sem quebrar URLs em tags de conteúdo se existirem
    xml_data = re.sub(r'<(\/)?\w+:(\w+)', r'<\1\2', xml_data)
    return xml_data

def parse_xml_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Lê e extrai metadados essenciais de um arquivo XML de NF-e, NFC-e ou CT-e.
    Retorna um dicionário com os campos ou None se o arquivo for inválido.
    """
    if not os.path.exists(filepath):
        return None
        
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
            
        clean_content = strip_namespaces(raw_content)
        root = ET.fromstring(clean_content)
        
        # Determinar se é NF-e/NFC-e ou CT-e
        # NF-e/NFC-e possuem tags como <infNFe> ou <NFe>. CT-e possui <infCte> ou <CTe>.
        is_cte = root.find(".//infCte") is not None or root.tag == "CTe" or "CTe" in root.tag
        
        if is_cte:
            return parse_cte(root, filepath, raw_content)
        else:
            # Assumimos NF-e/NFC-e
            return parse_nfe(root, filepath, raw_content)
            
    except Exception as e:
        print(f"Erro ao processar o XML {filepath}: {e}")
        return None

def parse_nfe(root: ET.Element, filepath: str, raw_content: str) -> Dict[str, Any]:
    """Faz o parsing de uma NF-e ou NFC-e."""
    # 1. Chave de acesso
    chave = None
    # Tenta achar no protNFe
    ch_el = root.find(".//chNFe")
    if ch_el is not None:
        chave = ch_el.text
    else:
        # Tenta achar no atributo Id do infNFe (ex: Id="NFe351908...")
        inf_nfe = root.find(".//infNFe")
        if inf_nfe is not None and 'Id' in inf_nfe.attrib:
            id_val = inf_nfe.attrib['Id']
            # Remove o prefixo "NFe" para obter os 44 números
            chave = id_val.replace("NFe", "") if id_val.startswith("NFe") else id_val
            
    # Se ainda assim não achar, tenta regex na chave do XML bruto
    if not chave:
        match = re.search(r'chNFe>(\d{44})<', raw_content)
        if match:
            chave = match.group(1)
        else:
            # Caso extremo: tenta obter a chave pelo atributo Id no XML limpo
            match_id = re.search(r'Id="NFe(\d{44})"', clean_xml_attributes(raw_content))
            if match_id:
                chave = match_id.group(1)
                
    if not chave:
        # Se não há chave de acesso, usamos o nome do arquivo/hash para não quebrar, mas idealmente precisa
        chave = f"SEM_CHAVE_{compute_file_hash(filepath)}"

    # 2. Dados de Ide
    ide = root.find(".//ide")
    numero = None
    serie = None
    modelo = None
    data_emissao = None
    tipo_nf = None
    
    if ide is not None:
        n_el = ide.find("nNF")
        if n_el is not None:
            numero = int(n_el.text) if n_el.text.isdigit() else None
            
        s_el = ide.find("serie")
        if s_el is not None:
            serie = int(s_el.text) if s_el.text.isdigit() else None
            
        m_el = ide.find("mod")
        if m_el is not None:
            modelo = int(m_el.text) if m_el.text.isdigit() else None
            
        # dhEmi (NF-e v3/v4) ou dEmi (NF-e v2)
        d_el = ide.find("dhEmi")
        if d_el is None:
            d_el = ide.find("dEmi")
        if d_el is not None:
            data_emissao = d_el.text
            
        # tipo_nf (tpNF): 0=Entrada, 1=Saída
        tp_el = ide.find("tpNF")
        if tp_el is not None:
            tipo_nf = int(tp_el.text) if tp_el.text in ('0', '1') else None

    # 3. Emitente
    emit = root.find(".//emit")
    cnpj_emit = None
    nome_emit = None
    if emit is not None:
        cn_el = emit.find("CNPJ")
        if cn_el is None:
            cn_el = emit.find("CPF")
        if cn_el is not None:
            cnpj_emit = cn_el.text
            
        nm_el = emit.find("xNome")
        if nm_el is not None:
            nome_emit = nm_el.text

    # 4. Destinatário
    dest = root.find(".//dest")
    cnpj_dest = None
    nome_dest = None
    if dest is not None:
        cn_el = dest.find("CNPJ")
        if cn_el is None:
            cn_el = dest.find("CPF")
        if cn_el is not None:
            cnpj_dest = cn_el.text
            
        nm_el = dest.find("xNome")
        if nm_el is not None:
            nome_dest = nm_el.text

    # 5. Valor Total
    valor_total = 0.0
    total = root.find(".//total")
    if total is not None:
        icms_tot = total.find("ICMSTot")
        if icms_tot is not None:
            v_el = icms_tot.find("vNF")
            if v_el is not None:
                try:
                    valor_total = float(v_el.text)
                except ValueError:
                    valor_total = 0.0

    return {
        "chave_acesso": chave,
        "numero": numero,
        "serie": serie,
        "modelo": modelo or 55, # Default para NF-e se vazio
        "data_emissao": data_emissao,
        "cnpj_emitente": cnpj_emit,
        "nome_emitente": nome_emit,
        "cnpj_destinatario": cnpj_dest,
        "nome_destinatario": nome_dest,
        "valor_total": valor_total,
        "tipo_nf": tipo_nf,
        "caminho_arquivo": os.path.abspath(filepath),
        "hash_arquivo": compute_file_hash(filepath),
        "tags": None
    }

def parse_cte(root: ET.Element, filepath: str, raw_content: str) -> Dict[str, Any]:
    """Faz o parsing de um CT-e."""
    # 1. Chave de acesso
    chave = None
    ch_el = root.find(".//chCTe")
    if ch_el is not None:
        chave = ch_el.text
    else:
        inf_cte = root.find(".//infCte")
        if inf_cte is not None and 'Id' in inf_cte.attrib:
            id_val = inf_cte.attrib['Id']
            chave = id_val.replace("CTe", "") if id_val.startswith("CTe") else id_val
            
    if not chave:
        match = re.search(r'chCTe>(\d{44})<', raw_content)
        if match:
            chave = match.group(1)
            
    if not chave:
        chave = f"SEM_CHAVE_{compute_file_hash(filepath)}"

    # 2. Dados de Ide
    ide = root.find(".//ide")
    numero = None
    serie = None
    modelo = None
    data_emissao = None
    
    if ide is not None:
        n_el = ide.find("nCT")
        if n_el is not None:
            numero = int(n_el.text) if n_el.text.isdigit() else None
            
        s_el = ide.find("serie")
        if s_el is not None:
            serie = int(s_el.text) if s_el.text.isdigit() else None
            
        m_el = ide.find("mod")
        if m_el is not None:
            modelo = int(m_el.text) if m_el.text.isdigit() else None
            
        d_el = ide.find("dhEmi")
        if d_el is not None:
            data_emissao = d_el.text

    # 3. Emitente
    emit = root.find(".//emit")
    cnpj_emit = None
    nome_emit = None
    if emit is not None:
        cn_el = emit.find("CNPJ")
        if cn_el is None:
            cn_el = emit.find("CPF")
        if cn_el is not None:
            cnpj_emit = cn_el.text
            
        nm_el = emit.find("xNome")
        if nm_el is not None:
            nome_emit = nm_el.text

    # 4. Destinatário
    dest = root.find(".//dest")
    cnpj_dest = None
    nome_dest = None
    if dest is not None:
        cn_el = dest.find("CNPJ")
        if cn_el is None:
            cn_el = dest.find("CPF")
        if cn_el is not None:
            cnpj_dest = cn_el.text
            
        nm_el = dest.find("xNome")
        if nm_el is not None:
            nome_dest = nm_el.text
            
    # Se dest não existe no CT-e (tomador pode ser outro), tenta achar tomador
    if not cnpj_dest:
        toma = root.find(".//toma3")
        if toma is None:
            toma = root.find(".//toma4")
        if toma is not None:
            cn_el = toma.find("CNPJ")
            if cn_el is None:
                cn_el = toma.find("CPF")
            if cn_el is not None:
                cnpj_dest = cn_el.text
                nome_dest = "Tomador do Serviço"

    # 5. Valor Total
    valor_total = 0.0
    v_prest = root.find(".//vPrest")
    if v_prest is not None:
        v_t_el = v_prest.find("vTPrest")
        if v_t_el is not None:
            try:
                valor_total = float(v_t_el.text)
            except ValueError:
                valor_total = 0.0

    return {
        "chave_acesso": chave,
        "numero": numero,
        "serie": serie,
        "modelo": modelo or 57, # Default para CT-e se vazio
        "data_emissao": data_emissao,
        "cnpj_emitente": cnpj_emit,
        "nome_emitente": nome_emit,
        "cnpj_destinatario": cnpj_dest,
        "nome_destinatario": nome_dest,
        "valor_total": valor_total,
        "tipo_nf": None, # CT-e não tem Entrada/Saída na mesma acepção da NF-e
        "caminho_arquivo": os.path.abspath(filepath),
        "hash_arquivo": compute_file_hash(filepath),
        "tags": None
    }

def clean_xml_attributes(xml_data: str) -> str:
    """Helper simples para remover espaçamentos adicionais em atributos."""
    return re.sub(r'\s+', ' ', xml_data)
