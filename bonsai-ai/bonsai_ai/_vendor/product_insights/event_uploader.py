from __future__ import absolute_import

import gzip
import ssl
from six import BytesIO
from six.moves import range
from six.moves.http_client import HTTPSConnection, HTTPResponse

from product_insights import constants
from product_insights._type_hints import *


class EventUploader(object):
    def __init__(self, host='mobile.events.data.microsoft.com', max_retries=4):
        self._host = host
        self._collector_url = 'https://' + host + '/OneCollector/1.0/'
        self._connection = HTTPSConnection(self._host, timeout=10)

        self._headers = {
            'Client-Version': constants.version_string,
            'Content-Type': 'application/bond-compact-binary'
        }

        if hasattr(ssl, '_create_unverified_context'):
            # noinspection PyProtectedMember
            # TODO: Determine if this is required
            ssl._create_default_https_context = ssl._create_unverified_context

        self._max_retries = max_retries

        # TODO: Add product_insights log

    @staticmethod
    def _gzip(data):
        # type: (Union[str, bytes]) -> bytes
        """
        gzip compresses the given data and returns the result

        :param data: The data to be compressed
        :return: The compressed bytes
        """
        if type(data) is not bytes:
            data = data.encode()

        compressed = BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode='w') as gzipper:
            gzipper.write(data)

        return compressed.getvalue()

    def upload_data(self, data, tenant, gzip_compress=True):
        # type: (bytes, str, bool) -> Optional[HTTPResponse]
        """
        Uploads a package of data to the PI collector

        :param data: The data to be uploaded to the collector
        :param tenant: The tenant to send the events to
        :param gzip_compress: Whether or not to gzip compress the data before uploading
        """
        headers = self._headers.copy()
        headers['apikey'] = tenant

        if gzip_compress:
            data = self._gzip(data)
            headers['Content-Encoding'] = 'gzip'

        for _ in range(self._max_retries):
            # noinspection PyBroadException
            try:
                self._connection.request('POST', self._collector_url, body=data, headers=headers)

                response = self._connection.getresponse()
                response.read()

                return response
            except Exception as e:  # TODO: Figure out which exceptions need to be caught
                # TODO: Add product_insights log

                self._reload_connection()

    def _reload_connection(self):
        if self._connection is not None:
            self._connection.close()
        self._connection = HTTPSConnection(self._host, timeout=10)
