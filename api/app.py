import base64
import os
import eye_tracking
import cv2
import numpy as np
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder="./templates/static")
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode="eventlet")

def base64_to_image(base64_string):
    """
    The base64_to_image function accepts a base64 encoded string and returns an image.
    The function extracts the base64 binary data from the input string, decodes it, converts 
    the bytes to numpy array, and then decodes the numpy array as an image using OpenCV.
    
    :param base64_string: Pass the base64 encoded image string to the function
    :return: An image
    """
    base64_data = base64_string.split(",")[1]
    image_bytes = base64.b64decode(base64_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


@socketio.on("connect")
def test_connect():
    """
    The test_connect function is used to test the connection between the client and server.
    It sends a message to the client letting it know that it has successfully connected.
    
    :return: A 'connected' string
    """
    print("Connected")
    emit("my response", {"data": "Connected"})




@socketio.on("image")
def receive_image(image):
    """
    The receive_image function takes in an image from the webcam, converts it to grayscale, and then emits
    the processed image back to the client.


    :param image: Pass the image data to the receive_image function
    :return: The image that was received from the client
    """
    # Decode the base64-encoded image data
    image = base64_to_image(image)
    frame_resized = cv2.resize(image, (640, 360))

    eye = eye_tracking.track(frame_resized, 120)
    if eye is None:
        return
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, frame_encoded = cv2.imencode(".jpg", eye, encode_param)
    processed_img_data = base64.b64encode(frame_encoded).decode()
    b64_src = "data:image/jpg;base64,"
    processed_img_data = b64_src + processed_img_data
    emit("processed_image", processed_img_data)


@app.route("/")
def index():
    """
    The index function returns the index.html template, which is a landing page for users.
    
    :return: The index
    """
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')