# database.py slave

import pymysql
import logging
import requests
import subprocess

class DatabaseConnection:
    """Handles database connections."""
    def __init__(self, config):
        self.config = config
        self.connection = None

    def __enter__(self):
        try:
            self.connection = pymysql.connect(**self.config)
            return self.connection
        except pymysql.MySQLError as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

class DatabaseOperations:
    """Performs database operations."""
    
    @staticmethod
    def insert_data(data, table_name, connection):
        if not data:
            logging.warning("No data provided for insertion.")
            return False

        try:
            
            with connection.cursor() as cursor:
                for record in data:
                    # Remove unnecessary columns based on the table name
                    if table_name == "slaves_modem":
                        record.pop('created_date', None)
                        record.pop('updated_at', None)
                        record.pop('modem_id', None)
                    elif table_name == "slaves_equipment":
                        record.pop('created_at', None)
                        record.pop('updated_at', None)
                        record.pop('equipment_id', None)
                    elif table_name == "live_data":
                        record.pop('timestamp', None)
                        
                        
                    if table_name == "slaves_modem":
                        table_name = "modem"   
                    if table_name == "slaves_equipment":
                        table_name = "equipment"
                    
                         

                    keys = ', '.join(f"`{key}`" for key in record.keys())
                    placeholders = ', '.join(['%s'] * len(record))
                    updates = ', '.join([f"`{key}`=VALUES(`{key}`)" for key in record.keys()])
                    sql = f"INSERT INTO `{table_name}` ({keys}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"
                    cursor.execute(sql, tuple(record.values()))
            connection.commit()
            logging.info(f"Data successfully inserted into '{table_name}'.")
            return True
        except pymysql.MySQLError as e:
            logging.error(f"Error inserting data into '{table_name}': {e}")
            connection.rollback()
            return False

    @staticmethod
    def fetch_data(table_name, connection):
        
        try:
            with connection.cursor() as cursor:
                a=cursor.execute(f"SELECT * FROM `{table_name}`")
                print(a)
                data = cursor.fetchall()
                logging.info(f"Fetched {len(data)} records from '{table_name}'.")
                return data
        except pymysql.MySQLError as e:
            logging.error(f"Error fetching data from '{table_name}': {e}")
            return []

    @staticmethod
    def get_slave_token(connection):
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT token FROM table_version WHERE table_name = %s", ('modem_slaves',))
                result = cursor.fetchone()
                if result and 'token' in result:
                    logging.info(f"Slave token retrieved: {result['token']}")
                    return result['token']
                else:
                    logging.error("Slave token not found in the database.")
                    return None
        except pymysql.MySQLError as e:
            logging.error(f"Error retrieving slave token: {e}")
            return None 
   
    def update_modem_status(self,connection, modem_data):
        try:
            with connection.cursor() as cursor:
                update_query = """
                UPDATE modem
                SET 
                    communication_protocol_id = %s,
                    communication_type = %s,
                    company_id = %s,
                    cpu_usage = %s,
                    memory_data = %s,
                    modem_ip = %s,
                    modem_lat = %s,
                    modem_lng = %s,
                    modem_location = %s,
                    modem_name = %s,
                    modem_os = %s,
                    modem_status = %s,
                    network_connection_password = %s,
                    network_type = %s,
                    public_adress = %s,
                    ram_usage = %s,
                    ssid = %s,
                    temperature_data = %s,
                    total_memory = %s,
                    total_ram = %s,
                    updated_at = NOW()
                WHERE modem_serial_no = %s;
                """
                cursor.execute(update_query, (
                    modem_data['communication_protocol_id'],
                    modem_data['communication_type'],
                    modem_data['company_id'],
                    modem_data['cpu_usage'],
                    modem_data['memory_data'],
                    modem_data['modem_ip'],
                    modem_data['modem_lat'],
                    modem_data['modem_lng'],
                    modem_data['modem_location'],
                    modem_data['modem_name'],
                    modem_data['modem_os'],
                    modem_data['modem_status'],
                    modem_data['network_connection_password'],
                    modem_data['network_type'],
                    modem_data['public_adress'],
                    modem_data['ram_usage'],
                    modem_data['ssid'],
                    modem_data['temperature_data'],
                    modem_data['total_memory'],
                    modem_data['total_ram'],
                    modem_data['modem_serial_no']  # Matching the serial number
                ))

                connection.commit()
                logging.info(f"Successfully updated modem with serial number {modem_data['modem_serial_no']}")

        except MySQLdb.Error as e:
            logging.error(f"Error updating modem status in the database: {e}")

    def check_modem_status(connection):
        with connection.cursor() as cursor:
            cursor.execute("SELECT modem_serial_no FROM modem WHERE modem_id = 1")
            slave_mac = cursor.fetchone()
        
        try:
            url = f"http://192.168.1.134:5100/check_modem"
            params = {'mac': slave_mac['modem_serial_no']}
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    DatabaseOperations().update_modem_status(connection, data['data'])
                else:
                    print(data['message'])
            else:
                print("Failed to communicate with master")

        except Exception as e:
            print(f"Error: {e}")        
