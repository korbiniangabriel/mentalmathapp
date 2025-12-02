"""Visualization functions using Plotly."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def create_accuracy_trend_chart(data: pd.DataFrame) -> go.Figure:
    """Create line chart showing accuracy over time.
    
    Args:
        data: DataFrame with 'date' and 'accuracy' columns
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if not data.empty:
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['accuracy'],
            mode='lines+markers',
            name='Accuracy',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title='Accuracy Trend',
        xaxis_title='Date',
        yaxis_title='Accuracy (%)',
        yaxis=dict(range=[0, 105]),
        template='plotly_white',
        height=400
    )
    
    return fig


def create_speed_trend_chart(data: pd.DataFrame) -> go.Figure:
    """Create line chart showing average time per question over time.
    
    Args:
        data: DataFrame with 'date' and 'avg_time' columns
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if not data.empty:
        fig.add_trace(go.Scatter(
            x=data['date'],
            y=data['avg_time'],
            mode='lines+markers',
            name='Avg Time',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title='Speed Trend',
        xaxis_title='Date',
        yaxis_title='Average Time (seconds)',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_category_breakdown_chart(data: pd.DataFrame) -> go.Figure:
    """Create bar chart showing performance by category.
    
    Args:
        data: DataFrame with category performance stats
        
    Returns:
        Plotly Figure
    """
    if data.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['question_type'],
        y=data['accuracy'],
        name='Accuracy (%)',
        marker_color='#2ecc71'
    ))
    
    fig.update_layout(
        title='Performance by Category',
        xaxis_title='Category',
        yaxis_title='Accuracy (%)',
        yaxis=dict(range=[0, 105]),
        template='plotly_white',
        height=400
    )
    
    return fig


def create_category_radar_chart(data: pd.DataFrame) -> go.Figure:
    """Create radar chart showing performance across categories.
    
    Args:
        data: DataFrame with category performance stats
        
    Returns:
        Plotly Figure
    """
    if data.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=data['accuracy'].tolist(),
        theta=data['question_type'].tolist(),
        fill='toself',
        name='Accuracy',
        line_color='#2ecc71'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title='Category Performance Radar',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_heatmap_chart(data: pd.DataFrame) -> go.Figure:
    """Create heatmap showing performance by time of day.
    
    Args:
        data: DataFrame with 'hour' and 'accuracy' columns
        
    Returns:
        Plotly Figure
    """
    if data.empty:
        return go.Figure()
    
    # Create a 24-hour array
    hours = list(range(24))
    accuracy = [0] * 24
    
    for _, row in data.iterrows():
        hour = int(row['hour'])
        accuracy[hour] = row['accuracy']
    
    # Create heatmap data
    heatmap_data = []
    for i in range(0, 24, 6):
        heatmap_data.append(accuracy[i:i+6])
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=['0-5', '6-11', '12-17', '18-23'],
        y=['Morning', 'Afternoon', 'Evening', 'Night'],
        colorscale='RdYlGn',
        text=heatmap_data,
        texttemplate='%{text:.1f}%',
        textfont={"size": 14},
        colorbar=dict(title="Accuracy %")
    ))
    
    fig.update_layout(
        title='Performance by Time of Day',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_progress_gauge(current: float, target: float, title: str = "Progress") -> go.Figure:
    """Create gauge chart for goal progress.
    
    Args:
        current: Current value
        target: Target value
        title: Chart title
        
    Returns:
        Plotly Figure
    """
    progress = (current / target * 100) if target > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': target},
        gauge={
            'axis': {'range': [None, target]},
            'bar': {'color': "#2ecc71"},
            'steps': [
                {'range': [0, target * 0.5], 'color': "#ecf0f1"},
                {'range': [target * 0.5, target * 0.8], 'color': "#d5dbdb"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))
    
    fig.update_layout(
        template='plotly_white',
        height=300
    )
    
    return fig


def create_streak_calendar(data: pd.DataFrame, weeks: int = 8) -> go.Figure:
    """Create calendar heatmap for streak visualization.
    
    Args:
        data: DataFrame with 'date' and 'sessions_completed' columns
        weeks: Number of weeks to show
        
    Returns:
        Plotly Figure
    """
    if data.empty:
        return go.Figure()
    
    # This is a simplified version - full calendar would be more complex
    fig = px.density_heatmap(
        data,
        x='date',
        y=[1] * len(data),
        z='sessions_completed',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        title='Activity Calendar',
        template='plotly_white',
        height=200,
        yaxis=dict(visible=False)
    )
    
    return fig
