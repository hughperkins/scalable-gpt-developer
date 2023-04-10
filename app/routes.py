from handlers import handle_chat_request


def setup_routes(app):
    app.router.add_route('POST', '/chat', handle_chat_request)

    # Add this line to serve the client build folder
    app.router.add_static('/', 'client/build', show_index=True)
