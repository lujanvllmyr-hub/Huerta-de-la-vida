"""Entidad con movimiento por tiempo y colisiones AABB por eje."""

from __future__ import annotations

from collections.abc import Iterable
from math import ceil, isfinite

import pygame


class EntidadBase:
    """Estado y movimiento básico de una entidad rectangular."""

    def __init__(
        self,
        x: float,
        y: float,
        ancho: float,
        alto: float,
        vx: float = 0.0,
        vy: float = 0.0,
    ) -> None:
        if ancho <= 0 or alto <= 0:
            raise ValueError("El ancho y el alto de la entidad deben ser positivos.")

        self.x = float(x)
        self.y = float(y)
        self.ancho = float(ancho)
        self.alto = float(alto)
        self.vx = float(vx)
        self.vy = float(vy)

    def actualizar(self, dt: float, solidos: Iterable[pygame.Rect]) -> None:
        """Integra la velocidad y resuelve las colisiones con rectángulos sólidos."""
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt debe ser un número finito mayor o igual a cero.")

        colisionadores = tuple(
            solido for solido in solidos if solido.width > 0 and solido.height > 0
        )
        desplazamiento_maximo = max(abs(self.vx * dt), abs(self.vy * dt))
        pasos = 1
        if colisionadores and desplazamiento_maximo > 0:
            tamano_minimo = min(
                self.ancho,
                self.alto,
                *(min(solido.width, solido.height) for solido in colisionadores),
            )
            pasos = max(1, ceil(desplazamiento_maximo / (tamano_minimo / 2)))

        dt_paso = dt / pasos
        # Dos AABB se superponen cuando sus intervalos se cruzan en ambos ejes:
        # min(A.right, B.right) - max(A.left, B.left) > 0 y
        # min(A.bottom, B.bottom) - max(A.top, B.top) > 0.
        # En una esquina pueden cumplirse las dos condiciones durante el mismo dt.
        # Cada subpaso resuelve X antes que Y. Las distancias a las caras son:
        # derecha/abajo: dx = B.left - A.right, dy = B.top - A.bottom;
        # izquierda/arriba: dx = B.right - A.left, dy = B.bottom - A.top.
        # Así se elige una cara de contacto de forma determinista y se reduce
        # el riesgo de atravesar esquinas en un único dt grande.
        for _ in range(pasos):
            self._mover_horizontal(self.vx * dt_paso, colisionadores)
            self._mover_vertical(self.vy * dt_paso, colisionadores)

    def _mover_horizontal(
        self,
        desplazamiento: float,
        solidos: tuple[pygame.Rect, ...],
    ) -> None:
        if desplazamiento == 0:
            return

        desplazamiento_permitido = desplazamiento
        for solido in solidos:
            if not self._solapa_vertical(solido):
                continue

            if desplazamiento > 0:
                distancia = solido.left - (self.x + self.ancho)
                if 0 <= distancia < desplazamiento_permitido:
                    desplazamiento_permitido = distancia
                elif self._solapa_horizontal(solido):
                    desplazamiento_permitido = min(
                        desplazamiento_permitido,
                        solido.left - (self.x + self.ancho),
                    )
            else:
                distancia = solido.right - self.x
                if desplazamiento_permitido < distancia <= 0:
                    desplazamiento_permitido = distancia
                elif self._solapa_horizontal(solido):
                    desplazamiento_permitido = max(
                        desplazamiento_permitido,
                        solido.right - self.x,
                    )

        self.x += desplazamiento_permitido
        if desplazamiento_permitido != desplazamiento:
            self.vx = 0.0

    def _mover_vertical(
        self,
        desplazamiento: float,
        solidos: tuple[pygame.Rect, ...],
    ) -> None:
        if desplazamiento == 0:
            return

        desplazamiento_permitido = desplazamiento
        for solido in solidos:
            if not self._solapa_horizontal(solido):
                continue

            if desplazamiento > 0:
                distancia = solido.top - (self.y + self.alto)
                if 0 <= distancia < desplazamiento_permitido:
                    desplazamiento_permitido = distancia
                elif self._solapa_vertical(solido):
                    desplazamiento_permitido = min(
                        desplazamiento_permitido,
                        solido.top - (self.y + self.alto),
                    )
            else:
                distancia = solido.bottom - self.y
                if desplazamiento_permitido < distancia <= 0:
                    desplazamiento_permitido = distancia
                elif self._solapa_vertical(solido):
                    desplazamiento_permitido = max(
                        desplazamiento_permitido,
                        solido.bottom - self.y,
                    )

        self.y += desplazamiento_permitido
        if desplazamiento_permitido != desplazamiento:
            self.vy = 0.0

    def _solapa_horizontal(self, solido: pygame.Rect) -> bool:
        return self.x < solido.right and self.x + self.ancho > solido.left

    def _solapa_vertical(self, solido: pygame.Rect) -> bool:
        return self.y < solido.bottom and self.y + self.alto > solido.top
