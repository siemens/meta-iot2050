# Copyright (c) Siemens AG, 2026
#
# SPDX-License-Identifier: MIT

"""In-memory singleton state and live logs for firmware services."""

import queue
import threading


class FirmwareOperationLogHub:
    """Publish best-effort live messages to current subscribers."""

    _CLOSED = object()

    def __init__(self, queue_size=32):
        self.queue_size = queue_size
        self._lock = threading.Lock()
        self._subscribers = set()
        self._closed = False

    def publish(self, message):
        with self._lock:
            if self._closed:
                return
            for subscriber in tuple(self._subscribers):
                try:
                    subscriber.put_nowait({"message": str(message)})
                except queue.Full:
                    try:
                        subscriber.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        subscriber.put_nowait({
                            "message": "Some progress messages were skipped",
                        })
                    except queue.Full:
                        pass

    def subscribe(self):
        subscriber = queue.Queue(maxsize=self.queue_size)
        with self._lock:
            if self._closed:
                subscriber.put_nowait(self._CLOSED)
            else:
                self._subscribers.add(subscriber)
        return subscriber

    def unsubscribe(self, subscriber):
        with self._lock:
            self._subscribers.discard(subscriber)

    def close(self):
        with self._lock:
            self._closed = True
            for subscriber in tuple(self._subscribers):
                try:
                    subscriber.put_nowait(self._CLOSED)
                except queue.Full:
                    try:
                        subscriber.get_nowait()
                        subscriber.put_nowait(self._CLOSED)
                    except queue.Empty:
                        pass
            self._subscribers.clear()

    def reset(self):
        """Open a new live-operation generation without replaying old logs."""
        with self._lock:
            self._closed = False


class FirmwareOperationStore:
    """Store the current or latest operation for one service process."""

    def __init__(self):
        self._lock = threading.Lock()
        self._operation = None

    def admit(self, operation):
        """Atomically reject a running operation or make one current."""
        with self._lock:
            if self._operation and self._operation.get("state") == "running":
                return False
            self._operation = dict(operation)
            return True

    def update(self, **values):
        with self._lock:
            if self._operation is None:
                raise KeyError("latest")
            self._operation.update(values)

    def read(self):
        with self._lock:
            if self._operation is None:
                raise KeyError("latest")
            return dict(self._operation)
