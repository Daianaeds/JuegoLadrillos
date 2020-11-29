import pygame 
import sys # para usar exit()
import time # para usar sleep()

ANCHO = 650
ALTO = 651
imagen_fondo = pygame.image.load('Imagenes/fodo_luna2.jpg')
color_blanco = (255,255,255)

pygame.init()

class Escena:
    def __init__(self):
        "inicializacion"
        self.proximaEscena = False
        self.jugando = True

    def leer_eventos(self, eventos):
        "Lee la lista de todos los eventos"
        pass

    def actualizar(self):
        "calculos y logica"
        pass

    def dibujar(self, pantalla):
        "dibuja los elementos en pantalla"
        pass

    def cambiar_escena(self, escena):
        "selecciona la nueva escena a ser desplegada"
        self.proximaEscena = escena

class Director:
    def __init__(self, titulo = "", res = (ANCHO, ALTO)):
        # Inicializado pantalla
        self.pantalla = pygame.display.set_mode((res))
        # Configurar titulo
        pygame.display.set_caption(titulo)
        # Crear el reloj
        self.reloj = pygame.time.Clock()
        self.escena = None
        self.escenas = {}
        self.sonidoFondo = pygame.mixer.Sound("Sonidos/musicadefondo.mpeg")
        self.sonidoFondo.play()
    
    def ejecutar(self, escena_inicial, fps = 100):
        self.escena = self.escenas[escena_inicial]
        jugando = True
        game_over = False
        while jugando:
            self.reloj.tick(fps)
            eventos = pygame.event.get()
            #revisar todos los eventos
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    #cerrar el juego
                    jugando = False
                    self.sonidoFondo.stop()
                    sys.exit()
                '''if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_s:
                        if game_over == True:
                            director.agregarEscena('Nivel1')
                            director.ejecutar('Nivel1')'''

            self.escena.leer_eventos(eventos)
            self.escena.actualizar()
            self.escena.dibujar(self.pantalla)

            self.elegirEscena(self.escena.proximaEscena)

            if jugando:
                jugando = self.escena.jugando
            pygame.display.flip()

        #time.sleep(3)

    def elegirEscena(self, proximaEscena):
        if proximaEscena:
            if proximaEscena not in self.escenas:
                self.agregarEscena(proximaEscena)
            self.escena = self.escenas[proximaEscena]

    def agregarEscena(self, escena):
        escenaClase = "Escena" + escena
        escenaObj = globals()[escenaClase]
        self.escenas[escena] = escenaObj();

