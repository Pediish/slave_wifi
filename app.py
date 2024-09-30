# app.py slave

from flask import Flask, request, jsonify
from config import Config, Logger
from database import DatabaseConnection, DatabaseOperations
from serialization import DataSerializer

Logger.configure()

app = Flask(__name__)

@app.route('/receive_data/<string:table>', methods=['POST'])
def receive_data(table):
    
    try:
        table_map = {
            
            'modem': 'slaves_modem',
            'equipment': 'slaves_equipment',
            'live_data' : 'live_data'
        }
        table_name = table_map.get(table)

        if not table_name:
            logging.error(f"Invalid table: {table}")
            return jsonify({"message": "Invalid table."}), 400
        global data
        data = request.json.get('data', [])
        print(data)
        if not isinstance(data,  list):
            logging.error("Data payload is not a list.")
            return jsonify({"message": "Invalid data format. 'data' should be a list."}), 400

        if not data:
            logging.warning("No data received in the request.")
            return jsonify({"message": "No data received."}), 400


        with DatabaseConnection(Config.DB_CONFIG) as connection:
            success = DatabaseOperations.insert_data(data, table_name, connection)

        if success:
            return jsonify({"message": f"Data successfully inserted into '{table_name}'."}), 200
        else:
            return jsonify({"message": "Failed to insert data."}), 500

    except Exception as e:
        logging.error(f"Error receiving data: {e}")
        return jsonify({"message": "Server error."}), 500


@app.route('/get_token', methods=['GET'])
def get_token():
    try:
        with DatabaseConnection(Config.DB_CONFIG) as connection:
            token = DatabaseOperations.get_slave_token(connection)
            if token is not None:
                data = DatabaseOperations.check_modem_status(connection)
                return jsonify({'token': token}), 200
            else:
                return jsonify({"error": "No data found."}), 404
    except Exception as e:
        logging.error(f"Error retrieving token: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/send_data/<string:table>', methods=['GET'])
def send_data(table):
    try:

        table_map = {
            'modem': 'modem',
            'equipment': 'equipment',
          #  'live_data': 'live_data'
        }
        table_name = table_map.get(table)
        
        if not table_name:
            logging.error(f"Invalid table: {table}")
            return jsonify({"message": "Invalid table."}), 400

        with DatabaseConnection(Config.DB_CONFIG) as connection:
            data = DatabaseOperations.fetch_data(table_name, connection)

        serialized_data = DataSerializer.serialize(data)
        return jsonify({"data": serialized_data}), 200

    except Exception as e:
        logging.error(f"Error sending data: {e}")
        return jsonify({"message": "Server error."}), 500

if __name__ == "__main__":
 
    app.run(host="0.0.0.0", port=5100, debug=False)
