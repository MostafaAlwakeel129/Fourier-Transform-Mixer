from dash import Dash, Input, Output, State, html, dcc, callback_context, no_update, ALL
import plotly.graph_objs as go
from controllers.controller import Controller
import numpy as np

# Global controller instance that gets reset on page load
_controller_instance = None

def get_controller():
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = Controller()
    return _controller_instance

def reset_controller():
    global _controller_instance
    _controller_instance = Controller()
    return _controller_instance

class Callbacks:
    """Callback class for handling Dash app callbacks."""

    def __init__(self, app: Dash):
        """
        Initialize ViewportCallbacks with Dash app instance.

        Args:
            app: Dash application instance
        """
        self.app = app
        self.controller = get_controller()
        self._register_callbacks()

    def _register_callbacks(self):

        # Clear session on page load by detecting URL changes
        @self.app.callback(
            Output('upload-image-1', 'contents', allow_duplicate=True),
            Input('upload-image-1', 'id'),
            prevent_initial_call='initial_duplicate'
        )
        def clear_on_page_load(upload_id):
            # Reset controller when page loads
            self.controller = reset_controller()
            return None

        # -------- IMAGE UPLOAD CALLBACKS -------- #
        for i in range(1, 5):
            self._create_image_callback(i)

        # -------- COMPONENT SELECT CALLBACKS -------- #
        for i in range(1, 5):
            self._create_component_select_callback(i)

        # -------- FT MODE CALLBACK -------- #
        self._create_ft_mode_callback()

        # -------- Mix image callbacks -------#
        self._create_mix_image()


    def _create_image_callback(self, card_id):
        """
        Handle image upload using controller.handle_upload() and display results.
        Reads ft_mode and current component selection directly from inputs.
        """
        @self.app.callback(
            [
                Output(f'image-display-{card_id}', 'children'),
                Output(f'ft-display-{card_id}', 'children'),
                Output(f'component-select-{card_id}', 'value', allow_duplicate=True)
            ],
            Input(f'upload-image-{card_id}', 'contents'),
            [
                State('ft-mode-select', 'value'),
                State(f'component-select-{card_id}', 'value')
            ],
            prevent_initial_call=True
        )
        def update_image_and_ft(contents, ft_mode, current_component):
            if not contents:
                return html.Div(), html.Div(), None
            
            # Default FT mode if None
            if ft_mode is None:
                ft_mode = 'mag_phase'
            
            # Default component based on mode
            if ft_mode == 'mag_phase':
                default_component = 'magnitude'
            else:  # real_imag
                default_component = 'real'
            
            # Use current component if selected, otherwise use default
            ft_component = current_component if current_component else default_component
            
            # Use controller.handle_upload (card_id is 1-4, but controller expects 0-3)
            result = self.controller.handle_upload(contents, card_id - 1, ft_component)
            
            if result['status'] == 'error':
                error_div = html.Div(
                    f"Error: {result['message']}",
                    style={'color': 'red', 'padding': '20px'}
                )
                return error_div, error_div, ft_component
            
            # Get data directly from handle_upload result
            raw_image_data = np.array(result['raw_image_data'])
            ft_component_data = np.array(result['ft_component_data'])
            
            # Create displays using the data from handle_upload
            raw_fig = go.Figure(data=go.Heatmap(
                z=raw_image_data,
                colorscale='gray',
                showscale=False,
                hoverinfo='skip'
            ))
            raw_fig.update_layout(
                xaxis={'visible': False, 'showgrid': False, 'fixedrange': True},
                yaxis={'visible': False, 'showgrid': False, 'autorange': 'reversed', 'fixedrange': True},
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='#0f0f0f',
                plot_bgcolor='#0f0f0f',
                autosize=True,
                dragmode=False
            )
            raw_fig.update_yaxes(scaleanchor="x", scaleratio=1)
            
            ft_fig = go.Figure(data=go.Heatmap(
                z=ft_component_data,
                colorscale='gray',
                showscale=False,
                hoverinfo='skip'
            ))
            ft_fig.update_layout(
                xaxis={'visible': False, 'showgrid': False},
                yaxis={'visible': False, 'showgrid': False, 'autorange': 'reversed'},
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='#0f0f0f',
                plot_bgcolor='#0f0f0f',
                dragmode='drawrect',
                newshape=dict(line_color='cyan'),
                autosize=True
            )
            ft_fig.update_yaxes(scaleanchor="x", scaleratio=1)
            
            raw_display = html.Div([
                dcc.Graph(
                    id=f'raw-graph-{card_id}',
                    figure=raw_fig,
                    config={'displayModeBar': False},
                    style={'height': '100%', 'width': '100%'},
                )
            ], style={'height': '100%', 'width': '100%'})
            
            ft_display = html.Div([
                dcc.Graph(
                    id={'type': 'ft-graph', 'card_id': card_id},
                    figure=ft_fig,
                    config={'displayModeBar': False},
                    style={'height': '100%', 'width': '100%'}
                )
            ], style={'height': '100%', 'width': '100%'})
            
            return raw_display, ft_display, ft_component


    def _create_component_select_callback(self, card_id):
        """
        Handle component selection changes and update FT display.
        Uses controller.get_plotting_data() for fast retrieval without re-uploading.
        """
        @self.app.callback(
            Output(f'ft-display-{card_id}', 'children', allow_duplicate=True),
            Input(f'component-select-{card_id}', 'value'),
            prevent_initial_call=True
        )
        def update_ft_display(selected_component):
            if not selected_component:
                return html.Div()
            
            # Use controller.get_plotting_data() instead of handle_upload()
            # This is much faster as it retrieves cached data
            ft_component_data = self.controller.get_plotting_data(
                index=card_id - 1,  # Convert 1-4 to 0-3
                mode=selected_component
            )
            
            if ft_component_data is None:
                return html.Div(
                    "Upload an image first",
                    style={'color': '#888', 'textAlign': 'center', 'padding': '20px'}
                )
            
            # Create display with the retrieved data
            ft_fig = go.Figure(data=go.Heatmap(
                z=ft_component_data,
                colorscale='gray',
                showscale=False,
                hoverinfo='skip'
            ))
            ft_fig.update_layout(
                xaxis={'visible': False, 'showgrid': False},
                yaxis={'visible': False, 'showgrid': False, 'autorange': 'reversed'},
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='#0f0f0f',
                plot_bgcolor='#0f0f0f',
                dragmode='drawrect',
                newshape=dict(line_color='cyan'),
                autosize=True
            )
            ft_fig.update_yaxes(scaleanchor="x", scaleratio=1)
            
            return html.Div([
                dcc.Graph(
                    id={'type': 'ft-graph', 'card_id': card_id},
                    figure=ft_fig,
                    config={'displayModeBar': False},
                    style={'height': '100%', 'width': '100%'}
                )
            ], style={'height': '100%', 'width': '100%'})


    def _create_ft_mode_callback(self):
        """
        Update all component dropdowns based on FT mode selection.
        Reads current values of component dropdowns to see if they need adjustment.
        """
        @self.app.callback(
            [Output(f'component-select-{i}', 'options') for i in range(1, 5)] +
            [Output(f'component-select-{i}', 'value') for i in range(1, 5)],
            Input('ft-mode-select', 'value'),
            [State(f'component-select-{i}', 'value') for i in range(1, 5)],
            prevent_initial_call=False
        )
        def update_component_dropdowns_and_values(mode, *current_values):
            
            # Set options based on mode
            if mode == 'mag_phase':
                options = [
                    {'label': 'Magnitude', 'value': 'magnitude'},
                    {'label': 'Phase', 'value': 'phase'}
                ]
                default_value = 'magnitude'
            else:  # real_imag
                options = [
                    {'label': 'Real', 'value': 'real'},
                    {'label': 'Imaginary', 'value': 'imag'}
                ]
                default_value = 'real'
            
            # Check current values against the new mode
            new_values = []
            valid_components = ['magnitude', 'phase'] if mode == 'mag_phase' else ['real', 'imag']
            
            for val in current_values:
                if val and val in valid_components:
                    new_values.append(val)
                else:
                    new_values.append(default_value)
            
            # Return options (4 times) and values (4 times)
            return (options, options, options, options, 
                    new_values[0], new_values[1], new_values[2], new_values[3])


    def _create_mix_image(self):
        """
        Create callback for the Mix button that processes inputs based on selected viewport.
        Uses an interval to poll for job completion.
        """
        @self.app.callback(
            [
                Output('output-viewport1', 'children'),
                Output('output-viewport2', 'children'),
                Output('job-store', 'data', allow_duplicate=True)
            ],
            Input('mix-button', 'n_clicks'),
            [
                State('viewport-select', 'value'),
                State('weight-slider-1', 'value'),
                State('weight-slider-2', 'value'),
                State('weight-slider-3', 'value'),
                State('weight-slider-4', 'value'),
                State('ft-mode-select', 'value'),
                State('component-select-1', 'value'),
                State('component-select-2', 'value'),
                State('component-select-3', 'value'),
                State('component-select-4', 'value'),
                State('roi-select', 'value'),
                State('job-store', 'data')
            ],
            prevent_initial_call=True
        )
        def start_mix_job(n_clicks, viewport, weight1, weight2, weight3, weight4, 
                        ft_mode, comp1, comp2, comp3, comp4, roi_select, job_store):
            """
            Start the mixing job and store the state.
            """
            if n_clicks == 0:
                return no_update, no_update, no_update
            
            print(f"Starting mix job for {viewport}")
            
            # First, update all sliders in the controller
            # Determine component groups based on FT mode
            if ft_mode == 'mag_phase':
                comp1_group = 'comp1' if comp1 == 'magnitude' else 'comp2'
                comp2_group = 'comp1' if comp2 == 'magnitude' else 'comp2'
                comp3_group = 'comp1' if comp3 == 'magnitude' else 'comp2'
                comp4_group = 'comp1' if comp4 == 'magnitude' else 'comp2'
            else:  # real_imag
                comp1_group = 'comp1' if comp1 == 'real' else 'comp2'
                comp2_group = 'comp1' if comp2 == 'real' else 'comp2'
                comp3_group = 'comp1' if comp3 == 'real' else 'comp2'
                comp4_group = 'comp1' if comp4 == 'real' else 'comp2'
            
            # Update slider values in controller
            self.controller.handle_slider_update(weight1 or 0.25, 0, comp1_group)
            self.controller.handle_slider_update(weight2 or 0.25, 1, comp2_group)
            self.controller.handle_slider_update(weight3 or 0.25, 2, comp3_group)
            self.controller.handle_slider_update(weight4 or 0.25, 3, comp4_group)
            
            # Trigger the mixing button update
            self.controller.mix_button_update()
            
            # Create a processing message
            processing_msg = html.Div([
                html.Div("Processing...", style={
                    'color': '#888',
                    'textAlign': 'center',
                    'padding': '20px',
                    'fontSize': '14px'
                })
            ])
            
            # Update job store to indicate job started
            job_store['job_started'] = True
            job_store['viewport'] = viewport
            
            # Return processing message and updated job store
            if viewport == 'viewport1':
                return processing_msg, no_update, job_store
            else:
                return no_update, processing_msg, job_store
        
        # Create interval callback to check job progress
        @self.app.callback(
            [
                Output('output-viewport1', 'children', allow_duplicate=True),
                Output('output-viewport2', 'children', allow_duplicate=True),
                Output('job-store', 'data', allow_duplicate=True)
            ],
            Input('interval-component', 'n_intervals'),
            State('job-store', 'data'),
            prevent_initial_call=True
        )
        def check_job_progress(n_intervals, job_store):
            """
            Check job progress periodically and update when complete.
            """
            # If no job is running, do nothing
            if not job_store.get('job_started', False):
                return no_update, no_update, no_update
            
            # Check if job is still processing
            if self.controller.is_processing():
                # Get current progress
                progress = self.controller.get_job_progress()
                
                # Create progress message
                progress_msg = html.Div([
                    html.Div(f"Processing... {progress*100:.1f}%", style={
                        'color': '#4CAF50',
                        'textAlign': 'center',
                        'padding': '20px',
                        'fontSize': '14px',
                        'fontWeight': 'bold'
                    })
                ])
                
                viewport = job_store.get('viewport', 'viewport1')
                if viewport == 'viewport1':
                    return progress_msg, no_update, job_store
                else:
                    return no_update, progress_msg, job_store
            
            # Job is no longer processing, check result
            result = self.controller.get_job_result()
            viewport = job_store.get('viewport', 'viewport1')
            
            # Reset job store
            job_store['job_started'] = False
            job_store['viewport'] = None
            
            if result is None:
                # Error or no result
                error_div = html.Div([
                    html.Div("Error: No mixed result available", style={
                        'color': 'red',
                        'textAlign': 'center',
                        'padding': '20px',
                        'fontSize': '14px'
                    })
                ])
                
                if viewport == 'viewport1':
                    return error_div, no_update, job_store
                else:
                    return no_update, error_div, job_store
            
            # Create display for the mixed image
            try:
                # Convert to numpy array if needed
                if isinstance(result, np.ndarray):
                    mixed_data = result
                elif isinstance(result, list):
                    mixed_data = np.array(result)
                else:
                    mixed_data = result
                
                mixed_fig = go.Figure(data=go.Heatmap(
                    z=mixed_data,
                    colorscale='gray',
                    showscale=False,
                    hoverinfo='skip'
                ))
                mixed_fig.update_layout(
                    xaxis={'visible': False, 'showgrid': False},
                    yaxis={'visible': False, 'showgrid': False, 'autorange': 'reversed'},
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor='#0f0f0f',
                    plot_bgcolor='#0f0f0f',
                    autosize=True
                )
                mixed_fig.update_yaxes(scaleanchor="x", scaleratio=1)
                
                mixed_display = html.Div([
                    dcc.Graph(
                        figure=mixed_fig,
                        config={'displayModeBar': False},
                        style={'height': '100%', 'width': '100%'}
                    )
                ], style={'height': '100%', 'width': '100%'})
                
                if viewport == 'viewport1':
                    return mixed_display, no_update, job_store
                else:
                    return no_update, mixed_display, job_store
                
            except Exception as e:
                error_div = html.Div([
                    html.Div(f"Display error: {str(e)}", style={
                        'color': 'red',
                        'textAlign': 'center',
                        'padding': '20px',
                        'fontSize': '14px'
                    })
                ])
                
                if viewport == 'viewport1':
                    return error_div, no_update, job_store
                else:
                    return no_update, error_div, job_store