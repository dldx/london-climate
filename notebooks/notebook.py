# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas==2.2.3",
#     "plotly-express",
#     "plotly==6.0.1",
#     "numpy==2.2.5",
#     "polars==1.29.0",
#     "pyarrow==20.0.0",
# ]
# ///

import marimo

__generated_with = "0.13.3"
app = marimo.App()

with app.setup:
    import marimo as mo


@app.cell
def _():
    import micropip
    return (micropip,)


@app.cell
async def _(micropip):
    await micropip.install("pyarrow")
    await micropip.install("polars")
    await micropip.install("plotly")
    return


@app.cell
def _(date_observed, format_date):
    mo.md(
        f"""
        # London Temperature Analysis (1924-2024)

        This notebook analyzes historical temperature data for London, focusing on {format_date(date_observed.value)} temperatures over the past 100 years.
        We'll highlight tomorrow's forecasted temperature of 29°C, which appears to be exceptionally warm compared to historical data.
        """
    )
    return


@app.cell
def _():
    import pandas as pd
    from datetime import datetime
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    import polars as pl
    return datetime, go, np, pd, pl, px


@app.cell
def _():
    date_observed = mo.ui.date("2025-05-01", label="Day to observe")
    date_observed
    return (date_observed,)


@app.cell
def load_data(pd, pl):
    # Load the dataset
    # Attempt to load from the default location for downloaded Kaggle datasets
    df = pl.read_csv(
        str(mo.notebook_location() / "public/london_weather_data_1979_to_2023.csv")
    ).to_pandas()

    # Process the dataset according to the provided column specifications:
    # DATE: Date in YYYYMMDD format
    # TG: Daily mean temperature in 0.1°C
    # TX: Daily maximum temperature in 0.1°C
    # TN: Daily minimum temperature in 0.1°C

    # Convert DATE to datetime
    df["date"] = pd.to_datetime(df["DATE"], format="%Y%m%d")

    # Convert temperatures from 0.1°C to °C
    if "TG" in df.columns:
        df["mean_temp"] = df["TG"] / 10.0
    if "TX" in df.columns:
        df["max_temp"] = df["TX"] / 10.0
    if "TN" in df.columns:
        df["min_temp"] = df["TN"] / 10.0

    # Display the first few rows of processed data
    df[["date", "mean_temp", "max_temp", "min_temp"]]
    return (df,)


@app.cell
def filter_may_1st(date_observed, df, format_date):
    # Filter for May 1st data only
    may_1st_data = df[
        (df.date.dt.month == date_observed.value.month)
        & (df.date.dt.day == date_observed.value.day)
    ].assign(year=df.date.dt.year)

    # Sort by year
    may_1st_data = may_1st_data.sort_values("date", ascending=True)

    # Display the May 1st data in a table
    may_1st_preview = (
        may_1st_data[["date", "year", "mean_temp", "max_temp", "min_temp"]]
        .sort_values("year", ascending=False)
        .head(10)
    )


    mo.vstack(
        [
            mo.md(
                f"### Most recent {format_date(date_observed.value)} temperature records:"
            ),
            may_1st_preview,
        ]
    )
    return (may_1st_data,)


