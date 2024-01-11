import asyncio
import os
import sys
import torch

from contextlib import contextmanager
import time
import json

class Profiler():
    profiling_trace_events = []
    event_tid = {"counter": 1, "external": 2, "internal": 3}

    def __init__(self):
        self.enabled = os.getenv("TGI_PROFILER_ENABLED", "false").lower() == "true"
        if self.enabled:
            with open("server_events.json", "w") as outfile:
                outfile.write('{"traceEvents": ')

    @contextmanager
    def record_event(self, type, name, args=None, util=None):
        if self.enabled:
            start = time.time() * 1000000.0
            if util is not None:
                self.profiling_trace_events.append({
                "pid": 1,
                "tid": self.event_tid["counter"],
                "ph": "C",
                "name": "util",
                "ts": start,
                "args": {
                    "util": util["util"],
                    #"queue": util["queue_len"]
                }})

            event = {
                "pid": 1,
                "tid": self.event_tid[type],
                "ph": "X",
                "name": name,
                "ts": start,
                "dur": None,
                "args": args
            }
            yield

            end = time.time() * 1000000.0
            event["dur"] = end - start
            self.profiling_trace_events.append(event)

            if len(self.profiling_trace_events) > 100:
                with open("server_events.json", "a") as outfile:
                    outfile.write(json.dumps(self.profiling_trace_events))
                self.profiling_trace_events = []
        else:
            yield