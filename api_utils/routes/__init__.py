from api_utils.routes.config_routes import create_config_routes
from api_utils.routes.explorer_routes import create_explorer_routes
from api_utils.routes.metric_routes import create_metric_routes
from api_utils.routes.shared_get_routes import (
    create_aggregation_get_routes,
    create_encounter_get_routes,
    create_event_get_routes,
    create_external_event_get_routes,
    create_journey_get_routes,
    create_mentee_get_routes,
    create_note_get_routes,
    create_notification_get_routes,
    create_path_get_routes,
    create_plan_get_routes,
    create_profile_get_routes,
    create_resource_get_routes,
)

__all__ = [
    "create_config_routes",
    "create_explorer_routes",
    "create_metric_routes",
    "create_aggregation_get_routes",
    "create_encounter_get_routes",
    "create_event_get_routes",
    "create_external_event_get_routes",
    "create_journey_get_routes",
    "create_mentee_get_routes",
    "create_note_get_routes",
    "create_notification_get_routes",
    "create_path_get_routes",
    "create_plan_get_routes",
    "create_profile_get_routes",
    "create_resource_get_routes",
]
