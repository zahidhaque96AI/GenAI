
import time
from enum import Enum
from threading import Lock
from typing import Callable, Protocol, TypeVar


T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when the circuit breaker rejects a request."""

    def __init__(self, retry_after: float | None = None):
        self.retry_after = retry_after

        if retry_after is not None:
            message = (
                f"Circuit is OPEN. Retry after "
                f"{retry_after:.2f} seconds."
            )
        else:
            message = "Circuit is OPEN. Recovery probe already running."

        super().__init__(message)


class FailurePolicy(Protocol):
    """Contract for deciding which exceptions count as failures."""

    def should_count(self, error: Exception) -> bool:
        ...


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        failure_policy: FailurePolicy,
        clock: Callable[[], float] = time.monotonic,
    ):
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")

        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be positive")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_policy = failure_policy
        self.clock = clock

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None
        self._probe_in_progress = False

        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute an operation only when the circuit allows it.
        """

        is_probe = self._before_call()

        try:
            result = operation()

        except Exception as error:
            self._record_failure(error, is_probe)
            raise

        else:
            self._record_success(is_probe)
            return result

    def _before_call(self) -> bool:

        with self._lock:

            current_time = self.clock()

            if self._state == CircuitState.OPEN:

                elapsed = current_time - self._opened_at

                if elapsed < self.recovery_timeout:
                    retry_after = self.recovery_timeout - elapsed
                    raise CircuitOpenError(retry_after)

                self._state = CircuitState.HALF_OPEN
                self._probe_in_progress = False

            if self._state == CircuitState.HALF_OPEN:

                if self._probe_in_progress:
                    raise CircuitOpenError()

                self._probe_in_progress = True
                return True

            return False

    def _record_failure(
        self,
        error: Exception,
        is_probe: bool
    ) -> None:

        should_count = self.failure_policy.should_count(error)

        with self._lock:

            if is_probe:

                if self._state == CircuitState.HALF_OPEN:
                    self._open_circuit()

                return

            if self._state != CircuitState.CLOSED:
                return

            if should_count:

                self._failure_count += 1

                if self._failure_count >= self.failure_threshold:
                    self._open_circuit()

    def _record_success(self, is_probe: bool) -> None:

        with self._lock:

            if is_probe:

                if self._state == CircuitState.HALF_OPEN:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._opened_at = None
                    self._probe_in_progress = False

            elif self._state == CircuitState.CLOSED:

                self._failure_count = 0

    def _open_circuit(self) -> None:

        self._state = CircuitState.OPEN
        self._opened_at = self.clock()
        self._probe_in_progress = False
