import numpy as np
import pandas as pd
import joblib
import shap

from app.config import get_model_path, ALL_FEATURES, ONCHAIN_FEATURES, OFFCHAIN_FEATURES


class MLService:

    def __init__(self):
        self._model = None
        self._feature_columns = None
        self._explainer = None
    
    def load_model(self):
        model_path = get_model_path()
        print(f"Loading model from {model_path}...")
        model_data = joblib.load(model_path)
        self._model = model_data['model']
        self._feature_columns = model_data['feature_columns']
        print(f"Model loaded with {len(self._feature_columns)} features")

        print("Initializing SHAP explainer...")
        self._explainer = shap.TreeExplainer(self._model)
        print("SHAP explainer ready")
    
    @property
    def model(self):
        if self._model is None:
            self.load_model()
        return self._model
    
    @property
    def explainer(self):
        if self._explainer is None:
            self.load_model()
        return self._explainer
    
    def predict(self, df):
        import xgboost as xgb
        
        feature_cols = list(self._feature_columns)
        X_df = df[feature_cols].astype(float)
        
        dtest = xgb.DMatrix(X_df, feature_names=feature_cols)
        probabilities = self.model.get_booster().predict(dtest)
        predictions = (probabilities > 0.5).astype(int)
        
        return predictions, probabilities
    
    def get_shap_values(self, df):
        X = df[self._feature_columns].astype(float)
        shap_values = self.explainer.shap_values(X.values, check_additivity=False)
        return shap_values
    
    def get_feature_contributions(self, row):
        X = pd.DataFrame([row[self._feature_columns]]).astype(float)
        shap_values = self.explainer.shap_values(X.values, check_additivity=False)[0]
        
        contributions = {}
        for i, col in enumerate(self._feature_columns):
            contributions[col] = float(shap_values[i])
        
        on_chain = {col: contributions[col] for col in ONCHAIN_FEATURES}
        off_chain = {col: contributions[col] for col in OFFCHAIN_FEATURES}
        
        return {'on_chain': on_chain, 'off_chain': off_chain}
    
    def generate_explanation(self, contributions, prediction):
        if prediction == 0:
            return "This day shows normal transaction patterns."
        
        all_contribs = {**contributions['on_chain'], **contributions['off_chain']}
        sorted_features = sorted(all_contribs.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = sorted_features[:3]
        
        # readable names for features
        feature_names = {
            'normal_total_cnt': 'transaction count',
            'uniq_peers_cnt': 'unique transaction partners',
            'burst_max_tx_5m': 'transaction burst activity',
            'normal_sent_cnt': 'sent transaction count',
            'reddit_fraud_mention_ratio': 'fraud mentions on Reddit',
            'reddit_total_activity': 'Reddit activity',
            'reddit_avg_sentiment': 'average sentiment',
            'eth_volatility_7d': 'ETH price volatility',
            'eth_daily_return': 'ETH daily return',
            'eth_intraday_volatility': 'intraday volatility'
        }
        
        explanations = []
        for feature, value in top_features:
            if value > 0:
                name = feature_names.get(feature, feature)
                explanations.append(f"elevated {name}")
        
        if explanations:
            return f"Flagged due to: {', '.join(explanations)}."
        return "Flagged based on combined feature analysis."
    
    def get_feature_importance(self):
        importance = dict(zip(self._feature_columns, self.model.feature_importances_))
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


ml_service = MLService()
