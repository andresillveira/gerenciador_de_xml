from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, 
    QPushButton, QTabWidget, QFrame, QMessageBox
)
from PySide6.QtGui import QDesktopServices
import os
import tempfile
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any, Optional
from reports.pdf_exporter import generate_pdf_from_xml

class XMLViewer(QFrame):
    """
    Painel de Detalhes à direita.
    Fornece visualização instantânea de metadados, visualização simplificada das tags XML
    com realce de sintaxe e renderização do PDF oficial (DANFE/DACTE) em leitor padrão.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detailFrame")
        self.current_doc: Optional[Dict[str, Any]] = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Título do Painel
        self.title_label = QLabel("Visualização & Detalhes")
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)
        
        # QTabWidget para alternar visualizações
        self.tabs = QTabWidget()
        
        # Aba 1: DANFE / DACTE Simplificado
        self.preview_browser = QTextBrowser()
        self.preview_browser.setOpenExternalLinks(True)
        self.preview_browser.setHtml("<div style='text-align: center; color: #94a3b8; padding-top: 100px;'>Selecione um XML na lista para visualizar</div>")
        
        # Aba 2: Código XML Bruto (Indented)
        self.code_browser = QTextBrowser()
        self.code_browser.setPlainText("Selecione um XML para ver a estrutura de tags.")
        self.code_browser.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; background-color: #1e1e24; color: #f1f5f9;")
        
        self.tabs.addTab(self.preview_browser, "DANFE/DACTE Rápido")
        self.tabs.addTab(self.code_browser, "Código XML (Tags)")
        
        layout.addWidget(self.tabs)
        
        # Botões na parte inferior
        btn_layout = QHBoxLayout()
        
        self.pdf_btn = QPushButton("Abrir PDF Oficial")
        self.pdf_btn.setObjectName("secondaryButton")
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.clicked.connect(self.open_official_pdf)
        
        self.delete_btn = QPushButton("Excluir XML")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setEnabled(False)
        # O sinal para exclusão será capturado pelo main_window
        
        btn_layout.addWidget(self.pdf_btn)
        btn_layout.addWidget(self.delete_btn)
        
        layout.addLayout(btn_layout)

    def load_document(self, doc: Dict[str, Any]):
        """Carrega e exibe um documento fiscal selecionado."""
        self.current_doc = doc
        self.pdf_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        
        # Atualiza títulos
        mod = doc.get("modelo")
        tipo_str = "NF-e" if mod == 55 else "NFC-e" if mod == 65 else "CT-e" if mod == 57 else "Doc Fiscal"
        self.title_label.setText(f"{tipo_str} Nº {doc.get('numero')} - Série {doc.get('serie')}")
        
        # 1. Carrega XML bruto formatado
        self.load_raw_xml(doc.get("caminho_arquivo"))
        
        # 2. Carrega visualização HTML dinâmica rápida (DANFE Simplificado)
        self.load_html_preview(doc)

    def load_raw_xml(self, filepath: str):
        """Lê o XML físico, identa-o lindamente e aplica realce de tags."""
        if not filepath or not os.path.exists(filepath):
            self.code_browser.setPlainText("Erro: Arquivo físico não encontrado.")
            return
            
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Identar XML
            # Remove namespaces apenas para deixar legível
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            root = ET.fromstring(content, parser=parser)
            ET.indent(root, space="  ")
            indented_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')
            
            # Escape de HTML para evitar que QTextBrowser renderize como HTML real
            escaped_xml = (
                indented_xml.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            
            # Regex simples para aplicar cores em tags, atributos e valores no visualizador
            # Realce de tags (ex: &lt;tag&gt; -> &lt;<font color='#6366f1'>tag</font>&gt;)
            highlighted = re_sub_tags(escaped_xml)
            
            self.code_browser.setHtml(f"<pre style='font-family: Consolas, monospace; line-height: 1.4;'>{highlighted}</pre>")
        except Exception as e:
            self.code_browser.setPlainText(f"Erro ao carregar tags: {e}")

    def load_html_preview(self, doc: Dict[str, Any]):
        """Gera e exibe um resumo comercial (DANFE/DACTE) bonito em HTML."""
        xml_path = doc.get("caminho_arquivo")
        
        # Variáveis padrão
        chave = doc.get("chave_acesso")
        # Formata chave com espaços a cada 4 dígitos
        chave_formatted = " ".join(chave[i:i+4] for i in range(0, len(chave), 4))
        
        modelo = doc.get("modelo")
        doc_type = "NOTA FISCAL ELETRÔNICA" if modelo == 55 else "NOTA FISCAL DE CONSUMIDOR ELETRÔNICA" if modelo == 65 else "CONHECIMENTO DE TRANSPORTE ELETRÔNICO" if modelo == 57 else "DOCUMENTO FISCAL"
        
        valor_total = doc.get("valor_total") or 0.0
        valor_total_str = f"R$ {valor_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        
        tipo_nf = doc.get("tipo_nf")
        tipo_str = "ENTRADA" if tipo_nf == 0 else "SAÍDA" if tipo_nf == 1 else "N/A"
        
        data_emi = doc.get("data_emissao") or ""
        if len(data_emi) >= 10:
            data_emi = f"{data_emi[8:10]}/{data_emi[5:7]}/{data_emi[:4]}"
            
        emit_cnpj = format_cnpj_cpf(doc.get("cnpj_emitente"))
        emit_nome = doc.get("nome_emitente") or "Não Informado"
        
        dest_cnpj = format_cnpj_cpf(doc.get("cnpj_destinatario"))
        dest_nome = doc.get("nome_destinatario") or "Não Informado"
        
        # Tenta ler itens do XML real
        items_html = ""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            # Remove namespaces
            xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
            # Remove namespaces na string
            xml_clean = strip_ns_temp(xml_str)
            clean_root = ET.fromstring(xml_clean)
            
            if modelo in (55, 65): # NF-e/NFC-e
                # Elemento <det> contêm itens
                dets = clean_root.findall(".//det")
                if dets:
                    items_html = """
                    <h4 style="margin-top: 16px; color: #4f46e5; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">Produtos / Serviços</h4>
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                        <thead>
                            <tr style="background-color: #f1f5f9; text-align: left; font-weight: bold;">
                                <th style="padding: 4px; border: 1px solid #cbd5e1;">Cód</th>
                                <th style="padding: 4px; border: 1px solid #cbd5e1;">Descrição</th>
                                <th style="padding: 4px; border: 1px solid #cbd5e1; text-align: center;">Qtd</th>
                                <th style="padding: 4px; border: 1px solid #cbd5e1; text-align: center;">Un</th>
                                <th style="padding: 4px; border: 1px solid #cbd5e1; text-align: right;">P. Unit</th>
                                <th style="padding: 4px; border: 1px solid #cbd5e1; text-align: right;">P. Total</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    for det in dets:
                        prod = det.find("prod")
                        if prod is not None:
                            c_prod = prod.find("cProd").text if prod.find("cProd") is not None else ""
                            x_prod = prod.find("xProd").text if prod.find("xProd") is not None else ""
                            q_com = float(prod.find("qCom").text) if prod.find("qCom") is not None else 0.0
                            u_com = prod.find("uCom").text if prod.find("uCom") is not None else ""
                            v_un_com = float(prod.find("vUnCom").text) if prod.find("vUnCom") is not None else 0.0
                            v_prod = float(prod.find("vProd").text) if prod.find("vProd") is not None else 0.0
                            
                            items_html += f"""
                            <tr>
                                <td style="padding: 4px; border: 1px solid #cbd5e1;">{c_prod}</td>
                                <td style="padding: 4px; border: 1px solid #cbd5e1;">{x_prod}</td>
                                <td style="padding: 4px; border: 1px solid #cbd5e1; text-align: center;">{q_com:,.2f}</td>
                                <td style="padding: 4px; border: 1px solid #cbd5e1; text-align: center;">{u_com}</td>
                                <td style="padding: 4px; border: 1px solid #cbd5e1; text-align: right;">{v_un_com:,.2f}</td>
                                <td style="padding: 4px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{v_prod:,.2f}</td>
                            </tr>
                            """
                    items_html += "</tbody></table>"
            elif modelo == 57: # CT-e
                # Serviços de transporte costumam ter valores de prestação e detalhes de carga
                v_prest = clean_root.find(".//vPrest")
                components_html = ""
                if v_prest is not None:
                    comp = v_prest.findall(".//comp")
                    if comp:
                        components_html = "<ul>"
                        for c in comp:
                            nome_c = c.find("xNome").text if c.find("xNome") is not None else "Componente"
                            val_c = float(c.find("vComp").text) if c.find("vComp") is not None else 0.0
                            components_html += f"<li>{nome_c}: R$ {val_c:,.2f}</li>"
                        components_html += "</ul>"
                        
                items_html = f"""
                <h4 style="margin-top: 16px; color: #4f46e5; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">Detalhamento do Frete</h4>
                <div style="font-size: 11px;">
                    {components_html if components_html else "<p>Componentes tarifários detalhados não encontrados no XML.</p>"}
                </div>
                """
        except Exception as e:
            print(f"Erro ao extrair itens para visualização rápida: {e}")
            items_html = "<p style='font-size:11px; color:#ef4444;'>Nota: Não foi possível carregar os itens detalhados deste XML.</p>"

        # Tema-dependente styles para QTextBrowser
        # Como QTextBrowser responde às paletas do Qt, podemos estilizar com background neutro
        # que se integra ao Light/Dark facilmente usando cores relativas.
        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #334155; margin: 0; padding: 10px; background-color: #ffffff; border-radius: 8px;">
            <div style="border: 2px solid #cbd5e1; border-radius: 8px; padding: 16px;">
                
                <!-- Cabeçalho Principal -->
                <div style="text-align: center; border-bottom: 2px solid #4f46e5; padding-bottom: 12px; margin-bottom: 16px;">
                    <span style="font-size: 11px; font-weight: bold; color: #64748b; letter-spacing: 1px;">DOCUMENTO AUXILIAR</span>
                    <h2 style="margin: 4px 0; color: #0f172a; font-size: 18px;">{doc_type}</h2>
                    <table style="width: 100%; font-size: 11px; margin-top: 8px;">
                        <tr>
                            <td><strong>NÚMERO:</strong> {doc.get('numero')}</td>
                            <td><strong>SÉRIE:</strong> {doc.get('serie')}</td>
                            <td><strong>TIPO:</strong> {tipo_str}</td>
                            <td><strong>EMISSÃO:</strong> {data_emi}</td>
                        </tr>
                    </table>
                </div>

                <!-- Chave de Acesso -->
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; text-align: center; margin-bottom: 16px;">
                    <span style="font-size: 10px; font-weight: bold; color: #64748b;">CHAVE DE ACESSO</span>
                    <div style="font-family: monospace; font-size: 13px; font-weight: bold; color: #0f172a; margin-top: 4px; letter-spacing: 0.5px;">{chave_formatted}</div>
                </div>

                <!-- Emitente e Destinatário -->
                <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 16px;">
                    <tr>
                        <td style="width: 50%; padding-right: 10px; vertical-align: top;">
                            <div style="border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; min-height: 80px; background-color: #fdfdfd;">
                                <strong style="color: #4f46e5; font-size: 12px;">EMITENTE</strong><br/>
                                <span style="font-weight: bold; font-size: 11px; color: #1e293b;">{emit_nome}</span><br/>
                                <span style="color: #64748b;">CNPJ/CPF: {emit_cnpj}</span>
                            </div>
                        </td>
                        <td style="width: 50%; padding-left: 10px; vertical-align: top;">
                            <div style="border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; min-height: 80px; background-color: #fdfdfd;">
                                <strong style="color: #4f46e5; font-size: 12px;">DESTINATÁRIO</strong><br/>
                                <span style="font-weight: bold; font-size: 11px; color: #1e293b;">{dest_nome}</span><br/>
                                <span style="color: #64748b;">CNPJ/CPF: {dest_cnpj}</span>
                            </div>
                        </td>
                    </tr>
                </table>

                <!-- Lista de Itens / Detalhes -->
                {items_html}

                <!-- Totais -->
                <div style="margin-top: 16px; text-align: right; border-top: 2px solid #cbd5e1; padding-top: 8px;">
                    <span style="font-size: 12px; font-weight: bold; color: #64748b;">VALOR TOTAL DO DOCUMENTO</span>
                    <div style="font-size: 20px; font-weight: bold; color: #4f46e5; margin-top: 2px;">{valor_total_str}</div>
                </div>
                
            </div>
        </body>
        </html>
        """
        self.preview_browser.setHtml(html)

    def open_official_pdf(self):
        """
        Compila o XML em PDF real usando brazilfiscalreport e abre no visualizador padrão do SO.
        """
        if not self.current_doc:
            return
            
        xml_path = self.current_doc.get("caminho_arquivo")
        modelo = self.current_doc.get("modelo")
        chave = self.current_doc.get("chave_acesso")
        
        # Criar caminho temporário de PDF
        temp_dir = tempfile.gettempdir()
        temp_pdf = os.path.join(temp_dir, f"DANFE_{chave}.pdf")
        
        # Gera o PDF
        ok = generate_pdf_from_xml(xml_path, modelo, temp_pdf)
        
        if ok and os.path.exists(temp_pdf):
            # Abre no visualizador padrão
            QDesktopServices.openUrl(QUrl.fromLocalFile(temp_pdf))
        else:
            QMessageBox.critical(
                self, 
                "Erro na Geração", 
                "Não foi possível gerar o PDF oficial usando brazilfiscalreport.\nVerifique se o XML está completo e é válido."
            )

    def clear(self):
        """Limpa as visualizações."""
        self.current_doc = None
        self.pdf_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.title_label.setText("Visualização & Detalhes")
        self.preview_browser.setHtml("<div style='text-align: center; color: #94a3b8; padding-top: 100px;'>Selecione um XML na lista para visualizar</div>")
        self.code_browser.setPlainText("Selecione um XML para ver a estrutura de tags.")


# Helpers
def strip_ns_temp(xml_str: str) -> str:
    """Helper temporário para remover namespaces."""
    xml_str = re.sub(r'\sxmlns="[^"]+"', '', xml_str)
    xml_str = re.sub(r'\sxmlns:\w+="[^"]+"', '', xml_str)
    xml_str = re.sub(r'\sxsi:\w+="[^"]+"', '', xml_str)
    xml_str = re.sub(r'<(\/)?\w+:(\w+)', r'<\1\2', xml_str)
    return xml_str

def re_sub_tags(escaped_xml: str) -> str:
    """Regex simples para dar cor às tags XML no browser."""
    # Tags de abertura e fechamento
    # &lt;/tag&gt;
    escaped_xml = re.sub(r'&lt;/(\w+)(:)?(\w+)?&gt;', r"&lt;/<font color='#f43f5e'>\1\2\3</font>&gt;", escaped_xml)
    # &lt;tag ... &gt; ou &lt;tag/&gt;
    escaped_xml = re.sub(r'&lt;(\w+)(:)?(\w+)?(\s|/|&gt;)', r"&lt;<font color='#6366f1'>\1\2\3</font>\4", escaped_xml)
    # Atributos (ex: Id="...")
    escaped_xml = re.sub(r'(\s)(\w+)="([^"]+)"', r"\1<font color='#10b981'>\2</font>=<font color='#f59e0b'>\"\3\"</font>", escaped_xml)
    return escaped_xml

def format_cnpj_cpf(val: Optional[str]) -> str:
    """Formata CNPJ ou CPF."""
    if not val:
        return ""
    clean = ''.join(c for c in val if c.isdigit())
    if len(clean) == 14:
        return f"{clean[0:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:14]}"
    elif len(clean) == 11:
        return f"{clean[0:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:11]}"
    return val
