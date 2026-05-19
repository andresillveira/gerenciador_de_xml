import os
import random
import uuid
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

def generate_cnpj():
    """Gera um CNPJ fictício válido apenas em termos de formato."""
    return f"{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(100, 999)}0001{random.randint(10, 99)}"

def generate_access_key(model, cnpj):
    """Gera uma chave de acesso fictícia de 44 dígitos."""
    state = "35" # São Paulo
    year_month = "2605" # Maio de 2026
    mod = str(model).zfill(2)
    serie = str(random.randint(1, 9)).zfill(3)
    number = str(random.randint(1, 999999)).zfill(9)
    tp_emiss = "1"
    numeric_code = str(random.randint(10000000, 99999999))
    dv = str(random.randint(0, 9))
    
    key = f"{state}{year_month}{cnpj}{mod}{serie}{number}{tp_emiss}{numeric_code}{dv}"
    return key[:44]

def generate_nfe_xml(filepath, key, number, model, date_str, emit_cnpj, dest_cnpj, value):
    """Escreve um XML fictício de NF-e ou NFC-e."""
    # Estrutura básica simplificada compatível com nosso parser
    root = ET.Element("nfeProc", xmlns="http://www.portalfiscal.inf.br/nfe")
    
    nfe = ET.SubModel = ET.SubElement(root, "NFe")
    inf_nfe = ET.SubElement(nfe, "infNFe", Id=f"NFe{key}")
    
    # ide
    ide = ET.SubElement(inf_nfe, "ide")
    ET.SubElement(ide, "mod").text = str(model)
    ET.SubElement(ide, "nNF").text = str(number)
    ET.SubElement(ide, "serie").text = str(random.randint(1, 9))
    ET.SubElement(ide, "dhEmi").text = date_str
    ET.SubElement(ide, "tpNF").text = str(random.choice([0, 1])) # Entrada ou Saída
    
    # emit
    emit = ET.SubElement(inf_nfe, "emit")
    ET.SubElement(emit, "CNPJ").text = emit_cnpj
    ET.SubElement(emit, "xNome").text = f"EMITENTE COMERCIAL LTDA - {random.randint(1, 5)}"
    
    # dest
    dest = ET.SubElement(inf_nfe, "dest")
    ET.SubElement(dest, "CNPJ").text = dest_cnpj
    ET.SubElement(dest, "xNome").text = f"CLIENTE DESTINATARIO SA - {random.randint(1, 10)}"
    
    # det (itens de produto)
    for i in range(1, random.randint(2, 6)):
        det = ET.SubElement(inf_nfe, "det", nItem=str(i))
        prod = ET.SubElement(det, "prod")
        ET.SubElement(prod, "cProd").text = f"PROD{random.randint(100, 999)}"
        ET.SubElement(prod, "xProd").text = f"PRODUTO INDUSTRIALIZADO MODELO {chr(64 + i)}"
        q_com = random.randint(1, 10)
        v_un = round(random.uniform(5.0, 150.0), 2)
        ET.SubElement(prod, "qCom").text = f"{q_com:.4f}"
        ET.SubElement(prod, "uCom").text = "UN"
        ET.SubElement(prod, "vUnCom").text = f"{v_un:.4f}"
        ET.SubElement(prod, "vProd").text = f"{(q_com * v_un):.2f}"
    
    # total
    total = ET.SubElement(inf_nfe, "total")
    icms_tot = ET.SubElement(total, "ICMSTot")
    ET.SubElement(icms_tot, "vNF").text = f"{value:.2f}"
    
    # protNFe
    prot = ET.SubElement(root, "protNFe")
    inf_prot = ET.SubElement(prot, "infProt")
    ET.SubElement(inf_prot, "chNFe").text = key
    ET.SubElement(inf_prot, "cStat").text = "100" # Autorizado
    
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(filepath, encoding="utf-8", xml_declaration=True)

