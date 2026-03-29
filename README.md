# Hybrid AI-Based Voice-Driven Sales Decision Intelligence System

This project is a full-stack AI system that analyzes conversations between Sales Persons and Clients and converts them into structured, data-driven sales insights. It combines speech recognition, natural language processing, machine learning, and rule-based decision logic into a unified pipeline.

---

## Overview

The system enables Sales Persons to upload meeting audio or text summaries. It processes this input through multiple AI layers to extract meaningful features, predict deal outcomes, and recommend the most effective next action.

The architecture is modular and designed to simulate real-world enterprise sales intelligence systems.

---

## Key Features

* Speech-to-text processing using a locally deployed model
* NLP-based feature extraction from conversation data
* Machine learning models for:

  * Closure probability prediction
  * Strategy recommendation
* Rule-based decision engine for business logic
* API-based backend using FastAPI
* Support for both text and voice input

---

## System Architecture

Input (Audio/Text)
↓
Speech Processing (Whisper Model)
↓
Text Processing (NLP Feature Extraction)
↓
Machine Learning Models
↓
Decision Engine (Rules + Predictions)
↓
Final Outputs (Insights and Recommendations)

---

## Outputs

The system generates structured outputs including:

* Extracted features from conversation
* Closure probability (0–100%)
* Predicted deal outcome
* Recommended strategy
* Decision summary
* Risk level

---

## Tech Stack

Frontend

* HTML, CSS, JavaScript

Backend

* FastAPI
* Uvicorn

AI and Machine Learning

* OpenAI Whisper (local speech-to-text)
* TextBlob (NLP processing)
* Scikit-learn (ML models)
* NumPy, Pandas

Model Management

* Joblib (model serialization)

---

## Project Structure

```bash
backend/
  main.py
  services/
    whisper_service.py
    nlp_service.py
    decision_engine.py
  models/
    closure_model.pkl
    closure_scaler.pkl
    strategy_model.pkl
    strategy_scaler.pkl

frontend/
  index.html
  script.js
  style.css

artificial_company/
  products.json
  pricing_policy.json
  discount_rules.json
  stock_data.json

requirements.txt
```

---

## Workflow

1. Sales Person uploads meeting audio or text
2. Audio is transcribed using a speech recognition model
3. Text is analyzed to extract structured features
4. Features are passed into trained machine learning models
5. Predictions are combined with business rules
6. System generates actionable insights and recommendations

---

## API Endpoints

GET /

* Returns system status and available endpoints

GET /health

* Health check for backend and model availability

POST /analyze-meeting

* Input: Text
* Output: Features, predictions, and decision insights

POST /analyze-voice

* Input: Audio file
* Output: Transcript, features, predictions, and insights

---

## Notes

* All AI components run locally; no external API keys are required
* Pre-trained models must be available in the models directory
* Audio files should be in supported formats such as wav, mp3, or m4a

---

## Future Improvements

* Integration with advanced large language models
* Real-time speech processing
* Improved NLP feature extraction
* Interactive frontend dashboard
* Model retraining pipeline

---

## Summary

This system demonstrates how unstructured human conversations can be transformed into structured, actionable intelligence using a hybrid AI approach. It combines speech processing, NLP, machine learning, and rule-based reasoning to support better sales decision-making.

---

## Author

Antony Rojes M
BE Computer Science and Engineering
