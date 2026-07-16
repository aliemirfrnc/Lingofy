"""
Exception hierarchy for the Operations Backend Business Services.
"""


class BaseBusinessException(Exception):
    """Base exception for all business layer exceptions."""
    pass


class BusinessException(BaseBusinessException):
    """Exception raised for business logic violations."""
    pass


class ValidationException(BaseBusinessException):
    """Exception raised when domain validation fails."""
    pass


class InfrastructureException(BaseBusinessException):
    """Exception raised for infrastructure or repository failures."""
    pass


class ExternalProviderException(BaseBusinessException):
    """Exception raised when an external provider fails."""
    pass


# Domain-specific exceptions
class MetricsException(BusinessException):
    """Exception for metrics domain."""
    pass


class QueueException(BusinessException):
    """Exception for queue domain."""
    pass


class HealthException(BusinessException):
    """Exception for health domain."""
    pass


class NotificationException(BusinessException):
    """Exception for notification domain."""
    pass


class IncidentException(BusinessException):
    """Exception for incident domain."""
    pass


class FeatureFlagException(BusinessException):
    """Exception for feature flag domain."""
    pass


class ConfigurationException(BusinessException):
    """Exception for configuration domain."""
    pass


class ExportException(BusinessException):
    """Exception for export domain."""
    pass


class AggregationException(BusinessException):
    """Exception for aggregation domain."""
    pass
