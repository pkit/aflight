# Aflight: simple Arrow Flight API builder

### TL;DR

Server:

```python
import aflight

app = aflight.Aflight()

@app.command("predict")
def predict(batch):
    result = do_something_with(batch)
    return [result]

app.serve()

```

Client:

```python
from aflight.client import predict

data = some_pandas_data()
print(predict(data))

```

## Why?

Current `kserve`, `torch/serve` etc. APIs are too reliant on HTTP request/response paradigm

Using Arrow as a data format and Arrow Flight as a service produces a much better interface:

- standard
- has schema
- fast
- columnar
- batch-able

