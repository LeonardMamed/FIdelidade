import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTabWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from db import cadastrar_cliente, registrar_compra, usar_pontos_parcial
import win32print
import win32ui

ultimo_recibo = {}

def imprimir_recibo():
    global ultimo_recibo
    if not ultimo_recibo:
        return

    texto = f"""
    --------------------------
       RECIBO DE FIDELIDADE
    --------------------------

    Nome: {ultimo_recibo['nome']}
    CPF: {ultimo_recibo['cpf']}

    Valor da compra: R$ {ultimo_recibo['valor']:.2f}
    Pontos recebidos: {ultimo_recibo.get('pontos_recebidos', 0)}
    Total de pontos: {ultimo_recibo['pontos']}
    Desconto atual: {ultimo_recibo['desconto']}%

    Pontos usados: {ultimo_recibo.get('pontos_usados', 0)}
    Pontos restantes: {ultimo_recibo.get('pontos_restantes', ultimo_recibo['pontos'])}

    Obrigado por comprar com a gente!
    --------------------------
    """

    impressora = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(impressora)
    hJob = win32print.StartDocPrinter(hPrinter, 1, ("Recibo Fidelidade", None, "RAW"))
    win32print.StartPagePrinter(hPrinter)
    win32print.WritePrinter(hPrinter, texto.encode("utf-8"))
    win32print.EndPagePrinter(hPrinter)
    win32print.EndDocPrinter(hPrinter)
    win32print.ClosePrinter(hPrinter)

class AbaCadastroConsulta(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        logo = QLabel()
        pixmap = QPixmap("logo_papa.jpeg").scaledToWidth(180, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        blocos = QHBoxLayout()

        cadastro_layout = QVBoxLayout()
        cadastro_label = QLabel("Cadastro de Cliente")
        cadastro_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome")
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("CPF")
        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.clicked.connect(self.cadastrar_cliente)
        cadastro_layout.addWidget(cadastro_label)
        cadastro_layout.addWidget(self.input_nome)
        cadastro_layout.addWidget(self.input_cpf)
        cadastro_layout.addWidget(btn_cadastrar)

        consulta_layout = QVBoxLayout()
        consulta_label = QLabel("Consulta de Pontos")
        consulta_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.input_cpf_consulta = QLineEdit()
        self.input_cpf_consulta.setPlaceholderText("CPF")
        btn_consultar = QPushButton("Consultar")
        btn_consultar.clicked.connect(self.consultar_pontos)
        self.resultado = QLabel("")
        consulta_layout.addWidget(consulta_label)
        consulta_layout.addWidget(self.input_cpf_consulta)
        consulta_layout.addWidget(btn_consultar)
        consulta_layout.addWidget(self.resultado)

        blocos.addLayout(cadastro_layout)
        blocos.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        blocos.addLayout(consulta_layout)

        layout.addLayout(blocos)
        self.setLayout(layout)

    def cadastrar_cliente(self):
        nome = self.input_nome.text().strip()
        cpf = self.input_cpf.text().strip()
        if not nome or not cpf:
            QMessageBox.warning(self, "Erro", "Preencha nome e CPF.")
            return
        resposta = cadastrar_cliente(nome, cpf)
        if isinstance(resposta, str) and "Erro" in resposta:
            QMessageBox.critical(self, "Erro", resposta)
        else:
            QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso!")
            self.input_nome.clear()
            self.input_cpf.clear()

    def consultar_pontos(self):
        cpf = self.input_cpf_consulta.text().strip()
        try:
            cliente = registrar_compra(cpf, 0)
            if isinstance(cliente, str):
                self.resultado.setText(cliente)
            else:
                self.resultado.setText(f"Pontos: {cliente['pontos']}\nDesconto: {cliente['desconto']}%")
        except Exception as e:
            self.resultado.setText(f"Erro: {str(e)}")

class AbaCompraUso(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        logo = QLabel()
        pixmap = QPixmap("logo_papa.jpeg").scaledToWidth(180, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        linhas = QHBoxLayout()

        usar_layout = QVBoxLayout()
        usar_label = QLabel("Usar Pontos")
        usar_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.input_cpf_usar = QLineEdit()
        self.input_cpf_usar.setPlaceholderText("CPF")
        self.input_pontos_usar = QLineEdit()
        self.input_pontos_usar.setPlaceholderText("Quantos pontos usar")
        btn_usar = QPushButton("Aplicar Desconto")
        btn_usar.clicked.connect(self.usar_pontos)
        self.resultado_uso = QLabel("")
        usar_layout.addWidget(usar_label)
        usar_layout.addWidget(self.input_cpf_usar)
        usar_layout.addWidget(self.input_pontos_usar)
        usar_layout.addWidget(btn_usar)
        usar_layout.addWidget(self.resultado_uso)

        compra_layout = QVBoxLayout()
        compra_label = QLabel("Registrar Compra")
        compra_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.input_cpf_compra = QLineEdit()
        self.input_cpf_compra.setPlaceholderText("CPF")
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Valor da compra")
        btn_salvar = QPushButton("Salvar Pontos")
        btn_salvar.clicked.connect(self.salvar_compra)
        self.btn_imprimir = QPushButton("Imprimir Recibo")
        self.btn_imprimir.clicked.connect(imprimir_recibo)
        self.resultado_compra = QLabel("")
        compra_layout.addWidget(compra_label)
        compra_layout.addWidget(self.input_cpf_compra)
        compra_layout.addWidget(self.input_valor)
        compra_layout.addWidget(btn_salvar)
        compra_layout.addWidget(self.btn_imprimir)
        compra_layout.addWidget(self.resultado_compra)

        linhas.addLayout(usar_layout)
        linhas.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        linhas.addLayout(compra_layout)

        layout.addLayout(linhas)
        self.setLayout(layout)

    def usar_pontos(self):
        global ultimo_recibo
        cpf = self.input_cpf_usar.text().strip()
        try:
            pontos = int(self.input_pontos_usar.text().strip())
            resposta = usar_pontos_parcial(cpf, pontos)
            if isinstance(resposta, str):
                self.resultado_uso.setText(resposta)
            else:
                self.resultado_uso.setText(f"Desconto aplicado: R$ {resposta['desconto_em_reais']}\nPontos restantes: {resposta['pontos_restantes']}")
                ultimo_recibo.update(resposta)
        except ValueError:
            self.resultado_uso.setText("Digite um número de pontos válido.")

    def salvar_compra(self):
        global ultimo_recibo
        cpf = self.input_cpf_compra.text().strip()
        try:
            valor = float(self.input_valor.text().replace(",", "."))
            resposta = registrar_compra(cpf, valor)
            if isinstance(resposta, str):
                self.resultado_compra.setText(resposta)
            else:
                self.resultado_compra.setText(f"Compra registrada com sucesso!\nPontos: {resposta['pontos']}\nDesconto atual: {resposta['desconto']}%")
                resposta.update({
                    "valor": valor,
                    "cpf": cpf,
                    "pontos_recebidos": int(valor),
                    "pontos_usados": 0
                })
                ultimo_recibo = resposta
        except ValueError:
            self.resultado_compra.setText("Digite um valor numérico válido.")

class InterfacePrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Fidelidade - Papa Açaí")
        self.resize(600, 400)
        abas = QTabWidget()
        abas.addTab(AbaCadastroConsulta(), "Cadastro / Consulta")
        abas.addTab(AbaCompraUso(), "Compra / Usar Pontos")
        layout = QVBoxLayout()
        layout.addWidget(abas)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = InterfacePrincipal()
    janela.show()
    sys.exit(app.exec())