@app.cell
def plot_historical_temperatures(
    date_observed,
    datetime,
    format_date,
    go,
    may_1st_data,
    np,
    pd,
):
    # Add tomorrow's forecast
    tomorrow = pd.DataFrame(
        {
            "date": [datetime(2025, 5, 1)],
            "mean_temp": [20.0],
            "max_temp": [29.0],
            "min_temp": [15.0],
        }
    )

    # Combine historical data with forecast
    plot_data = pd.concat([may_1st_data, tomorrow])

    # Create the temperature chart with Plotly
    fig = go.Figure()

    # Add mean temperature line
    fig.add_trace(
        go.Scatter(
            x=plot_data["year"],
            y=plot_data["mean_temp"],
            mode="lines+markers",
            name="Mean Temperature",
            line=dict(color="blue", width=2),
            marker=dict(size=7),
        )
    )

    # Add max and min temperature range if available
    if "max_temp" in plot_data.columns and "min_temp" in plot_data.columns:
        fig.add_trace(
            go.Scatter(
                x=plot_data["year"],
                y=plot_data["max_temp"],
                name="Max day temp.",
                mode="lines",
                line=dict(width=0, color="rgba(0, 0, 255, 0.3)"),
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=plot_data["year"],
                y=plot_data["min_temp"],
                name="Min day temp.",
                mode="lines",
                line=dict(width=0, color="rgba(0, 0, 255, 0.3)"),
                fill="tonexty",
                fillcolor="rgba(0, 0, 255, 0.3)",
            )
        )

    # Add a point to highlight tomorrow's temperature
    fig.add_trace(
        go.Scatter(
            x=[2025],
            y=[29.0],
            mode="markers",
            marker=dict(size=15, color="red", symbol="star"),
            name=f"Forecast for {format_date(date_observed.value)}, 2025 (29°C)",
        )
    )

    # Add trend line for mean temperature
    historical_data = plot_data[plot_data["year"] < 2025]
    z = np.polyfit(historical_data["year"], historical_data["mean_temp"], 1)
    p = np.poly1d(z)

    # Calculate slope for annotation
    slope = z[0]
    trend_per_century = slope * 100

    fig.add_trace(
        go.Scatter(
            x=historical_data["year"],
            y=p(historical_data["year"]),
            mode="lines",
            line=dict(dash="dash", color="green", width=2),
            name=f"Temperature Trend ({trend_per_century:.1f}°C+/century)",
        )
    )

    # Adjust layout
    fig.update_layout(
        title=f"<b>London Temperature on Worker's day (1st Map) (1980-2025)</b>",
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Temperature (°C)</b>",
        template="plotly_white",
        showlegend=False,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1
        ),
        yaxis_range=[-10, 30],
        annotations=[
            dict(
                x=2025,
                y=29.0,
                xref="x",
                yref="y",
                text="Todays High: 29°C",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-40,
            )
        ],
    )

    # Add reference lines for temperature milestones
    historical_mean = historical_data["mean_temp"].mean()
    fig.add_shape(
        type="line",
        x0=min(plot_data["year"]),
        y0=historical_mean,
        x1=max(plot_data["year"]),
        y1=historical_mean,
        line=dict(color="gray", width=1, dash="dot"),
    )

    fig.add_annotation(
        x=max(plot_data["year"]) + 5,
        y=historical_mean,
        text=f"Historical Mean: {historical_mean:.1f}°C",
        showarrow=False,
        yshift=10,
    )
    return


@app.cell
def temperature_comparison(date_observed, format_date, go, may_1st_data):
    # Calculate statistics for historical May 1st temperatures
    avg_mean_temp = may_1st_data["mean_temp"].mean()
    max_historical_mean = may_1st_data["mean_temp"].max()
    min_historical_mean = may_1st_data["mean_temp"].min()

    # Calculate statistics for max temperatures if available
    if "max_temp" in may_1st_data.columns:
        all_time_max = may_1st_data["max_temp"].max()
        all_time_max_year = may_1st_data.loc[
            may_1st_data["max_temp"].idxmax(), "year"
        ]
    else:
        all_time_max = max_historical_mean
        all_time_max_year = may_1st_data.loc[
            may_1st_data["mean_temp"].idxmax(), "year"
        ]

    # Calculate how many standard deviations tomorrow's temp is from the mean
    std_dev = may_1st_data["mean_temp"].std()
    forecast_temp = 29.0
    z_score = (forecast_temp - avg_mean_temp) / std_dev

    # Calculate percentile of tomorrow's forecast compared to historical data
    percentile = (may_1st_data["mean_temp"] < forecast_temp).mean() * 100

    # Create temperature comparison chart
    may_first_fig = go.Figure()

    # Add histogram of historical temperatures
    may_first_fig.add_trace(
        go.Histogram(
            x=may_1st_data["mean_temp"],
            nbinsx=20,
            name="Historical Mean Temperatures",
            opacity=0.7,
            marker_color="blue",
        )
    )

    # Add vertical line for average temperature
    may_first_fig.add_vline(
        x=avg_mean_temp,
        line_dash="solid",
        line_color="blue",
        annotation_text=f"Average: {avg_mean_temp:.1f}°C",
        annotation_position="top right",
    )

    # Add vertical line for tomorrow's forecast
    may_first_fig.add_vline(
        x=forecast_temp,
        line_dash="solid",
        line_color="red",
        annotation_text=f"Tomorrow: {forecast_temp:.1f}°C",
        annotation_position="top right",
    )

    # Add vertical line for all-time maximum if different from forecast
    if all_time_max < forecast_temp:
        may_first_fig.add_vline(
            x=all_time_max,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Previous Record: {all_time_max:.1f}°C ({int(all_time_max_year)})",
            annotation_position="top left",
        )

    # Update layout
    may_first_fig.update_layout(
        title=f"Distribution of Historical {format_date(date_observed.value)} Temperatures in London",
        xaxis_title="Temperature (°C)",
        yaxis_title="Count of Years",
        template="plotly_white",
    )


    # Return both plots
    return (
        all_time_max,
        all_time_max_year,
        avg_mean_temp,
        forecast_temp,
        max_historical_mean,
        min_historical_mean,
        percentile,
        z_score,
    )


