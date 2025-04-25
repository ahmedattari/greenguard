# 🤖🌱 Robo-Garden: AI-Powered Plant Monitoring System

Robo-Garden is a smart plant monitoring system that combines IoT sensors with AI chatbot capabilities to help users monitor and manage their garden effortlessly. It offers real-time data from sensors like soil moisture, air quality (MQ135), and temperature/humidity (DHT11), integrated with a conversational chatbot for intuitive interactions. With voice communication support and a Neo4j graph database for personalized memory storage, Robo-Garden brings futuristic garden care to your fingertips.

---

## 🚀 Features

### 🌿 Smart Plant Monitoring
- **Soil Moisture Sensor**: Measures how wet or dry the soil is.
- **DHT11 Sensor**: Captures real-time **temperature** and **humidity**.
- **MQ135 Sensor**: Monitors **air quality** (CO₂, NH₃, etc.).

### 🤖 AI Chatbot
- Ask natural language questions like:
  - "How much water does the plant need?"
  - "What’s the current temperature in the garden?"
  - "Is the air quality safe?"
- **Voice-enabled communication**: Chatbot can talk back!

### 🔐 Authentication System
- **Signup, Login, Logout** functionality.
- Secure and session-based access for each user.

### 🧠 Neo4j Graph Database (Memory System)
Each user has a **personalized memory**:
- **Episodic Memory**: Stores past interactions (chat history) per session.
- **Sensory Memory**: Stores real-time sensor data.
- **Social Memory**: Stores user's name, preferences, and frequently asked questions.

### 💬 Voice Communication
- Ask your garden questions **via voice** and get **spoken responses**.

---

## 🛠️ Technologies Used

| Component         | Technology                          |
|------------------|--------------------------------------|
| Backend           | Python + Flask                      |
| Database          | Neo4j (Graph Database)              |
| Frontend (Chat UI)| HTML, CSS, JavaScript               |
| Sensors           | ESP32, MQ135, DHT11, Soil Moisture  |
| Voice Features    | Web Speech API / Text-to-Speech     |
| NLP/Chatbot       | AIML or custom NLP logic             |

---
