from threading import Lock

from product_insights import util
from product_insights._type_hints import *
from product_insights.pi_schemas import CsEvent
from product_insights.log_manager_resources import LogManagerResources
from product_insights.pipeline.handlers.event_batcher import EventBatcher
from product_insights.pipeline.handlers.event_encoder import EventEncoder
from product_insights.pipeline.handlers.input_buffer import InputBuffer
from product_insights.pipeline.handlers.package_uploader import PackageUploader


class EventPipeline(object):
    # __pipelines has all the event pipelines in use. The last handler in each pipeline tuple
    # is expected to be the event uploader.
    __pipelines = {}  # type: Dict[str, Tuple[InputBuffer, EventEncoder, EventBatcher, PackageUploader]]
    __locks = {}  # type: Dict[str, Lock]

    @staticmethod
    def initialize(resource_manager, tenant, max_upload_size):
        # type: (LogManagerResources, str, int) -> None
        input_buffer = InputBuffer(resource_manager, tenant)
        encoder = EventEncoder(resource_manager, tenant, input_=input_buffer.output)
        packager = EventBatcher(
            resource_manager, tenant, max_package_size=max_upload_size,
            max_batch_size=resource_manager.log_manager_configuration.max_events_to_batch, input_=encoder.output
        )
        uploader = PackageUploader(resource_manager, tenant, input_=packager.output, tenant=tenant)

        EventPipeline.__pipelines[tenant] = (input_buffer, encoder, packager, uploader)
        EventPipeline.__locks[tenant] = Lock()

    # Step 0: Enqueue an event
    @staticmethod
    def enqueue(tenant_token, cs_event, sequence_id):
        # type: (str, CsEvent, int) -> None
        EventPipeline.__pipelines[tenant_token][0].input.append((cs_event, sequence_id))

    @staticmethod
    def drop_events(tenant_token):
        # type: (str) -> bool
        with EventPipeline.__locks[tenant_token]:
            for handler in EventPipeline.__pipelines[tenant_token][:-1]:
                if len(handler.input) > 0:
                    handler.drop()
                    return True

        return False

    @staticmethod
    def process(tenants, flush=False):
        # type: (Union[str, Iterable[str]], bool) -> None
        for tenant in EventPipeline._as_iterable(tenants):
            with EventPipeline.__locks[tenant]:
                for handler in EventPipeline.__pipelines[tenant][:-1]:
                    handler.process_input(flush=flush)

    @staticmethod
    def upload(tenants, flush=False):
        # type: (Union[str, Iterable[str]], bool) -> None
        for tenant in EventPipeline._as_iterable(tenants):
            with EventPipeline.__locks[tenant]:
                EventPipeline.__pipelines[tenant][-1].process_input(flush=flush)

    @staticmethod
    def flush(tenant):
        # type: (Union[str, Iterable[str]]) -> None
        EventPipeline.process(tenant, flush=True)
        EventPipeline.upload(tenant, flush=True)

    @staticmethod
    def _as_iterable(obj):
        if util.is_str(obj):
            return {obj}
        return obj
