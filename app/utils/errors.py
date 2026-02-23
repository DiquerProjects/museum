from __future__ import annotations


class DomainError(Exception):
    pass


class InfraError(Exception):
    pass


class RetryableError(Exception):
    pass


class FatalError(Exception):
    pass
