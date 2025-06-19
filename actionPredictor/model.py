import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import matplotlib.pyplot as plt
import json
import pandas as pd

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

PAGE_MAP = {
    'select_service': 0,
    'select_customer': 1,
}

def load_data():
    path = "agentic_chatbot_dataset_v3.jsonl"
    data = []
    with open(path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
            
    df = pd.DataFrame(data)
    df.fillna('NONE', inplace=True) 
            
    #print(data[:5]) 
    X = pd.get_dummies(df[['last_action_1', 'last_action_2', 'last_action_3']])
    y = df['action'].map(FUNCTION_MAP)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=21)
    
    with open("features.txt", "w") as f:
        for col in X_train.columns:
            f.write(col + "\n")
    
    return X_train, X_test, y_train, y_test    

def train_model(X_train, y_train, X_test=None, y_test=None):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    params = {
        'objective': 'multi:softmax',
        'num_class': 12, #Adjust based on your dataset
        'max_depth': 4,
        'eval_metric': 'mlogloss',
        'learning_rate': 0.1,
    }
    
    watchlist = [(dtrain, 'train'), (dtest, 'eval')]
    evals_result = {}
    model = xgb.train(params, dtrain, num_boost_round=100, evals=watchlist, early_stopping_rounds=10, evals_result=evals_result)
    train_log = evals_result['train']['mlogloss']
    val_log = evals_result['eval']['mlogloss']

    plt.plot(train_log, label='Train Loss')
    plt.plot(val_log, label='Validation Loss')
    plt.xlabel('Boosting Rounds')
    plt.ylabel('Log Loss')
    plt.title('Training vs Validation Loss')
    plt.legend()
    plt.show()
    return model

def evaluate_model(model, X_test, y_test):
    dtest = xgb.DMatrix(X_test, label=y_test)
    y_pred = model.predict(dtest)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"Test Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}")
    model.save_model('action_predictor_model.json')
    
def main():
    X_train, X_test, y_train, y_test = load_data()
    
    print(X_train[:5], y_train[:5]) 
    
    """model = train_model(X_train, y_train, X_test, y_test)
    y_pred = model.predict(xgb.DMatrix(X_train))
    print("Train Accuracy: ", accuracy_score(y_train, y_pred))
    
    evaluate_model(model, X_test, y_test)"""

if __name__ == "__main__":
    main()

