import cv2
import numpy as np
from tensorflow.keras.models import load_model

# 🔥 Load your trained model
model = load_model("models/attention_model.h5")

classes = ["distracted", "focused", "phone"]


def predict_attention(frame):
    """
    Returns:
    - label (str)
    - confidence (float)
    """

    try:
        # Resize image
        img = cv2.resize(frame, (224, 224))

        # Convert color
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Normalize
        img = img / 255.0

        # Add batch dimension
        img = np.expand_dims(img, axis=0)

        # Predict
        preds = model.predict(img, verbose=0)

        confidence = float(np.max(preds))
        label_index = int(np.argmax(preds))

        label = classes[label_index]

        return label, confidence

    except Exception as e:
        print("Prediction error:", e)
        return "focused", 0.0