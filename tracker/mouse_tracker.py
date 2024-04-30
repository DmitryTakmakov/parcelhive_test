import json

import cv2
from pynput import mouse
from websockets.sync.server import serve, ServerConnection

from tracker.database import insert_values_into_table


def capture_camera_image(x: int, y: int):
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Can't open camera!")
        exit()
    ret, frame = camera.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting...")
    insert_values_into_table(x, y, frame)
    camera.release()


def websocket_server(websocket: ServerConnection):
    def on_move(x: int, y: int):
        msg = {"x": x, "y": y}
        websocket.send(json.dumps(msg))

    def on_click(x: int, y: int, button: mouse.Button, pressed: bool):
        if button == mouse.Button.left and pressed:
            capture_camera_image(x, y)
            websocket.send("Image information saved to db")
        elif button == mouse.Button.right and pressed:
            websocket.send("Tracking stopped")
            websocket.close()
            return False

    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


def main():
    with serve(websocket_server, "localhost", 8899) as server:
        server.serve_forever()
