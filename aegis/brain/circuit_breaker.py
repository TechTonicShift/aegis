import time
from enum import Enum
from typing import Dict, Any

class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Healthy, requests pass through
    OPEN = "OPEN"            # Tripped, requests blocked / diverted
    HALF_OPEN = "HALF_OPEN"  # Testing recovery

class ProviderCircuit:
    def __init__(self, name: str, failure_threshold: int = 3, cooldown_seconds: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: float = 0.0
        self.last_state_change: float = time.time()
        self.success_count: int = 0

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if now - self.last_failure_time >= self.cooldown_seconds:
                # Transition to HALF_OPEN to attempt recovery
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def record_success(self):
        self.failure_count = 0
        self.success_count += 1
        if self.state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()

    def record_failure(self, error: Exception = None):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = self.last_failure_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
        }

class CircuitBreakerManager:
    """Manages circuit breakers across all registered upstream LLM providers."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._circuits: Dict[str, ProviderCircuit] = {}

    def get_circuit(self, provider_name: str) -> ProviderCircuit:
        if provider_name not in self._circuits:
            self._circuits[provider_name] = ProviderCircuit(
                name=provider_name,
                failure_threshold=self.failure_threshold,
                cooldown_seconds=self.cooldown_seconds,
            )
        return self._circuits[provider_name]

    def can_call(self, provider_name: str) -> bool:
        return self.get_circuit(provider_name).can_execute()

    def record_success(self, provider_name: str):
        self.get_circuit(provider_name).record_success()

    def record_failure(self, provider_name: str, error: Exception = None):
        self.get_circuit(provider_name).record_failure(error)

    def get_all_states(self) -> Dict[str, Any]:
        return {name: c.to_dict() for name, c in self._circuits.items()}
