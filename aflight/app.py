from typing import Callable

import pyarrow
import pyarrow.flight as flight

from aflight.logging import get_logger


class AflightException(Exception):
    pass


class AflightServer(flight.FlightServerBase):
    def __init__(self, app, *args, **kwargs):
        if not kwargs.get("middleware"):
            kwargs["middleware"] = {
                "logger": get_logger()
            }
        super().__init__(*args, **kwargs)
        self.app = app

    def do_exchange(self, context, descriptor, reader, writer):
        if descriptor.descriptor_type == flight.DescriptorType.CMD:
            cmd = self.app.get_command(str(descriptor.command, "utf-8"))
            if not cmd:
                raise AflightException("Unknown command")
            return self._handle(cmd, context, reader, writer)
        elif descriptor.descriptor_type == flight.DescriptorType.PATH:
            path = self.app.get_path(str(descriptor.path, "utf-8"))
            if not path:
                raise AflightException("Unknown path")
            return self._handle(path, context, reader, writer)
        else:
            raise AflightException("Unknown descriptor type")

    def _handle(self, handler: Callable[[pyarrow.RecordBatch], list[pyarrow.RecordBatch]], context, reader, writer):
        try:
            is_first_batch = True
            for batch in reader.read_chunk():
                if batch is None:
                    break
                result = handler(batch)
                if is_first_batch:
                    writer.begin(result[0].schema)
                    is_first_batch = False
                for rbatch in result:
                    writer.write_batch(rbatch)
            writer.close()
        except Exception as e:
            raise AflightException(e)


class Aflight:
    def __init__(self):
        self.commands = {}
        self.paths = {}

    def serve(self, host="localhost", port=18080):
        server = AflightServer(self, location=(host, port))
        server.serve()

    def add_handler(self, handler, command=None, path=None):
        if command:
            self.commands[command] = handler
        elif path:
            self.paths[path] = handler
        else:
            raise AflightException("should define command or path")

    def get_command(self, command):
        return self.commands.get(command)

    def get_path(self, path):
        return self.paths.get(path)

    def command(self, cmd):

        def decorator(f: Callable[[pyarrow.RecordBatch], list[pyarrow.RecordBatch]]):
            self.add_handler(f, command=cmd)
            return f

        return decorator

    def path(self, path):

        def decorator(f: Callable[[pyarrow.RecordBatch], list[pyarrow.RecordBatch]]):
            self.add_handler(f, path=path)
            return f

        return decorator
