import xgboost as xgb
import pandas as pd
import os

FUNCTION_MAP = {
    'None': 0, 
    'open_editor': 1,
    'add_service' : 2,
    'close_editor' : 3,
    'view_last_invoice' : 4,
    'list_services' : 5,
    'view_current_invoice': 6,
    'copy_previous_data': 7,
    'list_customers': 8,
    'add_customer': 9,
    'edit_customer': 10,
    'update_tax' : 11
}

def predict_action(model, last_actions):
    function_names = list(FUNCTION_MAP.keys())
    
    with open("features.txt") as f:
        feature_names = [line.strip() for line in f]

    # Initialize list of dicts
    rows = []
    for acts in last_actions:
        row = {col: False for col in feature_names}
        for i, act in enumerate(acts):
            key = f'last_action_{i+1}_{act}'
            if key in row:
                row[key] = True
        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)
    df = df.reindex(columns=feature_names, fill_value=False)
    X = xgb.DMatrix(df)
    
    predictions = model.predict(X)
    predicted_actions = [list(FUNCTION_MAP.keys())[int(pred)] for pred in predictions]
    
    print(f"Predicted actions: {predicted_actions}")

def main():
    
    model = xgb.Booster()
    model.load_model("action_predictor_model.json")
    last_actions = [
        ['open_editor', 'list_services', 'add_service'],
        ['open_editor', 'view_last_invoice', 'edit_customer']
    ]
    
    predict_action(model, last_actions)

if __name__ == "__main__":
    main() 