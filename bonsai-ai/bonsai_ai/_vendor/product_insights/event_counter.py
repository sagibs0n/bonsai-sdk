from product_insights._type_hints import *

from six.moves.http_client import HTTPResponse


class EventCounter(object):
    """
    EventCounter keeps track of how many events are sent through the SDK and how they end
    up. The variables kept track of are described below:

    logged: Number of events logged using Logger.log_event(). As soon as the event is in the
    hands of the SDK, it is counted here.

    completed: Number of events that made it all the way through the pipeline. If an event
    made it far enough to where the SDK attempted to upload it, it's counted here. Regardless
    of whether the uploaded was a success or failure, it gets counted.

    dropped: Number of events the SDK had to abandon. This is usually because of running out
    of space for new events.

    upload_success_count: Number of events that were uploaded with the collector responding with an
    HTTP status code of 200: OK.

    upload_failure_count: Number of events that couldn't be uploaded or had a collector response
    other than 200: OK.

    status_counts: A dictionary mapping received HTTP status codes and the number of events that
    resulted in that status code.

    event_space_left: The number of events that can still be logged before reaching
    max_events_in_memory.

    bytes_uploaded: The number of bytes that have been uploaded from the SDK. This does NOT count
    total packet size, just the size of uploaded payloads.

    packages_uploaded: The number of package upload attempts that have been made


    completed + dropped = all events the SDK handled at one point and no longer cares about.

    (completed + dropped) - logged = the number of events that are currently in the SDK pipeline.

    completed = upload_success_count + upload_failure_count

    failure_count + dropped = the number of events that failed to be properly uploaded.
    """

    def __init__(self, max_events_in_memory):
        # type: (int) -> None
        self.logged = 0
        self.completed = 0
        self.dropped = 0

        self.status_counts = {}  # type: Dict[int, int]

        self.upload_success_count = 0
        self.upload_failure_count = 0

        self.bytes_uploaded = 0
        self.packages_uploaded = 0

        self.event_space_left = max_events_in_memory

    def add_logged_event(self):
        self.logged += 1
        self.event_space_left -= 1

    def complete_events(self, event_ids, http_response):
        # type: (List[int], Optional[HTTPResponse]) -> None
        self.completed += len(event_ids)
        self.event_space_left += len(event_ids)

        if http_response is None:
            self.upload_failure_count += len(event_ids)
            return

        http_response_status = http_response.status

        if http_response_status not in self.status_counts:
            self.status_counts[http_response_status] = 0

        self.status_counts[http_response_status] += len(event_ids)

        if http_response_status == 200:
            self.upload_success_count += len(event_ids)
        else:
            self.upload_failure_count += len(event_ids)

    def drop_events(self, num_dropped):
        # type: (int) -> None
        self.dropped += num_dropped
        self.event_space_left += num_dropped

    def uploaded_package(self, num_bytes):
        # type: (int) -> None
        self.bytes_uploaded += num_bytes
        self.packages_uploaded += 1
