from flask_socketio import join_room, leave_room

def register_event_socket(socketio):
    @socketio.on('join_event')
    def handle_join_event(data):
        event_id = data.get('eventId')
        if not event_id:
            return
        room = f"event_{event_id}"
        join_room(room)
        print(f"Socket joined event room {room}")

    @socketio.on('leave_event')
    def handle_leave_event(data):
        event_id = data.get('eventId')
        if not event_id:
            return
        room = f"event_{event_id}"
        leave_room(room)
        print(f"Socket left event room {room}")

    @socketio.on('join_events')
    def handle_join_events():
        join_room('events_room')
        print("Socket joined global events_room")
