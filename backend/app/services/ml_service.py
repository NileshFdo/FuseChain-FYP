import numpy as np
import pandas as pd
import joblib
import shap

from app.config import (
    get_model_path, ALL_FEATURES,
    ONCHAIN_FEATURES, MARKET_FEATURES, REDDIT_FEATURES, TWITTER_FEATURES,
    FEATURE_DISPLAY_NAMES,
)


class MLService:

    def __init__(self):
        self._model = None
        self._feature_columns = None
        self._explainer = None
        self._optimal_threshold = 0.5

    def load_model(self):
        model_path = get_model_path()
        print(f"Loading model from {model_path}...")
        model_data = joblib.load(model_path)
        self._model = model_data['model']
        self._feature_columns = model_data['feature_columns']
        self._optimal_threshold = model_data.get('optimal_threshold', 0.5)
        print(f"Model loaded with {len(self._feature_columns)} features")
        print(f"Optimal threshold: {self._optimal_threshold:.3f}")

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

    @property
    def optimal_threshold(self):
        if self._model is None:
            self.load_model()
        return self._optimal_threshold

    def predict(self, df: pd.DataFrame):
        """Return (predictions, probabilities) for each row in df."""
        import xgboost as xgb

        feature_cols = list(self._feature_columns)
        X_df = df[feature_cols].astype(float)

        dtest = xgb.DMatrix(X_df, feature_names=feature_cols)
        probabilities = self.model.get_booster().predict(dtest)
        predictions = (probabilities > self._optimal_threshold).astype(int)

        return predictions, probabilities

    def predict_single(self, row: pd.Series):
        """Convenience: predict for a single address profile row."""
        df = pd.DataFrame([row[self._feature_columns]]).astype(float)
        preds, probs = self.predict(df)
        return int(preds[0]), float(probs[0])

    def get_shap_values(self, df: pd.DataFrame):
        X = df[self._feature_columns].astype(float)
        return self.explainer.shap_values(X.values, check_additivity=False)

    def get_feature_contributions(self, row: pd.Series):
        """Return SHAP contributions grouped by modality."""
        X = pd.DataFrame([row[self._feature_columns]]).astype(float)
        shap_values = self.explainer.shap_values(X.values, check_additivity=False)[0]

        contributions = {}
        for i, col in enumerate(self._feature_columns):
            contributions[col] = float(shap_values[i])

        on_chain = {c: contributions.get(c, 0) for c in ONCHAIN_FEATURES if c in contributions}
        market = {c: contributions.get(c, 0) for c in MARKET_FEATURES if c in contributions}
        reddit = {c: contributions.get(c, 0) for c in REDDIT_FEATURES if c in contributions}
        twitter = {c: contributions.get(c, 0) for c in TWITTER_FEATURES if c in contributions}

        return {
            'on_chain': on_chain,
            'market': market,
            'reddit': reddit,
            'twitter': twitter,
        }

    def generate_top_reasons(self, contributions: dict, profile: pd.Series = None, n: int = 5):
        """Return human-readable top-N reasons from SHAP contributions with rich context."""
        all_contribs = {}
        for group in contributions.values():
            all_contribs.update(group)

        sorted_features = sorted(all_contribs.items(), key=lambda x: abs(x[1]), reverse=True)
        top = sorted_features[:n]

        reasons = []
        for feature, shap_val in top:
            display = FEATURE_DISPLAY_NAMES.get(feature, feature)
            direction = "elevated" if shap_val > 0 else "unusually low"

            # If we have the actual feature value and dataset stats, make it richer
            if profile is not None and feature in profile.index:
                feat_value = float(profile[feature])
                reasons.append(self._build_rich_reason(feature, display, feat_value, shap_val, direction))
            else:
                reasons.append(f"{direction} {display}")

        return reasons

    def _build_rich_reason(self, feature: str, display_name: str, value: float, shap_val: float, direction: str):
        """Build a contextual sentence for a single feature."""
        from app.services.data_service import data_service

        # Get dataset statistics for comparison
        stats = data_service.get_feature_stats(feature)
        if stats:
            mean_val = stats['mean']
            # Compute how many times above/below mean
            if mean_val != 0:
                ratio = value / mean_val
                if ratio > 2.0:
                    return f"{display_name} is {ratio:.1f}× above the dataset average ({value:.2f} vs avg {mean_val:.2f}), strongly increasing risk."
                elif 0 < ratio < 0.3:
                    return f"{display_name} is far below the dataset average ({value:.4f} vs avg {mean_val:.4f}), which is unusual."
                elif value == 0:
                    if shap_val > 0:
                        return f"{display_name} is zero while the dataset average is {mean_val:.4f}, contributing to risk."
                    else:
                        return f"{display_name} is zero, which is typical and reduces risk."
                elif shap_val > 0:
                    return f"{display_name} ({value:.4f}) is above normal levels, contributing to the risk flag."
                else:
                    return f"{display_name} ({value:.4f}) is within normal range, slightly reducing risk."
            else:
                if value > 0 and shap_val > 0:
                    return f"Non-zero {display_name} ({value:.4f}) detected, contributing to risk."
                elif value == 0 and shap_val < 0:
                    return f"{display_name} shows no activity, which is typical of normal addresses."
                else:
                    return f"{direction} {display_name} ({value:.4f})."
        else:
            return f"{direction} {display_name}."

    def generate_narrative(self, contributions: dict, profile: pd.Series, verdict: str, risk_score: float, n: int = 5):
        """Generate a full narrative paragraph explaining the prediction."""
        all_contribs = {}
        modality_impact = {}
        for modality, group in contributions.items():
            all_contribs.update(group)
            modality_impact[modality] = sum(v for v in group.values() if v > 0)

        sorted_features = sorted(all_contribs.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = sorted_features[:n]

        # Determine dominant modality
        dominant_modality = max(modality_impact, key=modality_impact.get)
        modality_names = {
            'on_chain': 'on-chain transaction patterns',
            'market': 'market conditions during activity',
            'reddit': 'Reddit community sentiment',
            'twitter': 'Twitter/X social signals'
        }

        # Opening sentence
        if verdict == "Scam":
            opening = f"This address was flagged as high-risk (score: {risk_score:.2%}) primarily due to {modality_names.get(dominant_modality, dominant_modality)}."
        else:
            opening = f"This address was classified as normal (score: {risk_score:.2%}) with no strong indicators of fraudulent behavior."

        # Detail sentences from top features
        detail_parts = []
        for feature, shap_val in top_features[:3]:
            display = FEATURE_DISPLAY_NAMES.get(feature, feature)
            if feature in profile.index:
                val = float(profile[feature])
                if shap_val > 0:
                    detail_parts.append(f"{display} ({val:.2f}) contributed significantly to the risk score")
                else:
                    detail_parts.append(f"{display} ({val:.2f}) actually reduced the risk score")

        details = ""
        if detail_parts:
            details = " " + ". ".join(detail_parts) + "."

        return opening + details

    def get_top_shap_features(self, contributions: dict, profile: pd.Series = None, n: int = 8):
        """Return top N features by |SHAP| for a bar chart, with modality labels."""
        all_contribs = {}
        feature_modality = {}
        for modality, group in contributions.items():
            for feat, val in group.items():
                all_contribs[feat] = val
                feature_modality[feat] = modality

        sorted_features = sorted(all_contribs.items(), key=lambda x: abs(x[1]), reverse=True)[:n]

        result = []
        for feature, shap_val in sorted_features:
            display = FEATURE_DISPLAY_NAMES.get(feature, feature)
            entry = {
                "feature": feature,
                "display_name": display,
                "shap_value": round(shap_val, 4),
                "modality": feature_modality.get(feature, "unknown"),
            }
            if profile is not None and feature in profile.index:
                entry["value"] = float(profile[feature])
            result.append(entry)

        return result

    def get_feature_importance(self):
        importance = dict(zip(self._feature_columns, self.model.feature_importances_))
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


ml_service = MLService()
