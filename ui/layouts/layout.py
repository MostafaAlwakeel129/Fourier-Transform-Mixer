from dash import html, dcc

class Layout:
    """Layout class for the Dash application viewport."""

    def __init__(self):
        """Initialize ViewportLayout with dark-themed layout."""
        pass

    def build_input_card(self, card_id, text_color, card_style, display_item_style, upload_style):
        """
        Creates a single input card with two columns:
        - Left: Image display
        - Right: Component dropdown + FT display
        - Header: Includes Title and Weight Slider side-by-side
        """
        return html.Div([
            # Header with Title and Slider side-by-side
            html.Div([
                html.H3(f'Input {card_id}', style={
                    'margin': '0', 
                    'color': text_color, 
                    'whiteSpace': 'nowrap',
                    'marginRight': '15px'
                }),
                
                # Slider Container
                html.Div([
                    dcc.Slider(
                        id=f'weight-slider-{card_id}',
                        min=0, max=1, step=0.05,
                        value=0.0,
                        marks={0: '0', 1: '1'}, # Minimal marks to save space
                        tooltip={"placement": "bottom", "always_visible": False},
                    )
                ], style={'flex': '1', 'paddingTop': '8px'}) 
                
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'marginBottom': '12px',
                'width': '100%'
            }),
            
            # Two columns: Image and FT Display
            html.Div([
                # Left Column: Image Display Area

                html.Div([
                    # Upload area (small, fixed height)
                    dcc.Upload(
                        id=f'upload-image-{card_id}',
                        children=html.Div("Upload an image"),
                        multiple=False,
                        accept="image/*",
                        # style={'height': '40px', 'marginBottom': '2px'}
                        style=upload_style
                    ),

                    # Display area (flex 1, will show image)
                    html.Div(
                        id=f'image-display-{card_id}',
                        style={**display_item_style, 'flex': 1, 'minHeight': '200px', 'borderRadius': '8px', 'backgroundColor': '#0f0f0f'}
                    )
                ], style={'display': 'flex', 'flexDirection': 'column', 'flex': '1', 'height': '100%'}),

                # Right Column: Dropdown + FT Display Area
                html.Div([
                    # Component Selection Dropdown
                    html.Div([
                        dcc.Dropdown(
                            id=f'component-select-{card_id}',
                            options=[],  # Will be populated based on mode
                            value=None,
                            placeholder="Select component",
                            style={'width': '100%', 'color': 'black'}
                        )
                    ], style={'marginBottom': '8px'}),
                    
                    # FT Display
                    html.Div(
                        id=f'ft-display-{card_id}',
                        children=[
                            html.Img(
                                src="https://placehold.co/400x300/444444/888888?text=FT+Component",
                                style={'width': '100%', 'height': '100%', 'objectFit': 'contain'}
                            )
                        ],
                        style={**display_item_style, 'flex': '1'}
                    )
                ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'})

            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'flex': '1',
                'gap': '8px',
                'minHeight': 0
            })
        ], style={
            **card_style,
            'display': 'flex',
            'flexDirection': 'column',
            'overflow': 'hidden'   # ← ADDED
        })

    def build_settings_section(self, text_color):
        """
        Creates the settings section with:
        - Radio buttons for Viewport 1 and Viewport 2
        - Single mode dropdown for Magnitude/Phase or Real/Imaginary
        - ROI dropdown for Inner/Outer selection
        - Two output displays for viewport results
        - Mix button
        """
        
        output_display_style = {
            "borderRadius": "8px",
            "backgroundColor": "#0f0f0f",
            "overflow": "hidden",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "minHeight": "150px",
            "marginBottom": "12px",
            "border": "1px solid #404040"
        }
        
        mix_button_style = {
            "width": "100%",
            "padding": "12px",
            "fontSize": "16px",
            "fontWeight": "bold",
            "cursor": "pointer",
            "backgroundColor": "#4CAF50",
            "color": "white",
            "border": "none",
            "borderRadius": "8px",
            "transition": "background-color 0.3s, transform 0.1s",
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.3)"
        }
        
        return html.Div([
            # Viewport Radio Buttons
            html.Div([
                html.Label('Viewport:', style={
                    'color': text_color,
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'display': 'block'
                }),
                dcc.RadioItems(
                    id='viewport-select',
                    options=[
                        {'label': ' Viewport 1', 'value': 'viewport1'},
                        {'label': ' Viewport 2', 'value': 'viewport2'}
                    ],
                    value='viewport1',
                    inline=True,
                    style={'color': text_color},
                    labelStyle={'marginRight': '15px', 'display': 'inline-block'}
                )
            ], style={
                'marginBottom': '20px',
                'paddingBottom': '16px',
                'borderBottom': '1px solid #404040'
            }),
            
            # Mode Selection Dropdown
            html.Div([
                html.Label('FT Mode:', style={
                    'color': text_color,
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='ft-mode-select',
                    options=[
                        {'label': 'Magnitude and Phase', 'value': 'mag_phase'},
                        {'label': 'Real and Imaginary', 'value': 'real_imag'}
                    ],
                    value='mag_phase',
                    style={'width': '100%', 'color': 'black'}
                )
            ], style={
                'marginBottom': '20px',
                'paddingBottom': '16px',
                'borderBottom': '1px solid #404040'
            }),
            
            # ROI Selection Dropdown
            html.Div([
                html.Label('ROI Selection:', style={
                    'color': text_color,
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='roi-select',
                    options=[
                        {'label': 'Inner Region', 'value': 'inner'},
                        {'label': 'Outer Region', 'value': 'outer'}
                    ],
                    value='inner',
                    style={'width': '100%', 'color': 'black'}
                )
            ], style={
                'marginBottom': '20px',
                'paddingBottom': '16px',
                'borderBottom': '1px solid #404040'
            }),
            
            # Output Section
            html.Div([
                html.Label('Output:', style={
                    'color': text_color,
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'marginBottom': '12px',
                    'display': 'block'
                }),
                
                # Viewport 1 Output
                html.Div([
                    html.Div('Viewport 1', style={
                        'color': text_color,
                        'fontSize': '12px',
                        'marginBottom': '6px',
                        'fontWeight': 'bold'
                    }),
                    html.Div(
                        id='output-viewport1',
                        children=[
                            html.Div(
                                "Viewport 1 Output",
                                style={
                                    'color': '#666',
                                    'fontSize': '12px',
                                    'textAlign': 'center'
                                }
                            )
                        ],
                        style=output_display_style
                    )
                ], style={'marginBottom': '12px'}),
                
                # Viewport 2 Output
                html.Div([
                    html.Div('Viewport 2', style={
                        'color': text_color,
                        'fontSize': '12px',
                        'marginBottom': '6px',
                        'fontWeight': 'bold'
                    }),
                    html.Div(
                        id='output-viewport2',
                        children=[
                            html.Div(
                                "Viewport 2 Output",
                                style={
                                    'color': '#666',
                                    'fontSize': '12px',
                                    'textAlign': 'center'
                                }
                            )
                        ],
                        style=output_display_style
                    )
                ], style={'marginBottom': '16px'}),
                
                # Mix Button
                html.Button(
                    'Mix',
                    id='mix-button',
                    n_clicks=0,
                    style=mix_button_style
                )
            ])
        ])


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
            'overflowY': 'auto',
        }

        display_item_style = {
            "flex": 1,
            "borderRadius": "8px",
            "backgroundColor": "#0f0f0f",
            "overflow": "hidden",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "minHeight": "200px"
        }
        upload_style={
            "width": "100%",
            "padding": "6px",
            "fontSize": "12px",
            "cursor": "pointer",
            "backgroundColor": "#4CAF50",
            "color": "white",
            "borderRadius": "6px",
            "marginBottom": "8px",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center"
        }

        cards = []
        for card_id in range(1, 5):
            cards.append(
                self.build_input_card(
                    card_id,
                    text_color,
                    left_card_style,
                    display_item_style,
                    upload_style
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
                        html.H3('Settings', style={'margin': '0 0 20px 0', 'color': text_color}),
                        self.build_settings_section(text_color)
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
            }),
            
            # Hidden interval component for polling job progress
            dcc.Interval(
                id='interval-component',
                interval=1000,  # Update every 1 second (1000ms)
                n_intervals=0,
                disabled=False
            ),
            
            # Hidden store component to track job state
            dcc.Store(
                id='job-store',
                data={
                    'job_started': False,
                    'viewport': None,
                    'progress': 0.0
                }
            ),

            dcc.Store(
                id='bc-store',
                data={
                    str(i): {
                        'brightness': 0.0,
                        'contrast': 1.0,
                        'last_x': None,
                        'last_y': None
                    } for i in range(1, 5)
                }
            )
            
        ], style={
            'margin': '0',
            'padding': '0',
            'overflow': 'hidden',
            'height': '100vh',
            'width': '100vw',
        })