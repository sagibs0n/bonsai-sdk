import csv
import json
import os
import sys


class Writer(object):

    # TODO(oren.leiman): it might be the case that the JSON records should
    # be nested, because JSON. If that's the case, most of this code winds
    # up in CSVWriter, methods become stubs, JSONWriter gets its own impl.

    """
    An abstract base class for streaming simulation data to a file.
    Two supported specializations (CSVWriter and JSONWriter) are
    provided below.

    When recording is enabled (see `--record` flag), `Simulator`
    automatically creates and instance of `Writer` in its constructor.
    Format specialization is chosen based on the configured log filename.

    Example Code:

    ```python
    class MySimulator(bonsai_ai.Simulator):
        ...
        def simulate(self, action):
            # your simulation code goes here
            self.writer.record_append({'foo': 23,
                                       'bar': 24})
            self.writer.record_append({'baz': 33}, prefix='qux')
        ...

    if __name__ == '__main__':
        config = Config(sys.argv)
        brain = Brain(config)
        sim = MySimulator(brain)
        sim.enable_keys(['foo', 'bar'])
        sim.enable_keys(['baz'], prefix='qux')
        # code to run the simulator goes here
    ```
    """

    def __init__(self, record_file):
        self._schema = []
        self._current_record = {}
        self._record_file = record_file
        self._logfile = None

    def _add_prefix(self, key, prefix):
        if prefix is not None:
            key = prefix + '.' + key
        return key

    def _insert_kvp(self, key, value, prefix=None):
        key = self._add_prefix(key, prefix)
        if key in self._schema:
            self._current_record[key] = value
        else:
            raise KeyError(
                "({}) Current Writer schema: {}".format(
                    key, repr(self._schema)))

    def _open_logfile(self):
        if sys.version_info[0] < 3:
            self._logfile = open(self._record_file, 'ab', 1)
        else:
            self._logfile = open(self._record_file, 'a', 1, newline='')

    @property
    def record_file(self):
        """Get or set the record file.
        When a new record file is set, the previous file will be
        closed and subsequent lines will be recorded to the new file.
        """
        return self._record_file

    @record_file.setter
    def record_file(self, new_file):
        self._record_file = new_file
        if self._logfile is not None:
            self._logfile.close()
            self._logfile = None

    def add(self, obj, prefix=None):
        """ Adds the given dictionary to the current log line.

        Un-enabled keys are silently ignored
        """
        for key in obj.keys():
            self._insert_kvp(key, obj[key], prefix)

    def enable_keys(self, keys, prefix=None):
        """ Enable the given keys, prepended by prefix, for all subsequent
        log events for this writer.
        """
        keys = [self._add_prefix(k, prefix) for k in keys]
        keys = [k for k in keys if k not in self._schema]
        for key in keys:
            self._schema.append(key)
            self._current_record[key] = None

    def _reset(self):
        self._logfile.flush()
        self._current_record = dict((k, None) for k in self._schema)

    def write(self):
        """
        Writes the current log line to disk.
        You shouldn't need this method in normal use; it is called by the
        `Simulator` base class at the end of each simulation step.

        However, should your particular use case require calling `write`
        manually, here it is.
        """
        raise NotImplementedError(
            "Invalid log file: {}".format(self._logfile))

    def close(self):
        """
        Close the log file.
        As with `write`, this method is called automatically by
        `Simulator`. You generally shouldn't need to call it by hand.
        """
        self._logfile.close()


class CSVWriter(Writer):
    """
    A class to export simulation data in CSV form, line by line.
    """

    def __init__(self, record_file, delimiter=','):
        self._needs_header = True
        if os.path.exists(record_file):
            self._needs_header = False
        super(CSVWriter, self).__init__(record_file)
        self._delimiter = delimiter

    def write(self):
        if self._logfile is None:
            needs_header = not os.path.exists(self._record_file)
            self._open_logfile()
            self._writer = csv.DictWriter(
                self._logfile, self._schema, delimiter=self._delimiter)

            if needs_header:
                self._writer.writeheader()

        self._writer.writerow(self._current_record)
        self._reset()


class JSONWriter(Writer):
    """
    A class to stream simulation data in JSON form, object by object.
    Delimited by '\n'. This is done for streaming purposes, to avoid
    constructing large arrays in memory.
    """

    def __init__(self, record_file):
        super(JSONWriter, self).__init__(record_file)

    def write(self):
        if self._logfile is None:
            self._open_logfile()

        self._logfile.write("{}\n".format(
            json.dumps(self._current_record)))
        self._reset()
