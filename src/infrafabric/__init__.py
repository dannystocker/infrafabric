"""
InfraFabric package marker with fluent Logistics interface.

Example:
    from infrafabric import IF, Packet

    packet = Packet(origin="council", contents={"memo": "dispatch"})
    IF.Logistics.use(IF.Logistics.connect())  # optional shared dispatcher
    IF.Logistics.dispatch(packet).to("council:inbox")
"""

from typing import Optional

from infrafabric.core.logistics import (
    DispatchQueue,
    LogisticsDispatcher,
    Packet,
    ParcelSchemaVersion,
)


class _DispatchBuilder:
    """Fluent helper to complete a dispatch route."""

    def __init__(self, packet: Packet, logistics: "_FluentLogistics") -> None:
        self.packet = packet
        self._logistics = logistics
        self._dispatcher: Optional[LogisticsDispatcher] = None

    def via(self, dispatcher: LogisticsDispatcher) -> "_DispatchBuilder":
        """Explicitly set which dispatcher handles this route."""

        self._dispatcher = dispatcher
        return self

    def to(self, destination: str, operation: str = "set", use_msgpack: bool = False) -> bool:
        """Finalize the route and dispatch the Packet."""

        dispatcher = self._dispatcher or self._logistics.default_dispatcher
        if dispatcher is None:
            raise RuntimeError(
                "No Logistics dispatcher configured. Call IF.Logistics.use(...) "
                "or pass .via(dispatcher) before calling .to()."
            )
        return dispatcher.dispatch_to_redis(
            key=destination,
            packet=self.packet,
            operation=operation,
            use_msgpack=use_msgpack,
        )


class _FluentLogistics:
    """Natural language wrapper for IF.Logistics.dispatch(...).to(...)"""

    def __init__(self) -> None:
        self.default_dispatcher: Optional[LogisticsDispatcher] = None

    def connect(self, **kwargs) -> LogisticsDispatcher:
        """Instantiate a default LogisticsDispatcher with provided kwargs."""

        dispatcher = LogisticsDispatcher(**kwargs)
        self.default_dispatcher = dispatcher
        return dispatcher

    def use(self, dispatcher: LogisticsDispatcher) -> "_FluentLogistics":
        """Register an existing dispatcher as the default."""

        self.default_dispatcher = dispatcher
        return self

    def dispatch(self, packet: Packet) -> _DispatchBuilder:
        """Begin a fluent dispatch chain."""

        return _DispatchBuilder(packet, self)


class _IFNamespace:
    """Namespace to mirror the top-level IF.Logistics usage."""

    def __init__(self) -> None:
        self.Logistics = _FluentLogistics()


IF = _IFNamespace()

__all__ = [
    "DispatchQueue",
    "IF",
    "LogisticsDispatcher",
    "Packet",
    "ParcelSchemaVersion",
]
