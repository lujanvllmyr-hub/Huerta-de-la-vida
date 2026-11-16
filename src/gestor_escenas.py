"""Gestor responsable del registro y ciclo de vida de escenas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame


class EscenaBase(ABC):
    """Contrato que deben implementar las escenas del juego."""

    def procesar_eventos(self, eventos: Iterable[pygame.event.Event]) -> None:
        """Procesa los eventos recibidos por la aplicación."""
        pass

    @abstractmethod
    def actualizar(self, dt: float) -> None:
        """Actualiza la lógica de la escena."""
        raise NotImplementedError

    @abstractmethod
    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena en pantalla."""
        raise NotImplementedError


class GestorEscenas:
    """Registra las escenas y delega en la escena activa."""

    def __init__(self) -> None:
        self.escenas: dict[str, EscenaBase] = {}
        self.estado_actual: str | None = None

    def agregar_escena(self, nombre: str, escena: EscenaBase) -> None:
        """Registra una escena con un nombre único."""
        if nombre in self.escenas:
            raise ValueError(f"Ya existe una escena registrada con el nombre {nombre!r}.")

        self.escenas[nombre] = escena

    def cambiar_escena(self, nombre: str) -> None:
        """Activa una escena registrada."""
        if nombre not in self.escenas:
            raise KeyError(f"No hay una escena registrada con el nombre {nombre!r}.")

        self.estado_actual = nombre

    @property
    def escena_actual(self) -> EscenaBase:
        """Devuelve la escena activa."""
        if self.estado_actual is None:
            raise RuntimeError("No hay una escena activa.")

        return self.escenas[self.estado_actual]

    def procesar_eventos(self, eventos: Iterable[pygame.event.Event]) -> None:
        """Delega los eventos en la escena activa."""
        self.escena_actual.procesar_eventos(eventos)

    def actualizar(self, dt: float) -> None:
        """Actualiza la escena activa."""
        self.escena_actual.actualizar(dt)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena activa."""
        self.escena_actual.dibujar(pantalla)
