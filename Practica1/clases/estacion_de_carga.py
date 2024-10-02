import simpy

def carro(env, nombre, ec, tiempo_conduccion, duracion_carga):
    """Clase de ejemplo carro. Ilustra el uso de los recursos compartidos."""
    # Conducimos primero a la estacion de carga
    yield env.timeout(tiempo_conduccion)
    print('%s llegando al %d' % (nombre, env.now))

    # El with es necesario para no preocuparnos por soltar luego el recurso
    with ec.request() as req:
        # Solicitamos la EC y esperamos a que se libere
        yield req

        print('%s empezando a cargar al %s' % (nombre, env.now))
        yield env.timeout(duracion_carga)
        print('%s dejando la EC al %s' % (nombre, env.now))


env = simpy.Environment()
# Definimos el recurso compartido que modela la EC
ec = simpy.Resource(env, capacity=2) 

for i in range(4):
    # Creamos 4 procesos 'Carro' con distintos tiempos de conduccion
    env.process(carro(env, 'Carro %d' % i, ec, i*2, 5))

env.run() # No hay procesos que corran para siempre, no es necesario el until
