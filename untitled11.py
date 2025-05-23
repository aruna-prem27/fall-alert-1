# -*- coding: utf-8 -*-
"""Untitled11.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lz9KuFLrxh2j714W9jVd3apniwyb71DQ
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import find_peaks

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Streamlit app title
st.title("📉 Fall Detection with LSTM")

# Upload Excel file
uploaded_file = st.file_uploader("glasses1_part1_features_added.xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Simulate labels if missing
    if 'LABEL' not in df.columns:
        df['LABEL'] = 0
        df.loc[df['JERK_MAG'] > df['JERK_MAG'].quantile(0.95), 'LABEL'] = 1

    # Plot feature distributions
    st.subheader("Feature Distributions by LABEL")
    features_to_plot = ['ACC_MAG', 'JERK_MAG', 'GYRO_MAG', 'PITCH', 'ROLL', 'SVM']
    for feature in features_to_plot:
        sns.histplot(df, x=feature, hue='LABEL', kde=True, element='step')
        st.pyplot()

    # Prepare features and labels
    feature_cols = ['ACC_X', 'ACC_Y', 'ACC_Z', 'JERK_X', 'JERK_Y', 'JERK_Z',
                    'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'PITCH', 'ROLL', 'SVM']
    X = df[feature_cols].values
    y = df['LABEL'].values

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Create sequences
    SEQ_LEN = 10
    def create_sequences(X, y, seq_len):
        X_seq, y_seq = [], []
        for i in range(len(X) - seq_len):
            X_seq.append(X[i:i+seq_len])
            y_seq.append(y[i+seq_len])
        return np.array(X_seq), np.array(y_seq)

    X_seq, y_seq = create_sequences(X_scaled, y, SEQ_LEN)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)

    # LSTM Model
    model = Sequential()
    model.add(LSTM(64, input_shape=(SEQ_LEN, X.shape[1]), return_sequences=False))
    model.add(Dropout(0.3))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train model
    st.subheader("Training Model...")
    history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=0)

    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    st.success(f"✅ Test Accuracy: {accuracy:.2f}")

    # Plot training history
    st.subheader("Training History")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(history.history['loss'], label="Train Loss")
    ax[0].plot(history.history['val_loss'], label="Val Loss")
    ax[0].legend()
    ax[0].set_title("Loss")

    ax[1].plot(history.history['accuracy'], label="Train Acc")
    ax[1].plot(history.history['val_accuracy'], label="Val Acc")
    ax[1].legend()
    ax[1].set_title("Accuracy")

    st.pyplot(fig)

    # Market fall statistics (example data)
    st.subheader("🧓 Elderly Fall Statistics (Survey Data)")

    labels = ['Had ≥1 fall', 'Had ≥2 falls', 'Injured in fall', 'Needed medical attention', 'No falls']
    sizes = [35, 15, 20, 10, 65]
    colors = ['orange', 'red', 'purple', 'blue', 'green']

    fig2, ax2 = plt.subplots()
    ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax2.axis('equal')
    plt.title("Elderly Fall Cases Distribution")

    st.pyplot(fig2)

    # Summary description
    st.markdown("""
    **Survey Insight**
    - 35% of elderly experienced at least one fall in a year.
    - 15% fell multiple times.
    - 20% suffered injuries due to the fall.
    - 10% required medical attention.
    - 65% reported no falls.

    This highlights the urgent need for real-time fall detection systems, especially in assisted living environments.
    """)

    # Fall peak detection section
    st.subheader("📍 Fall Peak Detection (Using JERK_MAG)")

    peak_feature = 'JERK_MAG'
    peak_threshold = df[peak_feature].quantile(0.95)

    # Detect peaks
    peaks, _ = find_peaks(df[peak_feature], height=peak_threshold, distance=10)

    # Plot with peaks
    fig3, ax3 = plt.subplots(figsize=(12, 4))
    ax3.plot(df[peak_feature], label=f"{peak_feature}", color='blue')
    ax3.plot(peaks, df[peak_feature].iloc[peaks], "x", label='Detected Peaks (Possible Falls)', color='red')
    ax3.axhline(peak_threshold, color='orange', linestyle='--', label='Peak Threshold')
    ax3.set_title(f"{peak_feature} with Detected Fall Peaks")
    ax3.set_xlabel("Sample Index")
    ax3.set_ylabel(peak_feature)
    ax3.legend()
    ax3.grid(True)

    st.pyplot(fig3)

    st.markdown(f"**Total Detected Peaks (above 95th percentile):** {len(peaks)}")
    st.dataframe(df.iloc[peaks][[peak_feature, 'LABEL']])