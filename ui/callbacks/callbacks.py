"""Callbacks class for callback handlers."""

from dash import Dash, Input, Output, html
import base64
import io
from PIL import Image


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

    def _register_callbacks(self) -> None:
        """Register all callbacks for the viewport."""

        # Image upload callbacks for each input
        for i in range(1, 5):
            @self.app.callback(
                Output(f'image-display-{i}', 'children'),
                [Input(f'upload-image-{i}', 'contents')],
                prevent_initial_call=True
            )
            def update_image_display(contents, card_num=i):
                if contents is not None:
                    return self.parse_uploaded_image(contents)
                return html.Div()

        # Slider callbacks for each input (placeholder for future use)
        for i in range(1, 5):
            @self.app.callback(
                Output(f'weight-slider-{i}', 'value'),
                [Input(f'weight-slider-{i}', 'value')],
                prevent_initial_call=True
            )
            def update_slider_value(value, card_num=i):
                # Placeholder - just return the value for now
                # Future logic can be added here
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
            # Simply display the uploaded image as-is
            return html.Img(
                src=contents,
                style={
                    'width': '100%',
                    'height': '100%',
                    'objectFit': 'contain',
                    'position': 'absolute',
                    'top': '0',
                    'left': '0'
                }
            )

        except Exception as e:
            return html.Div(
                f'Error displaying image: {str(e)}',
                style={'color': 'red', 'padding': '20px'}
            )