class EscenaNivel1(Escena):
    def __init__(self):
        Escena.__init__(self)

        self.bolita = Bolita() 
        self.jugador = Paleta()
        self.muro = Muro(49)

        self.puntuacion = 0
        self.vidas = 3
        self.esperando_saque = True 
        

        # Ajustar repeticion de evento de tecla presionada
        pygame.key.set_repeat(30)  

    def leer_eventos(self, eventos):
        for evento in eventos:
        # Buscar eventos en el teclado
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)
                if self.esperando_saque == True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False
                    if self.bolita.rect.centerx < ANCHO / 2:
                        self.bolita.speed = [3, -3]
                    else:
                        self.bolita.speed = [-3, -3]

    def actualizar(self):
        # Actualizar la posicion de la bolita
        if self.esperando_saque == False:
            self.bolita.update()
        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop

        # Colision entre bolita y jugador
        if pygame.sprite.collide_rect(self.bolita, self.jugador): #indica si hubo colision entre dos sprites
            self.bolita.speed[1] = -self.bolita.speed[1]
            cx = self.bolita.rect.centerx
            if cx < self.jugador.rect.left or cx > self.jugador.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
        

        # Colision entre bolita y muro
        lista = pygame.sprite.spritecollide(self.bolita, self.muro, False) #da una lista de sprites dentro de un grupo 
                                                                #que colisiona con otro sprite, permitiendo decidir 
                                                                # si eliminar dichos elementos o no
        if lista:
            ladrillo = lista[0]
            sonido = pygame.mixer.Sound("Sonidos/laser5.ogg")
            cx = self.bolita.rect.centerx
            if cx < ladrillo.rect.left or cx > ladrillo.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
            else:
                self.bolita.speed[1] = -self.bolita.speed[1]
            self.muro.remove(ladrillo) #eliminacion manual de un sprite
            sonido.play()
            if len(self.muro) == 0:
                self.cambiar_escena('JuegoTerminado')
            self.puntuacion += 10

        # Revisar si la bolita sale de la pantalla 
        if self.bolita.rect.top > ALTO:
            self.vidas -= 1
            self.esperando_saque = True

        if self.vidas <= 0:
            self.cambiar_escena('JuegoTerminado')

    def dibujar(self, pantalla):
        # Rellenar la pantalla
        pantalla.blit(imagen_fondo, [0,0])
        # Mostrar puntuacion
        self.mostrar_puntuacion(pantalla)
        # Mostrar vidas
        self.mostrar_vidas(pantalla)
        #dibujar la pelota sobre la pantalla en las coordenadas que traiga el objeto
        pantalla.blit(self.bolita.image, self.bolita.rect) 
        # Dibujar jugador en pantalla
        pantalla.blit(self.jugador.image, self.jugador.rect)
        # Dibujar los ladrillos
        self.muro.draw(pantalla)

    def mostrar_puntuacion(self, pantalla):
        fuente = pygame.font.SysFont("Consolas", 20)
        texto = fuente.render(str(self.puntuacion).zfill(5), True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topleft = [0, 0]
        pantalla.blit(texto, texto_rect)

    def mostrar_vidas(self, pantalla):
        fuente = pygame.font.SysFont("Consolas", 20)
        cadena = "Vidas: " + str(self.vidas).zfill(2)
        texto = fuente.render(cadena, True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.topright = [ANCHO, 0]
        pantalla.blit(texto, texto_rect)

class EscenaJuegoTerminado(Escena):
    def actualizar(self):
        #self.jugando = False
        #self.game_over = True
        pass
    def dibujar(self, pantalla):
        self.image = pygame.image.load('Imagenes/gameover.jpg')
        pantalla.blit(self.image, [0,0])
        pygame.display.flip()
        fuente = pygame.font.SysFont('Unispace', 50)
        texto = fuente.render("""Si deseas continuar, teclear S""", True, color_blanco)
        texto_rect = texto.get_rect()
        texto_rect.center = [ANCHO / 2, ALTO - 80]
        pantalla.blit(texto, texto_rect)
        eventos = pygame.event.get()
        for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_s:
                            director.agregarEscena('Nivel1')
                            director.ejecutar('Nivel1')
                    if evento.type == pygame.QUIT:
                            #cerrar el juego
                        sys.exit()


class Bolita(pygame.sprite.Sprite):
    def __init__(self):#constructor
        pygame.sprite.Sprite.__init__(self)
        # Cargar imagen
        self.image = pygame.image.load("Imagenes/meteor.png")
        # Obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        # Posicion inicial centrada en pantalla
        self.rect.centerx = ANCHO / 2
        self.rect.centery = ALTO / 2
        # Establecer velocidad inicial (para que haya movimiento)
        self.speed = [3, 3] #cuantos pixeles se mueven en x e y

    def update(self): 
        
        # Evitar que la pelota salga por debajo
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
        # Evitar que salga por derecha
        elif self.rect.right >= ANCHO or self.rect.left <=0:
            self.speed[0] = -self.speed[0]
        #Mover en base a la posicion actual y velocidad
        self.rect.move_ip(self.speed)


class Paleta(pygame.sprite.Sprite):
    def __init__(self):#constructor
        pygame.sprite.Sprite.__init__(self)
        # Cargar imagen
        self.image = pygame.image.load("Imagenes/paleta.png")
        # Obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        # Posicion inicial centrada en pantalla en X
        self.rect.midbottom = (ANCHO / 2, ALTO -20)
        # Establecer velocidad inicial (para que haya movimiento)
        self.speed = [0, 0] #cuantos pixeles se mueven en x e y

    def update(self, evento): 
        
        # Buscar si se presiono tecla izquierda
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-7, 0]
        # Si se presiona la tecla derecha
        elif evento.key == pygame.K_RIGHT and self.rect.right < ANCHO:
            self.speed = [7, 0]
        else:
            self.speed = [0, 0]
        #Mover en base a la posicion actual y velocidad
        self.rect.move_ip(self.speed)


class Ladrillo(pygame.sprite.Sprite):
    def __init__(self, posicion):#constructor
        pygame.sprite.Sprite.__init__(self)
        # Cargar imagen
        self.image = pygame.image.load("Imagenes/ladrillolv2.jpeg")
        # Obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        # Posicion incial, provista externamente
        self.rect.topleft = posicion

class Muro(pygame.sprite.Group):
    def __init__(self, cantidadLadrillos):#constructor
        pygame.sprite.Group.__init__(self)    

        pos_x = 0
        pos_y = 20
        for i in range(cantidadLadrillos):
            ladrillo = Ladrillo((pos_x, pos_y))
            self.add(ladrillo)

            pos_x += ladrillo.rect.width
            if pos_x >= ANCHO:
                pos_x = 0
                pos_y += ladrillo.rect.height


director = Director ('Juego de ladrillos', (ANCHO, ALTO))
director.agregarEscena('Nivel1')
director.ejecutar('Nivel1')