from Canales import *
from Nodos import *
import simpy

class Grafica:
    """Representa una grafica.

    Atributos:
    nombre -- cadena que identifica a la grafica
    adyacencias -- lista de listas, adyacencias[i] representa las adyacencias
                    del i-esimo nodo
    nodos -- lista de nodos de la grafica. Dependiendo el algoritmo que hayamos
              corrido, el tipo de nodo sera distinto.
    """
    def __init__(self, nombre: str, adyacencias: list):
        self.nombre = nombre
        self.adyacencias = adyacencias
        self.nodos = []

    def __str__(self):
        return f'Grafica {self.nombre}, adyacencias: {self.adyacencias}'

    def get_nombre(self) -> str:
        return self.nombre

    def get_adyacencias(self) -> list:
        return self.adyacencias

    def get_nodos(self) -> list:
        return self.nodos

    def conoce_vecinos(self, env: simpy.Environment, canal: Canal) -> None:
        """Algoritmo para conocer a los vecinos de mis vecinos."""
        # Crear los nodos y agregarlos a 'nodos'.
        self.nodos = []
        for i in range(0, len(self.adyacencias)):
            self.nodos.append(NodoVecinos(i, self.adyacencias[i], 
                (canal.crea_canal_de_entrada(), canal)))
        # Decirle al env que procese 'conoce_vecinos' de cada nodo.
        for nodo in self.nodos:
            env.process(nodo.conoce_vecinos(env))
        yield env.timeout(0)

    def genera_arbol_generador(self, env: simpy.Environment, canal: Canal) \
            -> None:
        """Algoritmo para generar el arbol generador."""
        # Crear los nodos y agregarlos a 'nodos'.
        self.nodos = []
        for i in range(0, len(self.adyacencias)):
            self.nodos.append(NodoArbolGenerador(i, self.adyacencias[i], 
                (canal.crea_canal_de_entrada(), canal)))
        # Crear árbol generador.
        yield env.process(self.nodos[0].genera_arbol(env))
        for nodo in self.nodos:
            env.process(nodo.recibeMensajes(env))

    def broadcast(self, env: simpy.Environment, canal: Canal,
            adyacencias_arbol: list()) -> None:
        """Algoritmo de broadcast.
        
        Atributos:
        adyacencias_arbol -- Las aristas que forman el arbol sobre el que 
                              vamos a hacer el broadcast del mensaje.
        """
        self.adyacencias_arbol = adyacencias_arbol
        # Crear los nodos y agregarlos a 'nodos'.
        self.nodos = []
        for i in range(0, len(self.adyacencias_arbol)):
            self.nodos.append(NodoBroadcast(i, self.adyacencias_arbol[i], 
                (canal.crea_canal_de_entrada(), canal)))
        # Asignar un mensaje a un nodo distinguido
        self.nodos[0].mensaje = "Mensaje"
        # Broadcast
        yield env.process(self.nodos[0].broadcast(env))
        for nodo in self.nodos:
            env.process(nodo.recibeMensajes(env))