"""
Qiskit adapter stub.
Maps a circuit run to backend.run(circuit).
"""

from typing import Any


class QiskitAdapter:
    def __init__(self, backend: Any):
        self.backend = backend

    def run_circuit(self, circuit: Any) -> Any:
        if hasattr(self.backend, "run"):
            return self.backend.run(circuit)
        raise NotImplementedError("Backend missing run(circuit)")

    def handle_intent(self, intent: str, circuit: Any = None) -> Any:
        if intent.lower() in ["run", "execute", "run_circuit"]:
            if circuit is None:
                raise ValueError("Circuit must be provided")
            return self.run_circuit(circuit)
        raise ValueError(f"Unknown intent: {intent}")
