import time
from aegis.brain.circuit_breaker import CircuitBreakerManager, CircuitState

def test_circuit_trips_on_failures():
    mgr = CircuitBreakerManager(failure_threshold=2, cooldown_seconds=0.5)

    assert mgr.can_call("openai") is True
    assert mgr.get_circuit("openai").state == CircuitState.CLOSED

    # 1st failure
    mgr.record_failure("openai", RuntimeError("503"))
    assert mgr.can_call("openai") is True
    assert mgr.get_circuit("openai").state == CircuitState.CLOSED

    # 2nd failure -> threshold reached
    mgr.record_failure("openai", RuntimeError("503"))
    assert mgr.get_circuit("openai").state == CircuitState.OPEN
    assert mgr.can_call("openai") is False

def test_circuit_cooldown_and_recovery():
    mgr = CircuitBreakerManager(failure_threshold=1, cooldown_seconds=0.2)
    mgr.record_failure("openai", RuntimeError("429"))
    assert mgr.get_circuit("openai").state == CircuitState.OPEN
    assert mgr.can_call("openai") is False

    # Wait past cooldown
    time.sleep(0.25)
    assert mgr.can_call("openai") is True
    assert mgr.get_circuit("openai").state == CircuitState.HALF_OPEN

    # Record success -> returns to CLOSED
    mgr.record_success("openai")
    assert mgr.get_circuit("openai").state == CircuitState.CLOSED
    assert mgr.can_call("openai") is True
