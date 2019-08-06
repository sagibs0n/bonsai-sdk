from __future__ import absolute_import
from __future__ import print_function

import time
import os
import sys

from bonsai_ai.logger import Logger

# relevant SO: https://stackoverflow.com/questions/18812614/
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, '_vendor')

sys.path.append(vendor_dir)

from product_insights import (LogManager, EventProperties,
                              LogManagerConfiguration)

log = Logger()

_TELEMETRY_BLACKLIST = [
    "localhost",
    "testing",
    "127.0.0.1",
    "staging",
]

def init_logger(project_key):
    configuration = LogManagerConfiguration()

    LogManager.initialize(project_key, configuration)
    logger = LogManager.get_logger("", project_key)
    return logger

def _blacklisted_host(url: str) -> bool:
    return url is not None and any(
        [host in url for host in _TELEMETRY_BLACKLIST])

class AriaWriter():

    ARIA_PROJECT_KEY = "264ff126958641b796199416a69b577f-101f42ef-30f4-42a1-b284-3f454927cfd2-7403"

    def __init__(self, cluster_url, disable_telemetry=False):
        """
        Construct Aria Writer object

        Arguments:
        :param cluster_url: URL for bonsai cluster being used.
        :param disable_telemetry: flag to disable telemetry
        """
        self._logger = None
        if not disable_telemetry and not _blacklisted_host(cluster_url):
            self._logger = init_logger(self.ARIA_PROJECT_KEY)

    def track(self, aria_event):
        if self._logger is None:
            return

        event_props = EventProperties(aria_event.event_name)
        for key in aria_event.properties:
            event_props.set_property(key, aria_event.properties[key])

        event_id = self._logger.log_event(event_props)

        while event_id < 0:
            time.sleep(0.00001)
            event_id = self._logger.log_event(event_props)

        log.telemetry("Instrumentation Sent: {}: {}".format(
            aria_event.event_name, aria_event.properties)
        )

    def close(self):
        """
        Cleans up resources and closes Aria Writer

        NOTE: A deadlock occurs if no event is sent and writer is closed
        #12130: Find solution for deadlock
        """
        if self._logger is None:
            return

        LogManager.flush_and_tear_down(timeout=0)


class AriaEvent(object):
    def __init__(self, name, props={}):
        self.event_name = name
        self.properties = props


class SimConnecting(AriaEvent):
    def __init__(self, is_predict=False):
        super(SimConnecting, self).__init__(
            "simconnecting", {
                "IsPredict": is_predict
            })


class StartTrainingBrain(AriaEvent):
    def __init__(self, is_resume=False, brain_version=0):
        super(StartTrainingBrain, self).__init__(
            "starttrainingbrain", {
                "IsResume": is_resume,
                "VersionNum": brain_version
            })
