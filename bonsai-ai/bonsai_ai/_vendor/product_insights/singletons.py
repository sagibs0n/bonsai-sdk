from product_insights.log_manager_configuration import LogManagerConfiguration
from product_insights.log_manager import LogManager

stats_log_manager = LogManager()
stats_logger = stats_log_manager.initialize(
    'cdb783887a694494bab466421a591fa3-f8a13b4b-18f4-40fe-976c-c78a3cdb9b8f-7520',
    LogManagerConfiguration(
        tcp_connections=1, batching_threads_count=1, update_timer=1, flush_timer=1
    )
)

customer_log_manager = LogManager(stats_logger=stats_logger)
