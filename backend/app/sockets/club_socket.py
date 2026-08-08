from flask_socketio import join_room, leave_room

def register_club_socket(socketio):
    @socketio.on('join_club')
    def handle_join_club(data):
        club_id = data.get('clubId')
        if not club_id:
            return
        room = f"club_{club_id}"
        join_room(room)
        print(f"Socket joined club room {room}")

    @socketio.on('leave_club')
    def handle_leave_club(data):
        club_id = data.get('clubId')
        if not club_id:
            return
        room = f"club_{club_id}"
        leave_room(room)
        print(f"Socket left club room {room}")
