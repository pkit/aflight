# Aflight: simple Arrow Flight API builder/runner

Loosely inspired by [Flask](https://github.com/pallets/flask)

### TL;DR

Server:

Create `app.py`

```python
import aflight

app = aflight.Aflight()

@app.command("predict")
def predict(batch):
    result = do_something_with(batch)
    return [result]
```

To Run:

```bash
aflight
```

Client:

```python
from aflight.client import predict

data = some_pandas_data()
print(predict(data))

```

## Why?

Current `kserve`, `torch/serve` etc. APIs are too reliant on HTTP request/response paradigm

Using Arrow as a data format and Arrow Flight as a service API produces a much better interface:

- standard
- has schema
- fast
- columnar
- batch-able

