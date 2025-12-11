from dash import html, dcc

class Layout:
    """Layout class for the Dash application viewport."""

    def __init__(self):
        """Initialize ViewportLayout with dark-themed layout."""
        pass

    def build_input_card(self, card_id, text_color, card_style,
                         display_item_style, upload_style, displays_row_style):
        """
        Creates a single input card (Input 1–4) with the structure:
        """
        return html.Div([
            # first row: HEADER and SLIDER
            html.Div([
                # Header on the left
                html.Div(
                    html.H3(f'Input {card_id}', style={'margin': 0, 'color': text_color}),
                    style={
                        'flex': '0 0 auto',
                        'marginRight': '12px',
                        'display': 'flex',
                        'alignItems': 'center'
                    }
                ),
                # Slider aligned right
                html.Div(
                    dcc.Slider(
                        id=f'weight-slider-{card_id}',
                        min=0, max=1, step=0.05,
                        value=0.25,
                        marks={0: '0', 0.5: '0.5', 1: '1'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    style={
                        'flex': '0 0 45%',   # <<< slider width reduced (change % if needed)
                        'marginLeft': 'auto'  # pushes slider to the far right
                    }
                ),
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'marginBottom': '14px'
            }),
            # second row: UPLOAD and DROPDOWN
            html.Div([
                # Upload Button
                html.Div([
                    dcc.Upload(
                        id=f'upload-image-{card_id}',
                        children=html.Button(
                            "Upload Image",
                            style=upload_style
                        ),
                        multiple=False,
                        accept="image/*",
                        style={"marginBottom": "6px"}
                    )
                ], style={'flex': 1, 'marginRight': '6px'}),

                # FT Component Dropdown
                html.Div([
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
                ], style={'flex': 1})

            ], style={'display': 'flex', 'flexDirection': 'row', 'marginBottom': '12px'}),

            # third row: IMAGE and FT DISPLAY
            html.Div([
                # Image Display Area
                html.Div(
                    id=f'image-display-{card_id}',
                    children=[],  # empty initially
                    style=display_item_style
                ),

                # FT Display Area
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
                ], style=display_item_style)

            ], style=displays_row_style)

        ], style=card_style)


    def get_layout(self) -> html.Div:
        """Get the full page layout (dark theme)."""

        # Dark theme
        dark_bg = '#1a1a1a'
        card_bg = '#2d2d2d'
        card_border = '#404040'
        text_color = '#e0e0e0'

        # Card styling
        card_style = {
            'backgroundColor': card_bg,
            'border': f'1px solid {card_border}',
            'borderRadius': '12px',
            'padding': '16px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.3)',
            'color': text_color,
            'margin': '8px',
        }

        left_container_style = {
            'width': '75%',
            'float': 'left',
            'display': 'flex',
            'flexDirection': 'column',
            'boxSizing': 'border-box',
        }

        right_container_style = {
            'width': '25%',
            'float': 'right',
            'display': 'flex',
            'flexDirection': 'column',
            'boxSizing': 'border-box',
        }

        row_style = {
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
        }

        card_height = 'calc((100vh - 52px) / 2)'
        card_margin = '8px'
        right_card_height = 'calc(100vh - 36px)'

        left_card_style = {
            **card_style,
            'flex': '1',
            'height': card_height,
            'display': 'flex',
            'flexDirection': 'column',
        }

        right_card_style = {
            **card_style,
            'height': right_card_height,
            'marginTop': card_margin,
            'marginBottom': card_margin,
        }

        displays_row_style = {
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
            'flex': '1',
        }

        display_item_style = {
            "flex": 1,
            "borderRadius": "8px",
            "backgroundColor": "#0f0f0f",  # dark bg
            "overflow": "hidden",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "marginRight": "6px"
        }

        upload_style={
            "width": "100%",
            "padding": "6px",
            "fontSize": "12px",
            "cursor": "pointer",
            "backgroundColor": "#333",
            "color": "white",
            "borderRadius": "6px",
        }

        cards = []
        for card_id in range(1, 5):
            cards.append(
                self.build_input_card(
                    card_id,
                    text_color,
                    left_card_style,
                    display_item_style,
                    upload_style,
                    displays_row_style
                )
            )

        return html.Div([
            html.Div([
                html.Div([
                    html.Div(cards[:2], style=row_style),
                    html.Div(cards[2:], style=row_style)
                ], style=left_container_style),

                html.Div([
                    html.Div([
                        html.H3('Mixer Output', style={'margin': '0 0 16px 0', 'color': text_color}),
                        html.P('Output display and controls will be here', style={'color': text_color, 'opacity': '0.8'})
                    ], style=right_card_style),
                ], style=right_container_style),

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
