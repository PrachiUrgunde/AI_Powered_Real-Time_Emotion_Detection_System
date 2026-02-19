import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
import json
from collections import deque
from datetime import datetime
import pandas as pd

# ===============================
# 1️⃣ Load Model
# ===============================
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("ferNet.h5", compile=False)

model = load_model()

# ===============================
# 2️⃣ Load Emotion Labels
# ===============================
with open("class_labels.json", "r") as f:
    class_labels = json.load(f)

emotion_dict = {v: k for k, v in class_labels.items()}

# ===============================
# 3️⃣ Face Detector
# ===============================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ===============================
# 4️⃣ Streamlit Setup
# ===============================
st.set_page_config(page_title="Mood Mirror", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("🎭 Real-Time Emotion Detection")

start = st.checkbox("Start Camera")

frame_window = st.image([])

# Prediction smoothing
emotion_window = deque(maxlen=10)

# ===============================
# 5️⃣ Real-Time Detection
# ===============================
if start:

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Cannot access webcam.")
    else:
        st.success("Camera Started")

        while start:

            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5
            )

            for (x, y, w, h) in faces:

                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (48, 48))
                face = face.astype("float32") / 255.0
                face = np.reshape(face, (1, 48, 48, 1))

                prediction = model.predict(face, verbose=0)
                emotion_index = np.argmax(prediction)
                confidence = float(np.max(prediction) * 100)

                # Smooth predictions
                emotion_window.append(emotion_index)
                smooth_index = max(set(emotion_window),
                                   key=emotion_window.count)

                emotion_text = emotion_dict[smooth_index]

                # Draw box
                cv2.rectangle(frame, (x, y), (x+w, y+h),
                              (0, 255, 0), 2)

                cv2.putText(frame,
                            f"{emotion_text} ({confidence:.1f}%)",
                            (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2)

                # Save history
                st.session_state.history.insert(0, {
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Emotion": emotion_text,
                    "Confidence": f"{confidence:.2f}%"
                })

            frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        cap.release()

# ===============================
# 6️⃣ Dashboard
# ===============================
st.write("---")
st.header("📊 Emotion Analytics")

if len(st.session_state.history) > 0:

    df = pd.DataFrame(st.session_state.history)

    st.dataframe(df)

    st.subheader("Emotion Distribution")
    st.bar_chart(df["Emotion"].value_counts())

else:
    st.info("No detections yet.")

