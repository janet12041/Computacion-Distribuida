import simpy
class Carro(object):
    """Clase de ejemplo Carro.  Ilustra la espera a otros procesos."""
    def __init__(self, env):
        self.env = env
        # Agregamos el proceso al ambiente que nos pasen como parametro
        self.action = env.process(self.run())

    def run(self):
        """El proceso del carro que el ambiente ejecutara."""
        while True:
            print('Empieza a estacionarse y cargar al %d' % self.env.now)
            duracion_carga = 5

            yield self.env.process(self.carga(duracion_carga)) # Esperamos al proceso carga

            print('Empieza a manejar al %d' % self.env.now)
            duracion_viaje = 2
            yield self.env.timeout(duracion_viaje)

    def carga(self, duracion):
        """Proceso que modela la carga del carro electrico."""
        yield self.env.timeout(duracion)

env = simpy.Environment()
carro = Carro(env) # Como el constructor agrega auto. el proceso run no hay que hacer mas
env.run(until=15)