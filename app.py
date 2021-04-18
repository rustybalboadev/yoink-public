from app import app, socket

if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", logger=False, engineio_logger=False)