def generate_cte_xml(filepath, key, number, model, date_str, emit_cnpj, dest_cnpj, value):
    """Escreve um XML fictício de CT-e."""
    root = ET.Element("cteProc", xmlns="http://www.portalfiscal.inf.br/cte")
    
    cte = ET.SubElement(root, "CTe")
    inf_cte = ET.SubElement(cte, "infCte", Id=f"CTe{key}")
    
    # ide
    ide = ET.SubElement(inf_cte, "ide")
    ET.SubElement(ide, "mod").text = str(model)
    ET.SubElement(ide, "nCT").text = str(number)
    ET.SubElement(ide, "serie").text = str(random.randint(1, 9))
    ET.SubElement(ide, "dhEmi").text = date_str
    
    # emit
    emit = ET.SubElement(inf_cte, "emit")
    ET.SubElement(emit, "CNPJ").text = emit_cnpj
    ET.SubElement(emit, "xNome").text = f"TRANSPORTADORA RAPIDA LTDA - {random.randint(1, 3)}"
    
    # dest
    dest = ET.SubElement(inf_cte, "dest")
    ET.SubElement(dest, "CNPJ").text = dest_cnpj
    ET.SubElement(dest, "xNome").text = f"DESTINATARIO DA CARGA SA - {random.randint(1, 10)}"
    
    # vPrest
    v_prest = ET.SubElement(inf_cte, "vPrest")
    ET.SubElement(v_prest, "vTPrest").text = f"{value:.2f}"
    
    # Componentes
    comp1 = ET.SubElement(v_prest, "comp")
    ET.SubElement(comp1, "xNome").text = "FRETE PESO"
    ET.SubElement(comp1, "vComp").text = f"{(value * 0.8):.2f}"
    comp2 = ET.SubElement(v_prest, "comp")
    ET.SubElement(comp2, "xNome").text = "GRIS"
    ET.SubElement(comp2, "vComp").text = f"{(value * 0.2):.2f}"
    
    # protCTe
    prot = ET.SubElement(root, "protCTe")
    inf_prot = ET.SubElement(prot, "infProt")
    ET.SubElement(inf_prot, "chCTe").text = key
    ET.SubElement(inf_prot, "cStat").text = "100"
    
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(filepath, encoding="utf-8", xml_declaration=True)

def generate_mass_xmls(output_dir: str, count: int = 10000):
    """Gera milhares de arquivos XML de teste."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Gerando {count} XMLs de teste em: {output_dir}...")
    
    cnpj_pool = [generate_cnpj() for _ in range(15)]
    
    base_date = datetime.now()
    
    for i in range(1, count + 1):
        if i % 1000 == 0:
            print(f"-> {i} XMLs gerados...")
            
        model = random.choice([55, 65, 57])
        emit_cnpj = random.choice(cnpj_pool[:5])
        dest_cnpj = random.choice(cnpj_pool[5:])
        
        # Garante CNPJs diferentes
        while dest_cnpj == emit_cnpj:
            dest_cnpj = random.choice(cnpj_pool[5:])
            
        key = generate_access_key(model, emit_cnpj)
        number = random.randint(100, 999999)
        
        # Espalhar datas nos últimos 90 dias
        delta_days = random.randint(0, 90)
        delta_hours = random.randint(0, 23)
        delta_mins = random.randint(0, 59)
        date = base_date - timedelta(days=delta_days, hours=delta_hours, minutes=delta_mins)
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        
        value = round(random.uniform(10.0, 5000.0), 2)
        
        filename = f"XML_{model}_{number}_{key[:10]}.xml"
        filepath = os.path.join(output_dir, filename)
        
        if model in (55, 65):
            generate_nfe_xml(filepath, key, number, model, date_str, emit_cnpj, dest_cnpj, value)
        else:
            generate_cte_xml(filepath, key, number, model, date_str, emit_cnpj, dest_cnpj, value)
            
    print(f"Sucesso! {count} arquivos XML gerados em '{output_dir}'.")

if __name__ == "__main__":
    import sys
    out = "./xmls_teste"
    cnt = 5000
    if len(sys.argv) > 1:
        out = sys.argv[1]
    if len(sys.argv) > 2:
        cnt = int(sys.argv[2])
    generate_mass_xmls(out, cnt)
