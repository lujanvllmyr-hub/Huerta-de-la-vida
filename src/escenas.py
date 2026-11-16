"""Escenas del menú y del primer nivel de Huerta de la Vida."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import pygame

if __package__:
    from .entidades import EntidadBase
    from .gestor_escenas import EscenaBase, GestorEscenas
else:
    from entidades import EntidadBase
    from gestor_escenas import EscenaBase, GestorEscenas

ESTADO_MENU = "menu"
ESTADO_NIVEL_1 = "nivel_1"


class EscenaMenu(EscenaBase):
    """Pantalla inicial que permite comenzar el juego."""

    TECLAS_COMENZAR = (pygame.K_RETURN, pygame.K_KP_ENTER)

    def __init__(self, al_comenzar: Callable[[], None]) -> None:
        self._al_comenzar = al_comenzar
        self._fuentes = {42: pygame.font.Font(None, 42)}

    def procesar_eventos(self, eventos: Iterable[pygame.event.Event]) -> None:
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key in self.TECLAS_COMENZAR:
                self._al_comenzar()
                return

    def actualizar(self, dt: float) -> None:
        teclas_pulsadas = pygame.key.get_pressed()
        if any(teclas_pulsadas[tecla] for tecla in self.TECLAS_COMENZAR):
            self._al_comenzar()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill((177, 218, 147))
        tamano_fuente = 42
        fuente = self._fuentes[tamano_fuente]
        texto = fuente.render("Presionar ENTER para comenzar", True, (38, 72, 39))
        ancho_maximo = int(pantalla.get_width() * 0.9)
        if texto.get_width() > ancho_maximo:
            tamano_fuente = max(16, int(tamano_fuente * ancho_maximo / texto.get_width()))
            if tamano_fuente not in self._fuentes:
                self._fuentes[tamano_fuente] = pygame.font.Font(None, tamano_fuente)
            texto = self._fuentes[tamano_fuente].render(
                "Presionar ENTER para comenzar", True, (38, 72, 39)
            )
        pantalla.blit(texto, texto.get_rect(center=pantalla.get_rect().center))


class _Jugador(EntidadBase):
    def actualizar(
        self,
        dt: float,
        solidos: Iterable[pygame.Rect] = (),
        limites: pygame.Rect | None = None,
    ) -> None:
        super().actualizar(dt, solidos, limites)


class EscenaNivel1(EscenaBase):
    """Prototipo visual del jardinero y su huerta."""

    ANCHO_JUGADOR = 68
    ALTO_JUGADOR = 148

    def __init__(self) -> None:
        self._jugador = _Jugador(
            round(960 * 0.27 - self.ANCHO_JUGADOR / 2),
            round(540 * 0.78) - self.ALTO_JUGADOR,
            self.ANCHO_JUGADOR,
            self.ALTO_JUGADOR,
        )
        self._ancho_pantalla = 960
        self._alto_pantalla = 540
        self.limites_pantalla = pygame.Rect(0, 0, self._ancho_pantalla, self._alto_pantalla)
        self.objetos_estaticos = self._crear_objetos_estaticos(
            self._ancho_pantalla,
            self._alto_pantalla,
        )
        self._escala_escena = 1.0

    def procesar_eventos(self, eventos: Iterable[pygame.event.Event]) -> None:
        self._jugador.procesar_eventos(eventos)

    def actualizar(self, dt: float) -> None:
        self._jugador.actualizar(dt, self.objetos_estaticos, self.limites_pantalla)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        ancho, alto = pantalla.get_size()
        linea_suelo = int(alto * 0.62)
        if (ancho, alto) != (self._ancho_pantalla, self._alto_pantalla):
            self._ancho_pantalla = ancho
            self._alto_pantalla = alto
            self.limites_pantalla = pygame.Rect(0, 0, ancho, alto)
            self.objetos_estaticos = self._crear_objetos_estaticos(ancho, alto)
        self._escala_escena = alto / 540

        pantalla.fill((156, 211, 235))
        pygame.draw.circle(
            pantalla,
            (255, 220, 95),
            (int(ancho * 0.84), int(alto * 0.17)),
            int(alto * 0.07),
        )
        pygame.draw.rect(pantalla, (112, 177, 91), (0, linea_suelo, ancho, alto - linea_suelo))

        self._dibujar_cantero(pantalla, alto)
        self._dibujar_jardinero(
            pantalla,
            round(self._jugador.x + self._jugador.hitbox.width / 2),
            round(self._jugador.y + self._jugador.hitbox.height),
            alto,
        )

    def _crear_objetos_estaticos(self, ancho: int, alto: int) -> list[pygame.Rect]:
        y_suelo = round(alto * 0.78)
        cantero = pygame.Rect(
            round(ancho * 0.49),
            round(alto * 0.67),
            max(1, round(ancho * 0.45)),
            max(1, round(alto * 0.25)),
        )
        suelo = pygame.Rect(0, y_suelo, ancho, max(1, alto - y_suelo))
        return [suelo, cantero]

    def _dibujar_jardinero(self, pantalla: pygame.Surface, x: int, y: int, alto: int) -> None:
        escala = alto / 540

        def escalar(valor: float) -> int:
            return int(valor * escala)

        pygame.draw.line(
            pantalla,
            (55, 75, 110),
            (x + escalar(-12), y + escalar(-28)),
            (x + escalar(-17), y),
            max(1, escalar(8)),
        )
        pygame.draw.line(
            pantalla,
            (55, 75, 110),
            (x + escalar(12), y + escalar(-28)),
            (x + escalar(17), y),
            max(1, escalar(8)),
        )
        pygame.draw.rect(
            pantalla,
            (65, 139, 86),
            (x + escalar(-22), y + escalar(-92), escalar(44), escalar(65)),
        )
        pygame.draw.line(
            pantalla,
            (230, 174, 126),
            (x + escalar(-18), y + escalar(-78)),
            (x + escalar(-34), y + escalar(-48)),
            max(1, escalar(7)),
        )
        pygame.draw.line(
            pantalla,
            (230, 174, 126),
            (x + escalar(18), y + escalar(-78)),
            (x + escalar(34), y + escalar(-52)),
            max(1, escalar(7)),
        )
        pygame.draw.circle(
            pantalla,
            (230, 174, 126),
            (x, y + escalar(-111)),
            max(1, escalar(19)),
        )
        pygame.draw.ellipse(
            pantalla,
            (126, 82, 47),
            (x + escalar(-24), y + escalar(-137), escalar(48), escalar(13)),
        )
        pygame.draw.rect(
            pantalla,
            (126, 82, 47),
            (x + escalar(-14), y + escalar(-148), escalar(28), escalar(14)),
        )

    def _dibujar_cantero(self, pantalla: pygame.Surface, alto: int) -> None:
        escala = alto / 540
        cantero = self.objetos_estaticos[1]

        pygame.draw.rect(
            pantalla,
            (130, 82, 52),
            cantero,
        )

        for fila in range(2):
            centro_y = cantero.y + int((fila + 0.65) * cantero.height / 2)
            for columna in range(4):
                centro_x = cantero.x + int((columna + 0.5) * cantero.width / 4)
                self._dibujar_planta(pantalla, centro_x, centro_y, escala, fila + columna)

    def _dibujar_planta(
        self,
        pantalla: pygame.Surface,
        x: int,
        y: int,
        escala: float,
        variacion: int,
    ) -> None:
        def escalar(valor: float) -> int:
            return int(valor * escala)

        verde = (55, 126, 61)
        pygame.draw.line(
            pantalla,
            verde,
            (x, y + escalar(14)),
            (x, y - escalar(15)),
            max(1, escalar(4)),
        )
        pygame.draw.ellipse(
            pantalla,
            (78, 159, 73),
            (x - escalar(17), y - escalar(7), escalar(18), escalar(9)),
        )
        pygame.draw.ellipse(
            pantalla,
            (78, 159, 73),
            (x, y - escalar(13), escalar(18), escalar(9)),
        )
        color_fruto = (218, 73, 55) if variacion % 2 == 0 else (245, 180, 51)
        pygame.draw.circle(
            pantalla,
            color_fruto,
            (x, y - escalar(2)),
            max(1, escalar(7)),
        )


def crear_gestor_escenas() -> GestorEscenas:
    """Construye el gestor con el menú y el primer nivel registrados."""
    gestor = GestorEscenas()
    gestor.agregar_escena(
        ESTADO_MENU,
        EscenaMenu(lambda: gestor.cambiar_escena(ESTADO_NIVEL_1)),
    )
    gestor.agregar_escena(ESTADO_NIVEL_1, EscenaNivel1())
    gestor.cambiar_escena(ESTADO_MENU)
    return gestor