@app.cell
def _(date_observed, format_date, may_1st_data, px):
    # Calculate decade averages to show warming trend
    may_1st_data["decade"] = (may_1st_data["year"] // 10) * 10
    decade_avg = may_1st_data.groupby("decade")["mean_temp"].mean().reset_index()

    # Create decade comparison chart
    decade_fig = px.bar(
        decade_avg,
        x="decade",
        y="mean_temp",
        title=f"Average {format_date(date_observed.value)} Temperature by Decade",
        labels={"decade": "Decade", "mean_temp": "Average Temperature (°C)"},
        color="mean_temp",
        color_continuous_scale="Viridis",
    )
    decade_fig.update_layout(template="plotly_white")
    return


@app.cell
def _(
    all_time_max,
    all_time_max_year,
    avg_mean_temp,
    date_observed,
    forecast_temp,
    format_date,
    max_historical_mean,
    may_1st_data,
    min_historical_mean,
    percentile,
    z_score,
):
    # Get recent years for comparison
    recent_years = 30
    recent_avg = may_1st_data[
        may_1st_data["year"] >= (max(may_1st_data["year"]) - recent_years)
    ]["mean_temp"].mean()

    # Display charts and statistics
    mo.md(f"""
    ## Temperature Comparison

    ### Historical Statistics for {format_date(date_observed.value)} in London:

    - **Historical Average Temperature:** {avg_mean_temp:.1f}°C
    - **Historical Maximum Mean Temperature:** {max_historical_mean:.1f}°C
    - **Historical Minimum Mean Temperature:** {min_historical_mean:.1f}°C
    - **All-time Highest Temperature:** {all_time_max:.1f}°C (Year: {int(all_time_max_year)})
    - **Average Temperature over the last {recent_years} years:** {recent_avg:.1f}°C

    ### Tomorrow's Forecast:

    Tomorrow's forecast of **29.0°C** is:
    - {z_score:.1f} standard deviations above the historical average
    - In the {percentile:.1f}th percentile of historical records
    - {"Breaking the all-time record" if forecast_temp > all_time_max else f"{forecast_temp - all_time_max:.1f}°C below the all-time record"}

    This makes it an **{"extremely" if abs(z_score) > 3 else "very" if abs(z_score) > 2 else "somewhat"}** unusual temperature for May 1st in London.
    """)
    return


@app.cell
def data_sources():
    mo.md(
        """
        ## Data Sources and Methods

        ### Data Sources:

        - Historical weather data from London Weather Data Kaggle dataset
        - Column specifications:
            - **DATE**: Date in YYYYMMDD format
            - **TX**: Daily maximum temperature in 0.1°C
            - **TN**: Daily minimum temperature in 0.1°C
            - **TG**: Daily mean temperature in 0.1°C
            - **SS**: Daily sunshine duration in 0.1 hours
            - **SD**: Daily snow depth in 1 cm
            - **RR**: Daily precipitation amount in 0.1 mm
            - **QQ**: Daily global radiation in W/m²
            - **PP**: Daily sea level pressure in 0.1 hPa
            - **HU**: Daily relative humidity in %
            - **CC**: Daily cloud cover in oktas

        ### Methods:

        - Converted temperature values from 0.1°C to °C
        - Filtered data for May 1st across all available years
        - Calculated statistical measures (mean, max, min, standard deviation)
        - Created time series and distribution visualizations using Plotly
        - Conducted decade-by-decade analysis to identify long-term trends
        """
    )
    return


@app.cell
def _():
    def get_ordinal_suffix(day):
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return str(day) + suffix


    def format_date(date_obj):
        # Get the month name
        month_name = date_obj.strftime("%B")

        # Get the day with ordinal suffix
        day_with_suffix = get_ordinal_suffix(date_obj.day)

        return f"{month_name} {day_with_suffix}"
    return (format_date,)


if __name__ == "__main__":
    app.run()
