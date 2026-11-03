
A production-oriented Python project demonstrating reliable LLM application architecture using SOLID principles, rate limiting, provider timeouts, retries, circuit breakers, and fault-tolerance patterns.

* failure_threshold: Number of consecutive qualifying failures before opening the circuit.

* recovery_timeout: Number of seconds to wait before allowing a recovery probe.

The design includes four important responsibilities:
1. Rate Limiter – controls how frequently requests are sent to the LLM provider.
2. Circuit Breaker – prevents repeated calls when the provider is experiencing failures.
3. Failure Policy – decides which provider exceptions should count as failures.
4. LLM Client – sends the ticket and receives structured classification output.

Architectural and the sequence diagrams are present in the diagram folder

To run the test
    python -m unittest tests.test_circuit_breaker -v

To run the main
    python -m src.main