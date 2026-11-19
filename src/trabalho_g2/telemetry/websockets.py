from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class TelemetryWebsocket:
    def __init__(self) -> None:
        self._connections: set[tornado.websocket.WebSocketHandler] = set()
        self._io_loop: tornado.ioloop.IOLoop | None = None
        self._server: tornado.httpserver.HTTPServer | None = None
        self.application = tornado.web.Application(
            [(r"/ws", self._create_handler())]
        )

    def _create_handler(self) -> type[tornado.websocket.WebSocketHandler]:
        websocket = self

        class TelemetryWebSocketHandler(tornado.websocket.WebSocketHandler):
            def check_origin(self, origin: str) -> bool:
                return True

            def open(self) -> None:
                websocket._connections.add(self)
                print("Conexão aberta")

            def on_close(self) -> None:
                websocket._connections.discard(self)
                print("Conexão fechada")

        return TelemetryWebSocketHandler

    def start(self, port: int = 8888) -> None:
        if self._server is not None:
            raise RuntimeError("Telemetry websocket is already running")

        self._io_loop = tornado.ioloop.IOLoop.current()
        self._server = self.application.listen(port)

    def send_message(self, message: DataclassInstance) -> None:
        if self._io_loop is None:
            raise RuntimeError("Telemetry websocket has not been started")

        serialized_message = json.dumps(asdict(message))
        self._io_loop.add_callback(self._broadcast, serialized_message)

    def _broadcast(self, message: str) -> None:
        for connection in tuple(self._connections):
            connection.write_message(message)

    def stop(self) -> None:
        if self._server is not None:
            self._server.stop()
            self._server = None
