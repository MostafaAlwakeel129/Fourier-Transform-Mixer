


from dash import html, dcc
import base64
import io
from PIL import Image
import numpy as np

class Layout:
    """Layout class for the Dash application viewport."""

    def __init__(self):
        """Initialize ViewportLayout with dark-themed layout."""
        pass

    def build_input_card(self, card_id, text_color, card_style, controls_row_style,
                         control_item_style, display_item_style, upload_style, displays_row_style):
        """
        Creates a single input card (Input 1–4) that contains a weight slider,
        FT component dropdown, image upload area, and Fourier Transform display.
        The card_id is used to generate unique component IDs for Dash callbacks.
        """
        return html.Div([
            html.H3(f'Input {card_id}', style={'margin': '0 0 16px 0', 'color': text_color}),

            # Controls row
            html.Div([
                html.Div([
                    html.Label('Weight:', style={'color': text_color, 'fontSize': '12px', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id=f'weight-slider-{card_id}',
                        min=0,
                        max=1,
                        step=0.05,
                        value=0.25,
                        marks={0: '0', 0.5: '0.5', 1: '1'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style=control_item_style),

                html.Div([
                    html.Label('FT Component:', style={'color': text_color, 'fontSize': '12px', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id=f'ft-component-select-{card_id}',
                        options=[
                            {'label': 'Magnitude', 'value': 'magnitude'},
                            {'label': 'Phase', 'value': 'phase'},
                            {'label': 'Real', 'value': 'real'},
                            {'label': 'Imaginary', 'value': 'imaginary'}
                        ],
                        value='magnitude',
                        style={'width': '100%', 'color': 'black'}
                    )
                ], style=control_item_style),

            ], style=controls_row_style),

            # Displays row
            html.Div([
                html.Div([
                    dcc.Upload(
                        id=f'upload-image-{card_id}',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files', style={'color': '#007bff'})
                        ], style={'color': text_color}),
                        style=upload_style,
                        multiple=False,
                        accept='image/*'
                    ),
                    html.Div(id=f'image-display-{card_id}',
                             style={'position': 'absolute', 'top': '0', 'left': '0',
                                    'width': '100%', 'height': '100%'})
                ], style=display_item_style),

                html.Div([
                    html.Div(
                        id=f'ft-display-{card_id}',
                        children=[
                            html.Img(
                                src="https://placehold.co/300x200/444444/888888?text=FT+Component",
                                style={'width': '100%', 'height': '100%', 'objectFit': 'contain'}
                            )
                        ],
                        style={'width': '100%', 'height': '100%'}
                    )
                ], style=display_item_style),

            ], style=displays_row_style),

        ], style=card_style)


    def get_layout(self) -> html.Div:
        """
        Get the complete layout with dark theme and floating cards.

        Returns:
            HTML Div containing the main page layout
        """
        # Dark theme colors
        dark_bg = '#1a1a1a'
        card_bg = '#2d2d2d'
        card_border = '#404040'
        text_color = '#e0e0e0'

        # Card style
        card_style = {
            'backgroundColor': card_bg,
            'border': f'1px solid {card_border}',
            'borderRadius': '12px',
            'padding': '16px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.3)',
            'color': text_color,
            'margin': '8px',
        }

        # Left side container (75% width)
        left_container_style = {
            'width': '75%',
            'float': 'left',
            'display': 'flex',
            'flexDirection': 'column',
            'boxSizing': 'border-box',
        }

        # Right side container (25% width)
        right_container_style = {
            'width': '25%',
            'float': 'right',
            'display': 'flex',
            'flexDirection': 'column',
            'boxSizing': 'border-box',
        }

        # Row style for cards
        row_style = {
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
        }

        # Card height calculations (same as original)
        card_height = 'calc((100vh - 52px) / 2)'
        card_margin = '8px'
        right_card_height = 'calc(100vh - 36px)'

        # Left card style with flex column layout
        left_card_style = {
            **card_style,
            'flex': '1',
            'height': card_height,
            'display': 'flex',
            'flexDirection': 'column',
        }

        # Right card style
        right_card_style = {
            **card_style,
            'height': right_card_height,
            'marginTop': card_margin,
            'marginBottom': card_margin,
        }

        # Controls row style (slider and dropdown)
        controls_row_style = {
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
            'height': '80px',  # Increased height for slider
            'marginBottom': '10px',
        }

        # Displays row style (image and FT component)
        displays_row_style = {
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
            'flex': '1',  # Take remaining space
        }

        # Individual control/display styles
        control_item_style = {
            'flex': '1',
            'margin': '0 5px',
        }

        display_item_style = {
            'flex': '1',
            'margin': '0 5px',
            'border': f'1px solid {card_border}',
            'borderRadius': '8px',
            'backgroundColor': '#1a1a1a',
            'position': 'relative',
        }

        # Upload style
        upload_style = {
            'width': '100%',
            'height': '100%',
            'lineHeight': '100px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderColor': card_border,
            'borderRadius': '8px',
            'textAlign': 'center',
            'margin': '0',
            'backgroundColor': '#0f0f0f',
            'cursor': 'pointer',
            'position': 'relative',
        }

        cards = []
        for card_id in range(1, 5):
            cards.append(
                self.build_input_card(
                    card_id,
                    text_color,
                    left_card_style,
                    controls_row_style,
                    control_item_style,
                    display_item_style,
                    upload_style,
                    displays_row_style
                )
            )


        return html.Div([
            # Main container with dark background
            html.Div([
                # Left portion (75% width) - 4 cards in 2x2 grid
                html.Div([
                    html.Div(cards[:2], style=row_style),  # first row
                    html.Div(cards[2:], style=row_style)   # second row
                ], style=left_container_style),

                # Right portion (25% width) - 1 tall card
                html.Div([
                    html.Div([
                        html.H3('Mixer Output', style={'margin': '0 0 16px 0', 'color': text_color}),
                        html.P('Output display and controls will be here', style={'color': text_color, 'opacity': '0.8'})
                    ], style=right_card_style),
                ], style=right_container_style),

                # Clear float
                html.Div(style={'clear': 'both'})
            ], style={
                'backgroundColor': dark_bg,
                'height': '100vh',
                'width': '100vw',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif',
                'overflow': 'hidden',
                'boxSizing': 'border-box',
                'margin': '0',
                'position': 'fixed',
                'top': '0',
                'left': '0',
            })
        ], style={
            'margin': '0',
            'padding': '0',
            'overflow': 'hidden',
            'height': '100vh',
            'width': '100vw',
        })