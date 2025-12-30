import socketio
from config.settings import settings
from middleware.auth import verify_socket_token

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.MAIN_APP_URL,
    logger=True,
    engineio_logger=False
)

@sio.event
async def connect(sid, environ, auth):
    """Handle socket connection with authentication"""
    try:
        token = auth.get('token')
        if not token:
            return False
        
        user_id = verify_socket_token(token)
        # Store user_id in session
        async with sio.session(sid) as session:
            session['user_id'] = user_id
        
        return True
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

@sio.event
async def disconnect(sid):
    """Handle socket disconnection"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if user_id:
                print(f"User disconnected: {user_id}, Socket ID: {sid}")
    except Exception as e:
        print(f"Error on disconnect: {e}")