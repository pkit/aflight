## Example Aflight service

Use xgboost `iris.xgb` pre-trained model to do a prediction

### Install requirements

```bash
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

### Run server

```bash
aflight
```

Server will load `iris.xgb` model and serve predictions over `grpc://localhost:18080`

### Run client to get a prediction

In another terminal:

```bash
python client.py
```

Client will read a bunch of input rows from `xtest.csv` and get a prediction for each one from the server
