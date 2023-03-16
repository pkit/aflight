import threading

from aflight import Aflight
import numpy as np
import pyarrow
import xgboost as xgb

app = Aflight()
model = xgb.Booster()
model.load_model("iris.xgb")
lock = threading.Lock()


def gen_names(n):
    return [f"c{i}" for i in range(n)]


@app.command("predict")
def predict(batch):
    table = pyarrow.Table.from_batches([batch])
    arr2d = np.array([col.to_numpy() for col in table])
    dmatrix = xgb.DMatrix(arr2d.T)
    try:
        lock.acquire()
        result = model.predict(dmatrix)
    finally:
        lock.release()
    table = pyarrow.Table.from_arrays(result.T,
                                      names=gen_names(result.shape[1]))

    return table.to_batches()
