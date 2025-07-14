import requests
import json
from pyaiml21 import Kernel
from glob import glob
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from py2neo import Graph, Node, Relationship

def get_sensor_data():
    url = "http://192.168.0.121/sensors"  # ✅ Your ESP32 IP
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error requesting sensor data: {e}")
        return None

def update_aiml_variables(kernel, sensor_data):
    if sensor_data:
        kernel.setPredicate("temperature", str(sensor_data['temperature']), "USER_1")
        kernel.setPredicate("humidity", str(sensor_data['humidity']), "USER_1")
        kernel.setPredicate("soil_moisture", str(sensor_data['soil_moisture']), "USER_1")
        kernel.setPredicate("air_quality", str(sensor_data['air_quality']), "USER_1")

def update_sensor_nodes(sensor_data):
    if sensor_data:
        dht11_node = graph.nodes.match("sensor", name='DHT11', user_id=current_user_id).first()
        if dht11_node:
            dht11_node['Temperature'] = str(sensor_data['temperature'])
            dht11_node['Humidity'] = str(sensor_data['humidity'])
            dht11_node['Soil_Moisture'] = str(sensor_data['soil_moisture'])
            dht11_node['Air_Quality'] = str(sensor_data['air_quality'])
            graph.push(dht11_node)

# Initialize AIML kernel
k = Kernel()
aiml_files = glob('aiml/*.aiml')
for file_path in aiml_files:
    k.learn(file_path)

# Initialize Flask and Neo4j
app = Flask(__name__)
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))
app.secret_key = 'naming'

current_user_id = None
current_episode_id = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/splash')
def splash():
    user_name = session.get('user_name', 'User')
    return render_template('splash.html', user_name=user_name)

@app.route('/chat')
def chat():
    user_name = session.get('user_name', 'User')
    return render_template('chat.html', user_name=user_name)

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    user_node = graph.nodes.match("User", email=email).first()
    if user_node:
        return "Already Registered!"
    else:
        user_node = Node("User", name=name, email=email, password=password)
        graph.create(user_node)

        k.respond("Hello", "USER_1")
        k.setPredicate('username', name, "USER_1")
        
        episodic_node = Node("Episodic", name="Episodic", user_id=user_node.identity)
        sensory_node = Node("Sensory", name="Sensory", user_id=user_node.identity)
        semantic_node = Node("Semantic", name="Semantic", user_id=user_node.identity)
        episode_node = Node("Episode", name="episode1", user_id=user_node.identity)
        social_node = Node("Social", name="Social", user_id=user_node.identity)

        dht11_node = Node("sensor", name="DHT11", user_id=user_node.identity, Temperature="0", Humidity="0", Soil_Moisture="0", Air_Quality="0")
        graph.create(episodic_node)
        graph.create(sensory_node)
        graph.create(semantic_node)
        graph.create(episode_node)
        graph.create(social_node)
        graph.create(dht11_node)

        graph.create(Relationship(user_node, "HAS", episodic_node))
        graph.create(Relationship(user_node, "HAS", sensory_node))
        graph.create(Relationship(user_node, "HAS", semantic_node))
        graph.create(Relationship(user_node, "HAS", social_node))
        graph.create(Relationship(episodic_node, "STARTS", episode_node))
        graph.create(Relationship(sensory_node, "CONTAINS", dht11_node))
        
        global current_user_id, current_episode_id
        current_user_id = user_node.identity
        current_episode_id = episode_node.identity

        session['user_name'] = name
        return redirect(url_for('splash'))

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    user_node = graph.nodes.match("User", email=email, password=password).first()
    if user_node:
        k.respond("Hi", "USER_1")
        name = user_node['name']
        k.setPredicate('username', name, "USER_1")

        global current_user_id, current_episode_id
        current_user_id = user_node.identity

        episodic_node = graph.nodes.match("Episodic", user_id=current_user_id).first()
        episode_count = len(list(graph.relationships.match((episodic_node,), r_type="STARTS")))
        new_episode_name = f"episode{episode_count + 1}"
        new_episode_node = Node("Episode", name=new_episode_name, user_id=current_user_id)

        graph.create(new_episode_node)
        current_episode_id = new_episode_node.identity
        graph.create(Relationship(episodic_node, "STARTS", new_episode_node))
        
        session['user_name'] = name
        return redirect(url_for('splash'))
    else:
        return "Don't Have an account! Register yourself first"

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get("message").lower()

    keywords = ["sensor", "temperature", "humidity", "soil", "moisture", "air", "gas", "reading"]
    if any(word in user_input for word in keywords):
        sensor_data = get_sensor_data()
        if sensor_data:
            update_aiml_variables(k, sensor_data)
            update_sensor_nodes(sensor_data)

            # Individual checks
            if "temperature" in user_input:
                response = f"🌡 Temperature: {sensor_data['temperature']}°C"
            elif "humidity" in user_input:
                response = f"💧 Humidity: {sensor_data['humidity']}%"
            elif "soil" in user_input or "moisture" in user_input:
                response = f"🌱 Soil moisture: {sensor_data['soil_moisture']}"
            elif "air" in user_input or "gas" in user_input:
                response = f"🌀 Air quality: {sensor_data['air_quality']}"
            else:
                # If general or combined request
                response = (
                    f"🌡 Temp: {sensor_data['temperature']}°C\n"
                    f"💧 Humidity: {sensor_data['humidity']}%\n"
                    f"🌱 Soil moisture: {sensor_data['soil_moisture']}\n"
                    f"🌀 Air quality: {sensor_data['air_quality']}"
                )
        else:
            response = "❌ Unable to read sensor data right now."
    else:
        response = k.respond(user_input, "USER_1")

    if current_episode_id is not None:
        episode_node = graph.nodes.get(current_episode_id)
        chats = json.loads(episode_node.get('chats', '{}'))
        prompt_count = len(chats)
        new_prompt = f"prompt{prompt_count + 1}"
        chats[new_prompt] = {"user": user_input, "bot": response}
        episode_node['chats'] = json.dumps(chats)
        graph.push(episode_node)

    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
