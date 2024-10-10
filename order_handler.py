from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Import CORS
from chartink_scanner import get_dow_change,run_scanner
import subprocess
app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

@app.route('/get_dow_change', methods=['GET'])
def dow_change():
    try:
        dow_change = get_dow_change()
        response = jsonify({'dow_change': dow_change}), 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example place_order function
def place_order(scrip, action):
    with open("orders.txt", "a") as file:
        file.write(f"{scrip},{action}\n")
    return f"Order placed for {scrip} with action {action}"

@app.route('/place_order', methods=['POST'])
def handle_place_order():
    try:
        data = request.json
        scrip = data['scrip']
        action = data['action']
        result = place_order(scrip, action)         
        response = jsonify({"message": result}), 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except KeyError:
        return jsonify({"error": "Invalid input, 'scrip' or 'action' key is missing"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orders.txt')
def get_orders():
    
    response = send_from_directory('.', 'orders.txt')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    try:
        open("orders.txt", "w").close()
        response = jsonify({"message": "Orders cleared"}), 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run_chartink_scanner', methods=['POST'])
def run_chartink_scanner():
    try:
        result = run_scanner()
        response = jsonify({'output': result}), 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
