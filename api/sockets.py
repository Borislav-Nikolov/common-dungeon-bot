import socketio


sio = socketio.Client()


@sio.on('test_update_event')
def handle_test_update_event(data):
    test_message = data['test_message']
    print(f'Test update received. Message: {test_message}')
