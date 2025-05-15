import plotly.express as px
import pandas as pd
import streamlit as st

def plot_top_slowest_requests(df, top_n=10, return_fig=False):
    df['short_url'] = df['url'].apply(lambda u: u if len(u) < 80 else u[:77] + '...')
    df['status_category'] = df['status'].apply(lambda s: f"{s // 100}xx")
    df['label'] = df.apply(lambda r: f"{r['time_ms']} ms (TTFB: {r['wait_time']} ms)" if r['wait_time'] > 500 else f"{r['time_ms']} ms", axis=1)
    df = df.sort_values(by='time_ms', ascending=False).head(top_n)
    fig = px.bar(df, x='time_ms', y='short_url', orientation='h',
                 color='status_category',
                 text='label',
                 title=f"Top {top_n} Slowest Requests",
                 labels={'time_ms': 'Load Time (ms)', 'short_url': 'Request URL'},
                 color_discrete_sequence=px.colors.qualitative.Pastel)
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

