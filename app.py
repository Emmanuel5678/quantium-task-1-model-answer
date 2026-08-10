import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Load and prepare data
def load_and_prepare_data():
    df = pd.read_csv('data/formatted_data.csv')
    
    # Fixed: Use raw string for regex (r'...') or double backslash
    df['sales'] = df['sales'].replace(r'[\$,]', '', regex=True).astype(float)
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    return df

df = load_and_prepare_data()

# Initialize app
app = dash.Dash(__name__)
app.title = "Soul Foods - Pink Morsel Sales Analysis"

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1(
            "🍬 Pink Morsel Sales Performance Dashboard",
            style={'color': '#ff6b81', 'marginBottom': '5px'}
        ),
        html.H3(
            "Soul Foods - Sales Analysis",
            style={'color': '#2c3e50', 'fontWeight': 'normal'}
        ),
        html.Hr(style={'borderColor': '#ff6b81'})
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fafafa'}),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("Select Region:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='region-dropdown',
                options=[
                    {'label': '🌍 All Regions', 'value': 'All'},
                    {'label': '⬆️ East', 'value': 'east'},
                    {'label': '⬇️ South', 'value': 'south'},
                    {'label': '⬅️ West', 'value': 'west'},
                    {'label': '➡️ North', 'value': 'north'}
                ],
                value='All',
                style={'width': '250px', 'marginTop': '5px'}
            ),
        ], style={'display': 'inline-block', 'marginRight': '30px'}),
        
        html.Div([
            html.Label("Show Price Increase Line:", style={'fontWeight': 'bold'}),
            dcc.Checklist(
                id='show-line-toggle',
                options=[{'label': ' Show', 'value': 'show'}],
                value=['show'],
                style={'marginTop': '5px'}
            )
        ], style={'display': 'inline-block'})
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    # Chart
    dcc.Graph(id='sales-chart', style={'height': '500px'}),
    
    # Stats
    html.Div(id='stats-container', style={
        'padding': '20px',
        'margin': '20px auto',
        'maxWidth': '900px',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    })
])

@app.callback(
    [Output('sales-chart', 'figure'),
     Output('stats-container', 'children')],
    [Input('region-dropdown', 'value'),
     Input('show-line-toggle', 'value')]
)
def update_dashboard(selected_region, show_line):
    # Filter data
    if selected_region == 'All':
        filtered_df = df
        region_label = "All Regions"
    else:
        filtered_df = df[df['region'] == selected_region]
        region_label = f"{selected_region.capitalize()} Region"
    
    # Create figure
    fig = go.Figure()
    
    # Add sales line
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['sales'],
        mode='lines+markers',
        name='Sales',
        line=dict(color='#ff6b81', width=3),
        marker=dict(size=6, color='#ff6b81'),
        hovertemplate='Date: %{x}<br>Sales: $%{y:,.2f}<extra></extra>'
    ))
    
    # Add price increase line if toggled
    if 'show' in show_line:
        fig.add_vline(
            x=pd.Timestamp('2021-01-15'),
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="📈 Price Increase",
            annotation_position="top"
        )
        
        # Add shaded regions
        fig.add_vrect(
            x0=filtered_df['date'].min(),
            x1=pd.Timestamp('2021-01-15'),
            fillcolor="rgba(231, 76, 60, 0.1)",
            layer="below",
            line_width=0,
            annotation_text="Before",
            annotation_position="top left"
        )
        fig.add_vrect(
            x0=pd.Timestamp('2021-01-15'),
            x1=filtered_df['date'].max(),
            fillcolor="rgba(46, 204, 113, 0.1)",
            layer="below",
            line_width=0,
            annotation_text="After",
            annotation_position="top right"
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Pink Morsel Daily Sales - {region_label}',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        xaxis_title={
            'text': 'Date',
            'font': {'size': 14, 'color': '#2c3e50'}
        },
        yaxis_title={
            'text': 'Sales ($)',
            'font': {'size': 14, 'color': '#2c3e50'}
        },
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(255,255,255,0.9)'
    )
    
    # Calculate statistics
    price_increase_date = pd.Timestamp('2021-01-15')
    before_data = filtered_df[filtered_df['date'] < price_increase_date]
    after_data = filtered_df[filtered_df['date'] >= price_increase_date]
    
    if not before_data.empty and not after_data.empty:
        avg_before = before_data['sales'].mean()
        avg_after = after_data['sales'].mean()
        pct_change = ((avg_after - avg_before) / avg_before) * 100
        total_sales = filtered_df['sales'].sum()
        
        stats = html.Div([
            html.H4("📊 Sales Statistics", style={'textAlign': 'center', 'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("Before Price Increase", style={'color': '#e74c3c'}),
                        html.P(f"${avg_before:,.2f}", style={'fontSize': '24px', 'fontWeight': 'bold'}),
                        html.P("Average daily sales", style={'color': '#7f8c8d'})
                    ], style={'display': 'inline-block', 'width': '30%', 'padding': '10px'}),
                    
                    html.Div([
                        html.H5("After Price Increase", style={'color': '#27ae60'}),
                        html.P(f"${avg_after:,.2f}", style={'fontSize': '24px', 'fontWeight': 'bold'}),
                        html.P("Average daily sales", style={'color': '#7f8c8d'})
                    ], style={'display': 'inline-block', 'width': '30%', 'padding': '10px'}),
                    
                    html.Div([
                        html.H5("Change", style={'color': '#2c3e50'}),
                        html.P(
                            f"{pct_change:+.1f}%",
                            style={
                                'fontSize': '24px',
                                'fontWeight': 'bold',
                                'color': '#27ae60' if pct_change > 0 else '#e74c3c'
                            }
                        ),
                        html.P(
                            f"Total sales: ${total_sales:,.2f}",
                            style={'color': '#7f8c8d'}
                        )
                    ], style={'display': 'inline-block', 'width': '30%', 'padding': '10px'})
                ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
            ]),
            
            html.Div([
                html.Div([
                    html.Strong("📌 Conclusion: "),
                    html.Span(
                        f"Sales {'increased' if pct_change > 0 else 'decreased'} by {abs(pct_change):.1f}% after the price increase on January 15, 2021.",
                        style={
                            'color': '#27ae60' if pct_change > 0 else '#e74c3c',
                            'fontSize': '18px',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={'textAlign': 'center', 'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#fff', 'borderRadius': '5px'})
            ])
        ])
    else:
        stats = html.Div("Not enough data for comparison")
    
    return fig, stats

# Fixed: Changed app.run_server to app.run
if __name__ == '__main__':
    app.run(debug=True, port=8050)