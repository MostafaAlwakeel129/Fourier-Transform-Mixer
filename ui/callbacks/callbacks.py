from dash import Dash, Input, Output, State, html, dcc, callback_context, no_update, ALL, MATCH
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

        # -------- Mix image callback -------#
        self._create_mix_callback()

        # -------- Progress bar callback -------#
        self._create_progress_callback()

        #_________Rect update callback -------#
        self._rect_update_callback()


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


    def _create_mix_callback(self):
        """
        Callback for the Mix button - handles only the mixing operation.
        Starts the job and updates the job store.
        """
        @self.app.callback(
            Output('job-store', 'data'),
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
            Start the mixing job and update job store.
            """
            if n_clicks == 0:
                return no_update
            
            print(f"Starting mix job for {viewport}")
            
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
            self.controller.handle_slider_update(weight1 or 0.0, 0, comp1_group)
            self.controller.handle_slider_update(weight2 or 0.0, 1, comp2_group)
            self.controller.handle_slider_update(weight3 or 0.0, 2, comp3_group)
            self.controller.handle_slider_update(weight4 or 0.0, 3, comp4_group)
            
            # Trigger the mixing button update
            self.controller.mix_button_update()
            
            # Update job store to indicate job started
            job_store['job_started'] = True
            job_store['viewport'] = viewport
            
            return job_store


    def _create_progress_callback(self):
        """
        Callback for progress bar - handles polling for job progress and completion.
        Updates progress bar, progress text, and viewport outputs.
        """
        @self.app.callback(
            [
                Output('output-viewport1', 'children'),
                Output('output-viewport2', 'children'),
                Output('progress-bar', 'style'),
                Output('progress-text', 'children'),
                Output('job-store', 'data', allow_duplicate=True)
            ],
            Input('interval-component', 'n_intervals'),
            State('job-store', 'data'),
            prevent_initial_call=True
        )
        def update_progress(n_intervals, job_store):
            """
            Check job progress periodically and update progress bar and outputs.
            """
            # If no job is running, return ready state
            if not job_store.get('job_started', False):
                progress_style = {
                    'width': '0%',
                    'height': '100%',
                    'backgroundColor': '#4CAF50',
                    'borderRadius': '4px',
                    'transition': 'width 0.3s ease'
                }
                return no_update, no_update, progress_style, "Ready", no_update
            
            # Check if job is still processing
            if self.controller.is_processing():
                # Get current progress
                progress = self.controller.get_job_progress()
                
                # Round progress to nearest 10% increment for smoother visual updates
                progress_percent = int(progress * 100)
                display_percent = (progress_percent // 10) * 10  # Round down to nearest 10
                
                # Update progress bar
                progress_style = {
                    'width': f'{display_percent}%',
                    'height': '100%',
                    'backgroundColor': '#4CAF50',
                    'borderRadius': '4px',
                    'transition': 'width 0.3s ease'
                }
                
                return no_update, no_update, progress_style, f"Processing... {display_percent}%", no_update
            
            # Job is complete - get result
            result = self.controller.get_job_result()
            viewport = job_store.get('viewport', 'viewport1')
            
            # Reset job store
            job_store['job_started'] = False
            job_store['viewport'] = None
            
            # Set progress bar to 100% when complete
            progress_style = {
                'width': '100%',
                'height': '100%',
                'backgroundColor': '#4CAF50',
                'borderRadius': '4px',
                'transition': 'width 0.3s ease'
            }
            
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
                    return error_div, no_update, progress_style, "Error", job_store
                else:
                    return no_update, error_div, progress_style, "Error", job_store
            
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
                
                # Show 100% complete
                if viewport == 'viewport1':
                    return mixed_display, no_update, progress_style, "Complete - 100%", job_store
                else:
                    return no_update, mixed_display, progress_style, "Complete - 100%", job_store
                
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
                    return error_div, no_update, progress_style, "Error", job_store
                else:
                    return no_update, error_div, progress_style, "Error", job_store


    def _rect_update_callback(self):
        @self.app.callback(
            Output({'type': 'ft-graph', 'card_id': MATCH}, 'figure'),
            Input({'type': 'ft-graph', 'card_id': MATCH}, 'relayoutData'),
            Input('roi-select', 'value'),
            State({'type': 'ft-graph', 'card_id': MATCH}, 'figure'),
            prevent_initial_call=True
            )
        def remove_old_rect(relayoutData, roi_select, fig):
            if not relayoutData:
                return no_update

            if 'shapes' not in relayoutData:
                return no_update

            new_rect = relayoutData['shapes'][-1]
            fig['layout']['shapes'] = [new_rect]
            
            if roi_select == 'inner':
                is_inner = True
            else:
                is_inner = False
            x0, y0 = int(new_rect['x0']), int(new_rect['y0'])
            x1, y1 = int(new_rect['x1']), int(new_rect['y1'])
            self.controller.apply_region_mask((x0,y0,x1,y1),is_inner)

            return fig

