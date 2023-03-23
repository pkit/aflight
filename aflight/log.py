import datetime
import json
import logging
import uuid

from pyarrow.flight import ServerMiddlewareFactory, ServerMiddleware


class RequestLoggingMiddlewareFactory(ServerMiddlewareFactory):

    def __init__(self, logger, json_parser=json):
        super().__init__()
        self.logger = logger
        self.json = json_parser

    def start_call(self, info, headers):
        request_id = str(uuid.uuid4())
        return RequestLoggingMiddleware(
            request_id, self.logger, self.json
        )


class RequestLoggingMiddleware(ServerMiddleware):
    def __init__(self, request_id, logger, json_parser):
        super().__init__()
        self.request_id = request_id
        self.logger = logger
        self.json = json_parser

    def sending_headers(self):
        return {
            "x-request-id": self.request_id
        }

    def call_completed(self, exception):
        now = datetime.datetime.now().isoformat()
        code = 0
        desc = "OK"
        error = ""
        if exception is not None:
            if isinstance(exception, ValueError):
                code = 3
                desc = "INVALID_ARGUMENT"
                error = f"{exception}"
            else:
                code = 2
                desc = "UNKNOWN"
                error = f"{exception}"
        msg = self.json.dumps({
            "id": self.request_id,
            "ts": now,
            "code": code,
            "desc": desc,
            "error": error
        })
        self.logger.info(msg)


def get_logger(level=logging.DEBUG):
    logger = logging.getLogger("aflight")
    logger.setLevel(level)
    formatter = logging.Formatter(fmt="%(message)s", datefmt=None, style='%', validate=True)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return RequestLoggingMiddlewareFactory(logger)
