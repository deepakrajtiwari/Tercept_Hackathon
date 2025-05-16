from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from datetime import datetime
import uvicorn

app = FastAPI()

# Load models and feature names
models = joblib.load("multi_metric_models.pkl")
features = joblib.load("model_features.pkl")  # list of feature columns used in model training

class PostInput(BaseModel):
    date_str: str  # e.g. "2025-05-20 14:00:00"
    company_name: str  # Required input

def prepare_features(data: PostInput):
    # Initialize all features to zero
    row = {col: 0 for col in features}

    # Parse date string
    dt = datetime.strptime(data.date_str, "%Y-%m-%d %H:%M:%S")
    row["Hour"] = dt.hour
    row["DayOfWeek"] = dt.weekday()

    # Default numeric features (can be tuned as needed)
    if "Duration" in row:
        row["Duration"] = 1000
    if "Total Metric Value" in row:
        row["Total Metric Value"] = 3
    if "Post Duration" in row:
        row["Post Duration"] = 1000

    # Default category values
    default_categories = {
        "Media Category": "IMAGE",
        "Post Type": "carousel",
        "Company Name": data.company_name
    }

    for field, value in default_categories.items():
        col_name = f"{field}_{value}"
        if col_name in row:
            row[col_name] = 1

    return pd.DataFrame([row])

@app.post("/predict_metrics/")
def predict_metrics(data: PostInput):
    try:
        input_df = prepare_features(data)
    except ValueError as e:
        return {"error": f"Date parsing error: {str(e)}"}

    output = {}
    for metric, model in models.items():
        try:
            pred = model.predict(input_df)[0]
            output[metric] = round(float(pred), 2)
        except Exception as e:
            output[metric] = f"Prediction failed: {str(e)}"

    return output

if __name__ == "__main__":
    uvicorn.run("api_new_model:app", host="0.0.0.0", port=8200, reload=True)