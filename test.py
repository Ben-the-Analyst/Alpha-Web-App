import plotly.graph_objects as go

fig = go.Figure()

# Add traces (bar plots)
fig.add_trace(go.Bar(x=["A", "B", "C"], y=[10, 20, 30]))
fig.add_trace(go.Bar(x=["A", "B", "C"], y=[5, 10, 15]))

# Set barmode
fig.update_layout(barmode="group")  # Try 'stack' or 'overlay' instead of 'group'

fig.show()
