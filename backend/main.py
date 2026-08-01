from app import create_app
from app.extensions import socketio
from app.sockets.notification_socket import register_notification_socket
from app.utils.seed import seed_database

app = create_app()
register_notification_socket(socketio)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    seed_database(app)
    app.run(host='127.0.0.1', port=5000, debug=True)
