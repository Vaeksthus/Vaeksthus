# Simple flask emit test with extra steps
from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading
import random

import smbus 
import time 
import sqlite3
from datetime import datetime

import board
import adafruit_dht

import base64
from matplotlib.figure import Figure
from io import BytesIO

### Jordfugter

bus = smbus.SMBus(1) # RPi revision 2 (0 for revision 1) 
i2c_address = 0x4B # default address for Jordfugter. Testet med eksempel i prog10 slides

### DHT 11

dhtDevice = adafruit_dht.DHT11(board.D24)  # Use the correct GPIO pin

### Database

# Connect to the database
# conn = sqlite3.connect("example.db")
conn = sqlite3.connect("example.db", check_same_thread=False)
cursor = conn.cursor()

# Create a table for temperature readings
cursor.execute('''
    CREATE TABLE IF NOT EXISTS temp_humi_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL,
        earthhumidity REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Function to insert a value reading with automatic timestamp
def insert_temperature(temperature, humidity, earthhumidity):
    cursor.execute('''
        INSERT INTO temp_humi_readings (temperature, humidity, earthhumidity)
        VALUES (?, ?, ?)
    ''', (temperature, humidity, earthhumidity))
    conn.commit()

# Function to fetch all readings
def fetch_all_temperatures():
    cursor.execute("SELECT * FROM temp_humi_readings")
    return cursor.fetchall()

def fetch_temperatures_last_x_minutes(minutes):
    # Query to get temperatures from the last 'minutes' minutes
    cursor.execute(f'''
        SELECT * FROM temp_humi_readings
        WHERE timestamp >= DATETIME('now', ?)
    ''', (f'-{minutes} minutes',))
    return cursor.fetchall()


### Matplotlib Graphs :D


def create_graph(minuts):
    print(f"Create Graph Function is running")
    # Fetch recent data from database
    recent_data = fetch_temperatures_last_x_minutes(minuts)

    # Check to make sure things don't go south, in case no readings are returned
    if not recent_data:
        print(f"if not recent_data: was run :(")
        return None
    
    # Time stuff - DONT TOUCH!
    # One row looks like:
    # (id, temperature, humidity, earthhumidity, timestamp)
    # row[4] says that we want the fith element (timestamp) in the recent_data pull from the SQLite database
    # The timestamp looks like this:
    # '2025-12-31 17:59:30'
    # [-8] slices the last 8 charaters from the timestamp string, which gives us:
    #  17:59:30'
    times = [row[4][-8:] for row in recent_data]  # Only show HH:MM:SS
    # Row[3] says that we want the forth element:
    # (id, temperature, humidity, earthhumidity, timestamp)
    values = [row[3] for row in recent_data]  # Earth humidity

    fig = Figure()
    ax = fig.subplots()
    ax.plot(times, values, marker='o')
    ax.set_title(f"Earth Humidity (Last {minuts} Minutes)")
    ax.set_ylabel("Value")
    ax.set_xlabel("Time")
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    #print(f"Trying to print image - Hoping for the best...")
    #print(image_base64)
    return image_base64

### Flask

# Create Flask app and wrap with SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Webpage / Homepage route
@app.route('/')
def index():
    return '''
    <html>
        <head>
            <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
        </head>
        <body>
            <h1>Sensor Value:</h1>
            <div id="value">Waiting...</div>

            <h1>Live Graph</h1>
            <img id="graph" src="" alt="Graph will appear here... ETA: 5 seconds" style="width:600px; border:1px solid #ccc;"/>

            <script>
                var socket = io();

                // Update sensor value
                socket.on('sensor_data', function(data) {
                    document.getElementById('value').innerText = data.value;
                });

                // Update graph
                socket.on('sensor_graph', function(data) {
                    document.getElementById('graph').src = 'data:image/png;base64,' + data.image;
                });
            </script>
        </body>
    </html>
    '''

@app.route('/graf/')
def graf():
    # Generate the figure **without using pyplot**. 
    fig = Figure() 
    ax = fig.subplots()# tilader flere plots i samme figur 
    ax.plot([1, 2]) #Defaults y and increments 1 on x axis 
    # Save it to a temporary buffer. 
    buf = BytesIO() 
    fig.savefig(buf) 
    # Embed the result in the html output. 
    data = base64.b64encode(buf.getbuffer()).decode("ascii") 
    return render_template('graf1.html', graf = data)

# Background loop that sends data every 5 seconds
def sensor_loop():
    while True:        
        # Reads word (2 bytes) as int - 0 is comm byte 
        rd = bus.read_word_data(i2c_address, 0) 
        # Exchanges high and low bytes 
        data = ((rd & 0xFF) << 8) | ((rd & 0xFF00) >> 8) # Ignores two least significiant bits 
        data = data >> 2

        mychecksum = "Reset = Good"

        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print(f"Temp={temperature}°C  Humidity={humidity}%")
        except RuntimeError as error:
            mychecksum = "Bad"
            print(f"Error reading from DHT11: {error}")
        if mychecksum != "Bad":
            print("Temperature   : ", temperature)
            print("Humidity      : ", humidity)
            print("Earth Humidity: ", data)
            # insert_temperature(temperature, humidity, earthhumidity)
            insert_temperature(temperature, humidity, data)
        print("Tempartures last 2 minuttes")
        print(fetch_temperatures_last_x_minutes(2))
        time.sleep(5)
        print("Sending:", data)
        socketio.emit('sensor_data', {'value': data})

        # Creating and making sure something is returned by create_graph function
        graph_img = create_graph(5)
        if graph_img:
            socketio.emit('sensor_graph', {'image': graph_img})
        
        time.sleep(1)

# Start background thread and run server
if __name__ == '__main__':
    threading.Thread(target=sensor_loop, daemon=True).start() #Starts Sensor Loop with threading enabled
    socketio.run(app, host='0.0.0.0', port=5000)



print("Temperature Readings:", fetch_all_temperatures())
print("Tempartures last 2 minuttes", fetch_temperatures_last_x_minutes(2))

# Close the connection
conn.close()
