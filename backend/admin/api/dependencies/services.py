from backend.admin.services.interfaces import (
    IMetricsQueryService, IMetricsCommandService,
    IHealthQueryService, IQueueQueryService, IQueueCommandService,
    INotificationCommandService, IIncidentQueryService, IIncidentCommandService,
    IFeatureFlagQueryService, IFeatureFlagCommandService,
    IRuntimeConfigurationQueryService, IRuntimeConfigurationCommandService,
    IExportQueryService, IExportCommandService,
    IAggregationQueryService, IAggregationCommandService
)

# Placeholder dependencies for DI resolution in FastAPI

def get_metrics_query_service() -> IMetricsQueryService:
    raise NotImplementedError

def get_metrics_command_service() -> IMetricsCommandService:
    raise NotImplementedError

def get_health_query_service() -> IHealthQueryService:
    raise NotImplementedError

def get_queue_query_service() -> IQueueQueryService:
    raise NotImplementedError

def get_queue_command_service() -> IQueueCommandService:
    raise NotImplementedError

def get_notification_command_service() -> INotificationCommandService:
    raise NotImplementedError

def get_incident_query_service() -> IIncidentQueryService:
    raise NotImplementedError

def get_incident_command_service() -> IIncidentCommandService:
    raise NotImplementedError

def get_feature_flag_query_service() -> IFeatureFlagQueryService:
    raise NotImplementedError

def get_feature_flag_command_service() -> IFeatureFlagCommandService:
    raise NotImplementedError

def get_runtime_configuration_query_service() -> IRuntimeConfigurationQueryService:
    raise NotImplementedError

def get_runtime_configuration_command_service() -> IRuntimeConfigurationCommandService:
    raise NotImplementedError

def get_export_query_service() -> IExportQueryService:
    raise NotImplementedError

def get_export_command_service() -> IExportCommandService:
    raise NotImplementedError

def get_aggregation_query_service() -> IAggregationQueryService:
    raise NotImplementedError

def get_aggregation_command_service() -> IAggregationCommandService:
    raise NotImplementedError
