"""Visualization functions using Plotly."""

# pyright: reportMissingImports=false

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _apply_base_layout(fig: go.Figure, title: str, height: int = 360) -> go.Figure:
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=56, b=20),
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Manrope, Segoe UI, sans-serif", color="#11212c"),
        title_font=dict(size=17, color="#11212c"),
    )
    return fig


def create_accuracy_trend_chart(data: pd.DataFrame) -> go.Figure:
    """Create line chart showing accuracy over time."""
    fig = go.Figure()
    if not data.empty:
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=data["accuracy"],
                mode="lines+markers",
                name="Accuracy",
                line=dict(color="#0f766e", width=3),
                marker=dict(size=7, color="#f59e0b", line=dict(width=1, color="#ffffff")),
                hovertemplate="%{x|%b %d}<br>%{y:.1f}%<extra></extra>",
            )
        )
        rolling = data["accuracy"].rolling(window=3, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=rolling,
                mode="lines",
                name="3-session trend",
                line=dict(color="#115e59", width=2, dash="dot"),
                hovertemplate="%{x|%b %d}<br>%{y:.1f}% trend<extra></extra>",
            )
        )

    _apply_base_layout(fig, "Accuracy Trend")
    fig.update_yaxes(range=[0, 103], ticksuffix="%", gridcolor="rgba(17,33,44,0.08)")
    fig.update_xaxes(gridcolor="rgba(17,33,44,0.05)")
    return fig


def create_speed_trend_chart(data: pd.DataFrame) -> go.Figure:
    """Create line chart showing average time per question over time."""
    fig = go.Figure()
    if not data.empty:
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=data["avg_time"],
                mode="lines+markers",
                name="Avg time",
                line=dict(color="#2563eb", width=3),
                marker=dict(size=7, color="#93c5fd", line=dict(width=1, color="#ffffff")),
                hovertemplate="%{x|%b %d}<br>%{y:.2f}s<extra></extra>",
            )
        )

    _apply_base_layout(fig, "Speed Trend")
    fig.update_yaxes(title="Seconds", gridcolor="rgba(17,33,44,0.08)")
    fig.update_xaxes(gridcolor="rgba(17,33,44,0.05)")
    return fig


def create_question_volume_chart(data: pd.DataFrame) -> go.Figure:
    """Create bar chart showing question volume by day."""
    fig = go.Figure()
    if not data.empty:
        fig.add_trace(
            go.Bar(
                x=data["date"],
                y=data["questions"],
                marker=dict(color="#f59e0b"),
                name="Questions",
                hovertemplate="%{x|%b %d}<br>%{y} questions<extra></extra>",
            )
        )

    _apply_base_layout(fig, "Question Volume")
    fig.update_yaxes(title="Questions", gridcolor="rgba(17,33,44,0.08)")
    fig.update_xaxes(gridcolor="rgba(17,33,44,0.05)")
    return fig


def create_category_breakdown_chart(data: pd.DataFrame) -> go.Figure:
    """Create grouped bar chart showing category accuracy and speed."""
    if data.empty:
        return _apply_base_layout(go.Figure(), "Performance by Category")

    display = data.copy()
    display["question_type"] = display["question_type"].str.title()
    display = display.sort_values("questions_answered", ascending=False)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=display["question_type"],
            y=display["accuracy"],
            name="Accuracy",
            marker_color="#0f766e",
            hovertemplate="%{x}<br>%{y:.1f}% accuracy<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=display["question_type"],
            y=display["avg_time"],
            name="Avg time",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#f59e0b", width=2),
            marker=dict(size=8),
            hovertemplate="%{x}<br>%{y:.2f}s avg<extra></extra>",
        )
    )

    _apply_base_layout(fig, "Performance by Category")
    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Accuracy %", range=[0, 103], ticksuffix="%", gridcolor="rgba(17,33,44,0.08)"),
        yaxis2=dict(title="Avg seconds", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="rgba(17,33,44,0.05)")
    return fig


def create_category_radar_chart(data: pd.DataFrame) -> go.Figure:
    """Create radar chart showing performance across categories."""
    if data.empty:
        return _apply_base_layout(go.Figure(), "Category Balance", 420)

    display = data.copy()
    display["question_type"] = display["question_type"].str.title()

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=display["accuracy"].tolist(),
            theta=display["question_type"].tolist(),
            fill="toself",
            name="Accuracy",
            line=dict(color="#0f766e", width=2),
            fillcolor="rgba(15,118,110,0.24)",
        )
    )

    _apply_base_layout(fig, "Category Balance", 420)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%", gridcolor="rgba(17,33,44,0.12)")
        ),
        showlegend=False,
    )
    return fig


