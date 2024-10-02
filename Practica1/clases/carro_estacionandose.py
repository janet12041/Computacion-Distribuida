import simpy

def carro(env):
    """Proceso Carro.

    Parametros:
    env -- el ambiente en el que estara el proceso.
    """
    while True:
        print('Empieza a estacionarse al %d' % env.now)
        duracion_estacionado = 5
        yield env.timeout(duracion_estacionado) # Esperamos hasta que acabe el timeout

        print('Empieza a conducir al %d' % env.now)
        duracion_viaje = 2
        yield env.timeout(duracion_viaje)


env = simpy.Environment() # Creamos el ambiente
env.process(carro(env)) # Le agregamos un proceso carro al ambiente
env.run(until=17) # Y lo corremos 17 rondas