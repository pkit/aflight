import threading

import pandas
from pyarrow.flight import FlightClient, FlightDescriptor
import pyarrow


def _in_memory_read(reader, sink):
    table = reader.read_all()
    writer = pyarrow.ipc.new_stream(sink, table.schema)
    writer.write_table(table)
    writer.close()


def execute(data, **kwargs):
    return command("", data, **kwargs)


def predict(data, host="localhost", port=18080):
    """
    Run a prediction RPC against Aflight service
    :param data: data to predict on (DataFrame, ArrowTable)
    :param host: service hostname
    :param port: service port

    :returns: data in input format
    """
    return command("predict", data, host=host, port=port)


def command(cmd, data, host="localhost", port=18080):
    """
    Run an RPC against Aflight service
    :param cmd: rpc command string
    :param data: data to execute on (DataFrame, ArrowTable)
    :param host: service hostname
    :param port: service port

    :returns: data in input format
    """
    if isinstance(data, pandas.DataFrame):
        table = _rpc_for_table(cmd, pyarrow.Table.from_pandas(data), host=host, port=port)
        return table.to_pandas()
    elif isinstance(data, pyarrow.Table):
        return _rpc_for_table(cmd, data, host=host, port=port)
    else:
        raise Exception("Unknown input data format")


def _rpc_for_table(cmd, table, host, port):
    sink = pyarrow.BufferOutputStream()
    descriptor = FlightDescriptor.for_command(cmd)
    client = FlightClient(f"grpc://{host}:{port}")
    writer, reader = client.do_exchange(descriptor)
    th = threading.Thread(target=_in_memory_read, args=(reader, sink))
    th.start()
    writer.begin(table.schema)
    writer.write_table(table)
    writer.done_writing()
    th.join()
    writer.close()
    buf_reader = pyarrow.RecordBatchStreamReader(sink.getvalue())
    return buf_reader.read_all()