def create_weekly_consistency_chart(data: pd.DataFrame) -> go.Figure:
    """Create week-level question consistency chart.

    With a single row of data we render a simple bar (no accuracy line
    overlay - a one-point line is misleading).
    """
    fig = go.Figure()
    if not data.empty:
        fig.add_trace(
            go.Bar(
                x=data["week_start"],
                y=data["questions"],
                marker_color="#0f766e",
                name="Questions",
                hovertemplate="Week of %{x|%b %d}<br>%{y} questions<extra></extra>",
            )
        )
        # Only draw the accuracy line when there are >=2 weeks of data;
        # a single marker line slope is meaningless.
        if len(data.index) >= 2:
            fig.add_trace(
                go.Scatter(
                    x=data["week_start"],
                    y=data["accuracy"],
                    mode="lines+markers",
                    name="Accuracy",
                    yaxis="y2",
                    line=dict(color="#f59e0b", width=2),
                    hovertemplate="Week of %{x|%b %d}<br>%{y:.1f}% accuracy<extra></extra>",
                )
            )

    _apply_base_layout(fig, "Weekly Consistency", 340)
    fig.update_layout(
        yaxis=dict(title="Questions", gridcolor="rgba(17,33,44,0.08)"),
        yaxis2=dict(title="Accuracy %", overlaying="y", side="right", showgrid=False),
    )
    return fig


def create_heatmap_chart(data: pd.DataFrame) -> go.Figure:
    """Create heatmap showing performance by time of day.

    Falls back to a single-row bar chart when there is too little
    distinct hour data to render a meaningful density heatmap.
    """
    if data.empty:
        return _apply_base_layout(go.Figure(), "Performance by Time of Day")

    display = pd.DataFrame(data).copy()
    windows = display["hour"].astype(int).map(lambda h: f"{h:02d}:00")
    display = display.assign(window=windows)

    # Density heatmaps render misleadingly with <2 distinct x values
    # (single column gets stretched) - degrade to a simple bar chart.
    if display["window"].nunique() < 2:
        fig = go.Figure(
            go.Bar(
                x=display["window"],
                y=display["accuracy"],
                marker_color="#0f766e",
                hovertemplate="%{x}<br>%{y:.1f}% accuracy<extra></extra>",
            )
        )
        _apply_base_layout(fig, "Performance by Time of Day", 320)
        fig.update_yaxes(title="Accuracy %", range=[0, 103], ticksuffix="%")
        return fig

    fig = px.density_heatmap(
        display,
        x="window",
        y=["Accuracy"] * len(display),
        z="accuracy",
        color_continuous_scale="Tealgrn",
    )
    fig.update_traces(hovertemplate="%{x}<br>%{z:.1f}% accuracy<extra></extra>")
    _apply_base_layout(fig, "Performance by Time of Day", 320)
    return fig


def create_progress_gauge(current: float, target: float, title: str = "Progress") -> go.Figure:
    """Create gauge chart for goal progress.

    Guards against ``target == 0`` (which would produce a gauge with a
    zero-width band and is most likely a misconfiguration).
    """
    # Floor target at 1 so downstream multiplications (0.7 * target,
    # 1.2 * target, the percent computation) cannot divide-by-zero or
    # render an empty gauge.
    safe_target = max(target, 1)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=current,
            number={"suffix": "%"},
            title={"text": title},
            delta={"reference": safe_target},
            gauge={
                "axis": {"range": [0, max(safe_target * 1.2, 100)]},
                "bar": {"color": "#0f766e"},
                "steps": [
                    {"range": [0, safe_target * 0.7], "color": "#fee2e2"},
                    {"range": [safe_target * 0.7, safe_target], "color": "#fef3c7"},
                    {"range": [safe_target, max(safe_target * 1.2, 100)], "color": "#dcfce7"},
                ],
                "threshold": {
                    "line": {"color": "#b42318", "width": 3},
                    "thickness": 0.75,
                    "value": safe_target,
                },
            },
        )
    )
    _apply_base_layout(fig, title, 280)
    return fig


def create_streak_calendar(data: pd.DataFrame, weeks: int = 8) -> go.Figure:
    """Create a compact streak activity calendar.

    Falls back to a single bar when there is too little distinct date
    data to render a meaningful density heatmap.
    """
    if data.empty:
        return _apply_base_layout(go.Figure(), "Activity Calendar", 260)

    display = data.copy()
    display["date"] = pd.to_datetime(display["date"])
    cutoff = display["date"].max() - pd.Timedelta(weeks=weeks)
    display = display[display["date"] >= cutoff]

    if display.empty:
        return _apply_base_layout(go.Figure(), "Activity Calendar", 260)

    # density_heatmap with a single distinct x stretches a full-width
    # band and reads as "every day" - degrade to a single bar.
    if display["date"].nunique() < 2:
        fig = go.Figure(
            go.Bar(
                x=display["date"],
                y=display["sessions_completed"],
                marker_color="#0f766e",
                hovertemplate="%{x|%b %d}<br>%{y} sessions<extra></extra>",
            )
        )
        _apply_base_layout(fig, "Activity Calendar", 260)
        fig.update_yaxes(title="Sessions")
        return fig

    fig = px.density_heatmap(
        display,
        x="date",
        y=["Sessions"] * len(display),
        z="sessions_completed",
        color_continuous_scale="Teal",
    )
    fig.update_traces(hovertemplate="%{x|%b %d}<br>%{z} sessions<extra></extra>")
    _apply_base_layout(fig, "Activity Calendar", 260)
    fig.update_yaxes(visible=False)
    return fig
