"""Punto de entrada y bucle principal de Huerta de la Vida."""

import pygame

if __package__:
    from .escenas import crear_gestor_escenas
else:
    from escenas import crear_gestor_escenas

ANCHO_PANTALLA = 960
ALTO_PANTALLA = 540
FPS_OBJETIVO = 60


def main() -> None:
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Huerta de la Vida")
    reloj = pygame.time.Clock()
    gestor_escenas = crear_gestor_escenas()
    ejecutando = True

    while ejecutando:
        dt = reloj.tick(FPS_OBJETIVO) / 1000.0
        eventos = pygame.event.get()

        for evento in eventos:
            if evento.type == pygame.QUIT:
                ejecutando = False

        gestor_escenas.procesar_eventos(eventos)
        gestor_escenas.actualizar(dt)
        gestor_escenas.dibujar(pantalla)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
