import threading
import time
from collections import deque

from product_insights._type_hints import *
from product_insights.pipeline.handlers.pipeline_handler import PipelineHandler
from product_insights.log_manager_resources import LogManagerResources
from product_insights.serial_number import SerialNumber
from product_insights.subscribers import SubscriberStatus

_max_upload_threads = 10


class _PackageUpload(object):
    def __init__(self, tenant, package, event_ids, upload_id):
        # type: (str, bytes, List[int], int) -> None
        self.tenant = tenant
        self.package = package
        self.event_ids = event_ids
        self.upload_id = upload_id

        self.attempts_left = 4


class PackageUploader(PipelineHandler):
    def __init__(self, resource_manager, tenant_token, input_, tenant):
        # type: (LogManagerResources, str, deque, str) -> None
        super(PackageUploader, self).__init__(resource_manager, tenant_token, input_)

        self._tenant = tenant
        # Prevents too many upload threads from existing at a time
        self.__thread_semaphore = threading.Semaphore(_max_upload_threads)

        self._in_progress = set()  # type: Set[int]
        self._upload_id = SerialNumber()

    def _upload_package(self, upload):
        # type: (_PackageUpload) -> None
        with self.__thread_semaphore:
            with self._resources.get_uploader() as uploader:
                response = uploader.upload_data(upload.package, upload.tenant)
                self._resources.event_counter.uploaded_package(len(upload.package))

                if (response is None or response.status != 200) and upload.attempts_left > 0:
                    upload.attempts_left -= 1
                    self._enqueue_package(upload)
                else:
                    self._resources.event_counter.complete_events(upload.event_ids, response)

                    subscriber_update = self._resources.get_subscriber_updater()
                    subscriber_update.set_result(
                        self._tenant, upload.event_ids,
                        SubscriberStatus.UPLOAD_FAILED if response is None else response.status
                    )

                    subscriber_update.update()

                    self._in_progress.remove(upload.upload_id)

    def process_input(self, flush=False):
        while len(self.input) > 0:
            with self.__thread_semaphore:
                package, event_ids = self.input.popleft()
                upload_id = self._upload_id.consume()
                self._in_progress.add(upload_id)

                self._enqueue_package(_PackageUpload(self._tenant, package, event_ids, upload_id))

        if flush:
            self._wait_for_all_uploads()

    def _enqueue_package(self, package):
        # type: (_PackageUpload) -> None
        thread = threading.Thread(target=self._upload_package, name='Uploader thread', args=(package,))

        thread.start()

    def drop(self):
        dropped_ids = []
        for batch, sequence_ids in self.input:
            dropped_ids += sequence_ids

        self.input.clear()
        self._resources.event_counter.drop_events(len(dropped_ids))

        self._resources.update_subscribers(self._tenant, dropped_ids, SubscriberStatus.EVENT_DROPPED)

    def _wait_for_all_uploads(self):
        uploads = self._in_progress.copy()

        while len(uploads.intersection(self._in_progress)) > 0:
            time.sleep(0.01)
