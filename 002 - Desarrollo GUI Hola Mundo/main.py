"""
Trabajo de desarrollo N° 1 - Proyecto 4 FIUNA
Alumno: Caleb Trepowski Castillo
"""

from PyQt6 import QtWidgets, QtGui, QtCore


class MainWindow(QtWidgets.QMainWindow):
    mainContainer: QtWidgets.QWidget
    campoNombre: QtWidgets.QLineEdit
    texto: QtWidgets.QLabel

    def __init__(self) -> None:
        super().__init__()
        self.inicializarPropiedadesGraficas()
        self.inicializarWidgets()
        self.show()

    def inicializarPropiedadesGraficas(self) -> None:
        self.setWindowTitle("Hola Mundo - Caleb Trepowski")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

    def inicializarWidgets(self) -> None:
        # Contenedor principal
        self.mainContainer = QtWidgets.QWidget(self)
        self.mainContainer.setStyleSheet("""
            margin-right: 50px;
            margin-left: 50px
        """)
        layout = QtWidgets.QVBoxLayout()

        layout.addStretch(1)

        # Campo para el nombre
        self.campoNombre = QtWidgets.QLineEdit(self.mainContainer)
        layout.addWidget(self.campoNombre)
        self.campoNombre.setPlaceholderText("Ej: Juan")
        self.campoNombre.setMinimumHeight(35)

        # Boton de "submit"
        self.boton = QtWidgets.QPushButton(self.mainContainer)
        self.boton.setMinimumHeight(35)
        self.boton.setText("Actualizar")
        layout.addWidget(self.boton)
        self.boton.clicked.connect(self.actualizar_saludo)

        # Texto a mostrar
        self.texto = QtWidgets.QLabel(self.mainContainer)
        self.texto.setStyleSheet("""
            font-weight: bold;
            font-size: 14pt;
        """)
        layout.addStretch(1)

        layout.addWidget(self.texto)

        layout.addStretch(1)
        self.mainContainer.setLayout(layout)

        self.setCentralWidget(self.mainContainer)

    def actualizar_saludo(self) -> None:
        """ Muestra un saludo al nombre introducido en el campo
        de nombre. Si este está vacío muestra un mensaje de error """
        textoNombre = self.campoNombre.text()
        if textoNombre == "":
            self.texto.clear()
            self.texto.setText("No dejar vacío el nombre!")
            return

        self.texto.clear()
        self.texto.setText(f"Hola, {textoNombre}!")
        self.campoNombre.setText("")
        self.campoNombre.setFocus()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        print(a0.modifiers())
        if a0.key() == QtCore.Qt.Key.Key_Return or a0.key() == QtCore.Qt.Key.Key_Enter:
            self.actualizar_saludo()
        if a0.key() == QtCore.Qt.Key.Key_Escape:
            raise SystemExit


def main() -> None:
    app = QtWidgets.QApplication([])
    main_window = MainWindow()

    app.exec()


main()
