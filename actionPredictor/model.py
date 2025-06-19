import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt

def load_data():
    X,y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model(X_train, y_train, X_test=None, y_test=None):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    params = {
        'objective': 'multi:softmax',
        'num_class': 3,
        'max_depth': 4,
        'eval_metric': 'mlogloss',
        'learning_rate': 0.1,
    }
    
    watchlist = [(dtrain, 'train'), (dtest, 'eval')]
    evals_result = {}
    model = xgb.train(params, dtrain, num_boost_round=50, evals=watchlist, early_stopping_rounds=10, evals_result=evals_result)
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
    
def main():
    X_train, X_test, y_train, y_test = load_data()
    print(f"Training data shape: {X_train.shape}, Test data shape: {X_test.shape}")
    
    model = train_model(X_train, y_train, X_test, y_test)
    y_pred = model.predict(xgb.DMatrix(X_train))
    print("Train Accuracy: ", accuracy_score(y_train, y_pred))
    
    evaluate_model(model, X_test, y_test)

if __name__ == "__main__":
    main()

