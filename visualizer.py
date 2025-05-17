import plotly.express as px
import pandas as pd
import streamlit as st

def plot_top_slowest_requests(df, top_n=10, return_fig=False):
    df = df.copy()
    df['short_url'] = df['url'].apply(lambda u: u if len(u) < 80 else u[:77] + '...')
    df['status_category'] = df['status'].apply(lambda s: f"{s // 100}xx")

    # Ensure all timing fields are present and clean
    for col in ['dns_time', 'connect_time', 'ssl_time', 'wait_time', 'receive_time']:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].replace(-1, 0).fillna(0)

    # Sort by total time and select top N
    df = df.sort_values(by='time_ms', ascending=False).head(top_n)

    # Plot horizontal stacked bar chart
    fig = px.bar(
        df,
        y='short_url',
        x=['dns_time', 'connect_time', 'ssl_time', 'wait_time', 'receive_time'],
        orientation='h',
        labels={
            'short_url': 'Request URL',
            'value': 'Time (ms)',
            'variable': 'Timing Phase'
        },
        title=f"Top {top_n} Slowest Requests – Timing Breakdown",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_layout(
        barmode='stack',
        yaxis_title='',
        xaxis_title='Total Time (ms)',
        height=600
    )
    fig.update_yaxes(autorange='reversed')

    if return_fig:
        return fig
    fig.show()

def plot_status_code_distribution(df, return_fig=False):
    df['status_category'] = df['status'].apply(lambda s: f"{s // 100}xx")
    count_df = df['status_category'].value_counts().reset_index()
    count_df.columns = ['status_category', 'count']
    fig = px.pie(count_df, names='status_category', values='count',
                 title='HTTP Status Code Distribution',
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textinfo='percent+label')
    if return_fig:
        return fig
    fig.show()


def plot_domain_load_time(df, return_fig=False):
    df = df.copy()

    # Extract domain from URL
    df['domain'] = df['url'].apply(lambda u: u.split('/')[2] if '//' in u else 'unknown')

    # Group by domain and sum total load time
    domain_df = df.groupby('domain')['time_ms'].sum().reset_index()

    # Sort and take top 10
    domain_df = domain_df.sort_values(by='time_ms', ascending=False).head(10)

    # Create bar chart
    fig = px.bar(
        domain_df,
        x='domain',
        y='time_ms',
        title='Top Domains by Total Load Time',
        labels={'domain': 'Domain', 'time_ms': 'Total Load Time (ms)'},
        color='time_ms',
        color_continuous_scale='Blues'
    )

    fig.update_layout(height=400)

    if return_fig:
        return fig
    fig.show()

