from ast import While
from concurrent.futures import process
import Canales
import simpy

class Nodo:
    """Representa un nodo basico.

    Atributos:
    id_nodo -- identificador del nodo
    vecinos -- lista con los ids de nuestros vecinos
    canales -- tupla de la forma (canal_entrada, canal_salida)
    """
    def __init__(self, id_nodo: int, vecinos: list, canales: tuple):
        """Constructor basico de un Nodo."""
        self.id_nodo = id_nodo
        self.vecinos = vecinos
        self.canales = canales

    def __str__(self):
        """Regresa la representacion en cadena del nodo."""
        return f'Nodo {self.id_nodo}, vecinos = {self.vecinos}'
    
    def get_id(self) -> int:
        """Regresa el identificador del nodo."""
        return self.id_nodo
    
    def get_vecinos(self) -> list:
        """Regresa la lista de vecinos del nodo."""
        return self.vecinos

    def get_canal_entrada(self) -> simpy.Store:
        """Regresa el canal de entrada del nodo."""
        return self.canales[0]

    def get_canal_salida(self) -> Canales.Canal:
        """Regresa el canal de salida del nodo."""
        return self.canales[1]

class NodoVecinos(Nodo):
    """Nodo que implementa el algoritmo del ejercicio 1.

    Atributos adicionales:
    vecinos_de_vecinos -- lista con los ids de los vecinos de nuestros vecinos
    """
    def __init__(self, id_nodo: int, vecinos: list, canales: tuple):
        """Constructor para el nodo 'vecinos'."""
        # Llamar al constructor padre
        Nodo.__init__(self, id_nodo, vecinos, canales)
        # Agregar lógica nueva
        self.vecinos_de_vecinos = []

    def conoce_vecinos(self, env: simpy.Environment):
        """Algoritmo para conocer a los vecinos de mis vecinos."""
        # Enviar mis vecinos a mis vecinos
        self.canales[1].envia(self.vecinos, self.vecinos)
        # Recibir y procesar los mesajes de mis vecinos
        while True:
            msg = yield self.canales[0].get()
            for vecino in msg:
                if vecino not in self.vecinos_de_vecinos:
                    self.vecinos_de_vecinos.append(vecino)

class NodoArbolGenerador(Nodo):
    """Nodo que implementa el algoritmo del ejercicio 2.

    Atributos adicionales:
    madre -- id del nodo madre dentro del arbol
    hijas -- lista de nodos hijas del nodo actual
    """
    def __init__(self, id_nodo: int, vecinos: list, canales: tuple):
        """Constructor para el nodo arbol generador."""
        # Llamar al constructor padre
        Nodo.__init__(self, id_nodo, vecinos, canales)
        # Agregar lógica nueva
        self.madre = None
        self.hijas = []

    def genera_arbol(self, env: simpy.Store):
        """Algoritmo para producir el arbol generador."""
        # Asignar al mismo nodo como su madre
        self.madre = self.id_nodo
        # Definir el número de mensajes esperados como su número de vecinos
        self.expected_msg = len(self.vecinos)
        # Enviar mensaje GO a sus vecinos
        self.canales[1].envia(("GO",self.id_nodo), self.vecinos)
        yield env.timeout(0)

    def recibeMensajes(self, env: simpy.Store):
        while True:

            # Recibir mensaje
            msg = yield self.canales[0].get()
            # Procesar los mesajes GO
            if msg[0] == "GO":
                if self.madre is None:
                    self.madre = msg[1]
                    self.expected_msg = len(self.vecinos)-1
                    if self.expected_msg == 0:
                        self.canales[1].envia(("BACK", self.id_nodo, self.id_nodo), [msg[1]])
                    else:
                        for vecino in self.vecinos:
                            if vecino != msg[1]:
                                self.canales[1].envia(("GO", self.id_nodo), [vecino])
                else: self.canales[1].envia(("BACK", self.id_nodo, None), [msg[1]])
            
            # Procesar los mensajes BACK
            if msg[0] == "BACK":
                self.expected_msg -= 1
                if not (msg[2] is None):
                    self.hijas.append(msg[2])
                if self.expected_msg == 0:
                    if self.madre != self.id_nodo:
                        self.canales[1].envia(("BACK", self.id_nodo, self.id_nodo), [self.madre])
            
class NodoBroadcast(Nodo):
    """Nodo que implementa el algoritmo del ejercicio 3.

    Atributos adicionales:
    mensaje -- cadena con el mensaje que se distribuye
    """
    def __init__(self, id_nodo: int, vecinos: list, canales: tuple):
        """Constructor para el nodo broadcast."""
        # Llamar al constructor padre
        Nodo.__init__(self, id_nodo, vecinos, canales)
        # Agregar lógica nueva
        self.mensaje = None

    def broadcast(self, env: simpy.Store):
        """Algoritmo de broadcast."""
        # Enviar el mensaje del nodo distinguido a sus hijas
        self.canales[1].envia(self.mensaje, self.vecinos)
        yield env.timeout(0)

    def recibeMensajes(self, env: simpy.Store):
        while True:
            # Recibir y guardar el mensaje
            self.mensaje = yield self.canales[0].get()
            # Enviar el mensaje del nodo a sus hijas
            self.canales[1].envia(self.mensaje, self.vecinos)
