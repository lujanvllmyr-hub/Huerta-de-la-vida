"""Clases base para las entidades del juego."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from math import isfinite

import pygame


class EntidadBase(ABC):
    """Estado y actualización por tiempo compartidos por las entidades."""

    VELOCIDAD_CONTROL = 300.0
    TECLAS_IZQUIERDA = (pygame.K_LEFT, pygame.K_a)
    TECLAS_DERECHA = (pygame.K_RIGHT, pygame.K_d)
    TECLAS_ARRIBA = (pygame.K_UP, pygame.K_w)
    TECLAS_ABAJO = (pygame.K_DOWN, pygame.K_s)
    TECLAS_MOVIMIENTO = (
        TECLAS_IZQUIERDA + TECLAS_DERECHA + TECLAS_ARRIBA + TECLAS_ABAJO
    )

    def __init__(
        self,
        x: float,
        y: float,
        ancho: int,
        alto: int,
        vx: float = 0.0,
        vy: float = 0.0,
        g: float = 980.0,
    ) -> None:
        if ancho <= 0 or alto <= 0:
            raise ValueError("El ancho y el alto de la entidad deben ser positivos.")
        if not isfinite(g):
            raise ValueError("g debe ser un número finito.")

        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.g = float(g)
        self.hitbox = pygame.Rect(round(self.x), round(self.y), ancho, alto)
        self._teclas_pulsadas: set[int] = set()

    def procesar_eventos(self, eventos: Iterable[pygame.event.Event]) -> None:
        """Guarda el estado de las teclas direccionales recibidas."""
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key in self.TECLAS_MOVIMIENTO:
                self._teclas_pulsadas.add(evento.key)
            elif evento.type == pygame.KEYUP and evento.key in self.TECLAS_MOVIMIENTO:
                self._teclas_pulsadas.discard(evento.key)

    @abstractmethod
    def actualizar(
        self,
        dt: float,
        solidos: Iterable[pygame.Rect] = (),
        limites: pygame.Rect | None = None,
    ) -> None:
        """Integra gravedad y movimiento; las subclases deben llamar a super()."""
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt debe ser un número finito mayor o igual a cero.")

        izquierda = any(tecla in self._teclas_pulsadas for tecla in self.TECLAS_IZQUIERDA)
        derecha = any(tecla in self._teclas_pulsadas for tecla in self.TECLAS_DERECHA)
        self.vx = (int(derecha) - int(izquierda)) * self.VELOCIDAD_CONTROL

        teclas_verticales = self.TECLAS_ARRIBA + self.TECLAS_ABAJO
        if any(tecla in self._teclas_pulsadas for tecla in teclas_verticales):
            arriba = any(tecla in self._teclas_pulsadas for tecla in self.TECLAS_ARRIBA)
            abajo = any(tecla in self._teclas_pulsadas for tecla in self.TECLAS_ABAJO)
            self.vy = (int(abajo) - int(arriba)) * self.VELOCIDAD_CONTROL

        self.vy += self.g * dt
        self.resolver_colisiones_aabb(dt, solidos, limites)

    def resolver_colisiones_aabb(
        self,
        dt: float,
        solidos: Iterable[pygame.Rect],
        limites: pygame.Rect | None = None,
    ) -> None:
        """Mueve y resuelve las colisiones AABB por separado en X y luego en Y."""
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt debe ser un número finito mayor o igual a cero.")

        rectangulos_solidos = tuple(
            solido for solido in solidos if solido.width > 0 and solido.height > 0
        )
        self._mover_horizontal(self.vx * dt, rectangulos_solidos, limites)
        self._sincronizar_hitbox()
        self._mover_vertical(self.vy * dt, rectangulos_solidos, limites)
        self._sincronizar_hitbox()

    def _mover_horizontal(
        self,
        desplazamiento: float,
        solidos: tuple[pygame.Rect, ...],
        limites: pygame.Rect | None,
    ) -> None:
        destino_x = self.x + desplazamiento
        hubo_colision = False

        if limites is not None:
            x_minimo = limites.left
            x_maximo = max(x_minimo, limites.right - self.hitbox.width)
            destino_limitado = max(x_minimo, min(destino_x, x_maximo))
            hubo_colision = destino_limitado != destino_x
            destino_x = destino_limitado

        if desplazamiento > 0:
            for solido in solidos:
                if (
                    self._solapa_vertical(solido)
                    and self.x + self.hitbox.width <= solido.left
                    and destino_x + self.hitbox.width > solido.left
                ):
                    destino_x = min(destino_x, solido.left - self.hitbox.width)
                    hubo_colision = True
        elif desplazamiento < 0:
            for solido in solidos:
                if (
                    self._solapa_vertical(solido)
                    and self.x >= solido.right
                    and destino_x < solido.right
                ):
                    destino_x = max(destino_x, solido.right)
                    hubo_colision = True

        self.x = destino_x
        if hubo_colision:
            self.vx = 0.0

    def _mover_vertical(
        self,
        desplazamiento: float,
        solidos: tuple[pygame.Rect, ...],
        limites: pygame.Rect | None,
    ) -> None:
        destino_y = self.y + desplazamiento
        hubo_colision = False

        if limites is not None:
            y_minimo = limites.top
            y_maximo = max(y_minimo, limites.bottom - self.hitbox.height)
            destino_limitado = max(y_minimo, min(destino_y, y_maximo))
            hubo_colision = destino_limitado != destino_y
            destino_y = destino_limitado

        if desplazamiento > 0:
            for solido in solidos:
                if (
                    self._solapa_horizontal(solido)
                    and self.y + self.hitbox.height <= solido.top
                    and destino_y + self.hitbox.height > solido.top
                ):
                    destino_y = min(destino_y, solido.top - self.hitbox.height)
                    hubo_colision = True
        elif desplazamiento < 0:
            for solido in solidos:
                if (
                    self._solapa_horizontal(solido)
                    and self.y >= solido.bottom
                    and destino_y < solido.bottom
                ):
                    destino_y = max(destino_y, solido.bottom)
                    hubo_colision = True

        self.y = destino_y
        if hubo_colision:
            self.vy = 0.0

    def _sincronizar_hitbox(self) -> None:
        self.hitbox.topleft = (round(self.x), round(self.y))

    def _solapa_horizontal(self, solido: pygame.Rect) -> bool:
        return self.x < solido.right and self.x + self.hitbox.width > solido.left

    def _solapa_vertical(self, solido: pygame.Rect) -> bool:
        return self.y < solido.bottom and self.y + self.hitbox.height > solido.top
