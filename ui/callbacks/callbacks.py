from dash import Dash, Input, Output, html

class Callbacks:
    """Callback class for handling Dash app callbacks."""

    def __init__(self, app: Dash):
        """
        Initialize ViewportCallbacks with Dash app instance.

        Args:
            app: Dash application instance
        """
        self.app = app
        self._register_callbacks()

    def _register_callbacks(self):

        # -------- IMAGE UPLOAD CALLBACKS -------- #
        for i in range(1, 5):
            self._create_image_callback(i)

        # -------- SLIDER CALLBACKS -------- #
        for i in range(1, 5):
            self._create_slider_callback(i)


    def _create_image_callback(self, card_id):
        @self.app.callback(
            Output(f'image-display-{card_id}', 'children'),
            Input(f'upload-image-{card_id}', 'contents'),
            prevent_initial_call=True
        )
        def update_image(contents):
            if contents:
                return self.parse_uploaded_image(contents)
            return html.Div()


    def _create_slider_callback(self, card_id):
        @self.app.callback(
            Output(f'weight-slider-{card_id}', 'value'),
            Input(f'weight-slider-{card_id}', 'value'),
            prevent_initial_call=True
        )
        def update_slider(value):
            return value


    def parse_uploaded_image(self, contents):
        """
        Parse uploaded image content and return displayable component.

        Args:
            contents: Base64 encoded image content from dcc.Upload

        Returns:
            html.Img component with uploaded image
        """
        try:
            #display the uploaded image as-is
            return html.Img(
                src=contents,
                style={
                    "maxWidth": "100%",
                    "maxHeight": "100%",
                    "objectFit": "contain",
                }
            )
        except Exception as e:
            return html.Div(
                f'Error displaying image: {str(e)}',
                style={'color': 'red', 'padding': '20px'}
            )