
import unittest

from src.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
)


class FakeClock:
    def __init__(self):
        self.current_time = 0.0

    def __call__(self):
        return self.current_time

    def advance(self, seconds):
        self.current_time += seconds


class TestFailurePolicy:

    def should_count(self, error):
        return isinstance(error, RuntimeError)


class CircuitBreakerTest(unittest.TestCase):

    def setUp(self):
        self.clock = FakeClock()

        self.breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            failure_policy=TestFailurePolicy(),
            clock=self.clock,
        )

    def test_initial_state_is_closed(self):
        self.assertEqual(
            self.breaker.state,
            CircuitState.CLOSED
        )

    def test_successful_request(self):
        result = self.breaker.execute(lambda: "success")

        self.assertEqual(result, "success")
        self.assertEqual(
            self.breaker.state,
            CircuitState.CLOSED
        )

    def test_circuit_opens_after_failure_threshold(self):

        def failing_operation():
            raise RuntimeError("Provider unavailable")

        for _ in range(3):
            with self.assertRaises(RuntimeError):
                self.breaker.execute(failing_operation)

        self.assertEqual(
            self.breaker.state,
            CircuitState.OPEN
        )

    def test_open_circuit_rejects_requests(self):

        def failing_operation():
            raise RuntimeError("Provider unavailable")

        for _ in range(3):
            with self.assertRaises(RuntimeError):
                self.breaker.execute(failing_operation)

        with self.assertRaises(CircuitOpenError):
            self.breaker.execute(lambda: "success")

    def test_successful_probe_closes_circuit(self):

        def failing_operation():
            raise RuntimeError("Provider unavailable")

        for _ in range(3):
            with self.assertRaises(RuntimeError):
                self.breaker.execute(failing_operation)

        self.clock.advance(30)

        result = self.breaker.execute(lambda: "recovered")

        self.assertEqual(result, "recovered")
        self.assertEqual(
            self.breaker.state,
            CircuitState.CLOSED
        )

    def test_failed_probe_reopens_circuit(self):

        def failing_operation():
            raise RuntimeError("Provider unavailable")

        for _ in range(3):
            with self.assertRaises(RuntimeError):
                self.breaker.execute(failing_operation)

        self.clock.advance(30)

        with self.assertRaises(RuntimeError):
            self.breaker.execute(failing_operation)

        self.assertEqual(
            self.breaker.state,
            CircuitState.OPEN
        )


if __name__ == "__main__":
    unittest.main()
