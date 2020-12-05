import plotly.graph_objects as go

def plotly_map():
    fig = go.Figure(go.Scattergeo())
    fig.update_geos(projection_type="orthographic")
    fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    return fig