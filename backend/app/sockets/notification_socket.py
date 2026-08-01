from flask_socketio import join_room

def register_notification_socket(socketio):
    @socketio.on('connect')
    def handle_connect():
        print("Socket Connected")

    @socketio.on('disconnect')
    def handle_disconnect():
        print("Socker disconnected")

    @socketio.on('join')
    def handle_join(data):
        user_id = data.get("userId")
        if not user_id:
            return 
        room = f"user_{user_id}"
        join_room(room)
        print(f"User {user_id} joined {room}")