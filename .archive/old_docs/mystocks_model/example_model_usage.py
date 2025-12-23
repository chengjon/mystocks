"""
Model Layer Example - Demonstrates unified model interface

Shows how to use RandomForestModel and LightGBMModel with the same interface.

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from model import RandomForestModel, LightGBMModel


def generate_test_data(n_samples: int = 1000, n_features: int = 10):
    """Generate test data for demonstration"""
    print(f"Generating test data: {n_samples} samples, {n_features} features")

    # Create random features
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)],
    )

    # Classification target (binary)
    y_class = pd.Series(
        (X.iloc[:, :3].sum(axis=1) > 0).astype(int), name="target_class"
    )

    # Regression target (continuous)
    y_reg = pd.Series(
        X.iloc[:, :5].sum(axis=1) * 100 + np.random.randn(n_samples) * 10 + 3000,
        name="target_price",
    )

    return X, y_class, y_reg


def test_random_forest():
    """Test Random Forest model"""
    print("\n" + "=" * 70)
    print("Test 1: Random Forest Model (Classification)")
    print("=" * 70)

    # Generate data
    X, y_class, _ = generate_test_data(1000, 10)

    # Create model
    print("\n1. Creating Random Forest model...")
    model = RandomForestModel(n_estimators=50, max_depth=8)
    print(f"   Model: {model.model_name}")
    print(f"   Trained: {model.is_fitted()}")

    # Train model
    print("\n2. Training model...")
    metrics = model.fit(X, y_class, test_size=0.2)

    print("   ✅ Training complete")
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall: {metrics['recall']:.4f}")
    print(f"   F1 Score: {metrics['f1_score']:.4f}")
    print(f"   Train samples: {metrics['train_samples']}")
    print(f"   Test samples: {metrics['test_samples']}")

    # Predict
    print("\n3. Making predictions...")
    X_test = X.iloc[:10]
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    print(f"   First 5 predictions: {predictions[:5]}")
    print(f"   First 5 probabilities: {probabilities[:5].round(3)}")

    # Save model
    print("\n4. Saving model...")
    model_path = "models/random_forest_test.pkl"
    model.save_model(model_path)
    print(f"   ✅ Model saved: {model_path}")

    # Load model
    print("\n5. Loading model...")
    model2 = RandomForestModel()
    model2.load_model(model_path)
    predictions2 = model2.predict(X_test)
    print("   ✅ Model loaded")
    print(f"   Predictions match: {np.array_equal(predictions, predictions2)}")

    print("\n✅ Random Forest test complete!")


def test_lightgbm():
    """Test LightGBM model"""
    print("\n" + "=" * 70)
    print("Test 2: LightGBM Model (Regression)")
    print("=" * 70)

    # Generate data
    X, _, y_reg = generate_test_data(1000, 15)

    # Create model
    print("\n1. Creating LightGBM model...")
    model = LightGBMModel()
    print(f"   Model: {model.model_name}")
    print(f"   Trained: {model.is_fitted()}")

    # Train model
    print("\n2. Training model...")
    metrics = model.fit(X, y_reg, test_size=0.2)

    print("   ✅ Training complete")
    print(f"   RMSE: {metrics['rmse']:.2f}")
    print(f"   MAE: {metrics['mae']:.2f}")
    print(f"   R² Score: {metrics['r2_score']:.4f}")
    print(f"   MAPE: {metrics.get('mape', 'N/A'):.2f}%")
    print(f"   Train samples: {metrics['train_samples']}")
    print(f"   Test samples: {metrics['test_samples']}")

    # Predict
    print("\n3. Making predictions...")
    X_test = X.iloc[:10]
    y_true = y_reg.iloc[:10]
    predictions = model.predict(X_test)

    print(f"   First 5 predictions: {predictions[:5].round(2)}")
    print(f"   First 5 true values: {y_true.values[:5].round(2)}")

    # Save model
    print("\n4. Saving model...")
    model_path = "models/lightgbm_test.pkl"
    model.save_model(model_path)
    print(f"   ✅ Model saved: {model_path}")

    # Load model
    print("\n5. Loading model...")
    model2 = LightGBMModel()
    model2.load_model(model_path)
    predictions2 = model2.predict(X_test)
    print("   ✅ Model loaded")
    print(f"   Predictions match: {np.allclose(predictions, predictions2)}")

    print("\n✅ LightGBM test complete!")


def test_unified_interface():
    """Test unified interface - both models work the same way"""
    print("\n" + "=" * 70)
    print("Test 3: Unified Interface Demonstration")
    print("=" * 70)

    X, y_class, y_reg = generate_test_data(500, 10)

    # List of models to test
    models = [
        ("RandomForest", RandomForestModel(n_estimators=30), X, y_class),
        ("LightGBM", LightGBMModel(), X, y_reg),
    ]

    print("\nTesting unified interface for multiple models:\n")

    for name, model, X_data, y_data in models:
        print(f"Model: {name}")
        print(f"  - Initial state: Trained={model.is_fitted()}")

        # Fit
        metrics = model.fit(X_data, y_data, test_size=0.2)
        print(f"  - After fit: Trained={model.is_fitted()}")

        # Predict
        predictions = model.predict(X_data.iloc[:5])
        print(f"  - Predictions shape: {predictions.shape}")

        # Save/Load
        path = f"models/{name.lower()}_unified_test.pkl"
        model.save_model(path)
        print(f"  - Saved to: {path}")

        model2 = type(model)()  # Create new instance
        model2.load_model(path)
        print(f"  - Loaded successfully: Trained={model2.is_fitted()}")
        print()

    print("✅ All models conform to unified interface!")


if __name__ == "__main__":
    print("=" * 70)
    print("MyStocks Model Layer - Unified Interface Examples")
    print("=" * 70)

    # Run tests
    try:
        test_random_forest()
    except Exception as e:
        print(f"\n❌ Random Forest test failed: {e}")

    try:
        test_lightgbm()
    except Exception as e:
        print(f"\n❌ LightGBM test failed: {e}")

    try:
        test_unified_interface()
    except Exception as e:
        print(f"\n❌ Unified interface test failed: {e}")

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
    print("=" * 70)
