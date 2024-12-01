import streamlit as st
import pandas as pd
import pytz
import math
from datetime import datetime
import streamlit_shadcn_ui as ui
import streamlit_antd_components as sac
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px


def load_custom_css():
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_custom_css()
primary_color = st.get_option("theme.primaryColor")
# --------------------AUTHENTICATION CHECK---------------------------------------------------------------
if st.session_state["authentication_status"]:
    st.session_state["credentials"] = credentials
    st.session_state["authenticated"] = True
    st.session_state["username"] = st.session_state["username"]
    st.session_state["name"] = st.session_state["name"]
    st.session_state["user_credentials"] = credentials["usernames"][
        st.session_state["username"]
    ]

    # --------------------GET USER SPECIFIC DATA(Signed in user)---------------------------------------------------------------
    username = st.session_state["username"]
    user_credentials = st.session_state["user_credentials"]
    user_territory = user_credentials["Territory_ID"]
    st.write(user_territory)
    
    from data import (
        load_route_data,
        load_daily_data,
        load_hcp_clients_data,
        load_institution_data,
        load_pending_clients_data,
    )
    
    
    df = load_daily_data()
    df["TimeStamp"] = df["TimeStamp"].str.replace("/", "-")
    df["TimeStamp"] = pd.to_datetime(
        df["TimeStamp"], format="%d-%m-%Y %H:%M:%S", dayfirst=True, errors="coerce"
    )
    current_time = datetime.now()
    user_data = []
    from datetime import datetime
    import pandas as pd
    
    # Assuming `df` is already loaded and cleaned
    df = load_daily_data()
    df["TimeStamp"] = df["TimeStamp"].str.replace("/", "-")
    df["TimeStamp"] = pd.to_datetime(
        df["TimeStamp"], format="%d-%m-%Y %H:%M:%S", dayfirst=True, errors="coerce"
    )
    
    current_time = datetime.now()
    user_data = []
    
    # Iterate over each Territory
    for territory in df["Territory"].unique():
        agent_data = df[df["Territory"].str.strip() == territory]
    
        # Skip processing if no data for this territory
        if agent_data.empty:
            continue
    
        # Calculate total reports for the current agent
        total_reports = len(agent_data)
        reports_this_year = len(
            agent_data[agent_data["TimeStamp"].dt.year == current_time.year]
        )
        reports_this_month = len(
            agent_data[agent_data["TimeStamp"].dt.month == current_time.month]
        )
    
        # Activity share calculations
        total_reports_in_df = len(df)
        total_reports_this_month = len(df[df["TimeStamp"].dt.month == current_time.month])
        activity_share = (
            (total_reports / total_reports_in_df) * 100 if total_reports_in_df > 0 else 0
        )
        activity_share_this_month = (
            (reports_this_month / total_reports_this_month) * 100
            if total_reports_this_month > 0
            else 0
        )
    
        # Get the last updated timestamp
        last_updated = agent_data["TimeStamp"].max()
    
        # Calculate time since the last update
        if pd.isna(last_updated) or last_updated is pd.NaT:
            time_since_last_update = "N/A"  # Handle missing or invalid timestamps
            last_updated_str = "N/A"
        else:
            time_ago = (current_time - last_updated).total_seconds()
            days_ago = time_ago // (24 * 3600)
            hours_ago = (time_ago % (24 * 3600)) // 3600
            minutes_ago = (time_ago % 3600) // 60
            seconds_ago = time_ago % 60
            time_since_last_update = f"{int(days_ago)} Days {int(hours_ago)} hrs {int(minutes_ago)} mins {int(seconds_ago)} secs"
            last_updated_str = last_updated.strftime("%d-%m-%Y")
    
        # Append data for this territory
        user_data.append(
            {
                "territory": territory,
                "last_updated": last_updated_str,
                "time_since_last_update": time_since_last_update,
                "total_reports": f"{total_reports} ({reports_this_year} this year) ({reports_this_month} this month)",
                "activity_share": f"{activity_share:.2f}%",
                "activity_share_this_month": f"{activity_share_this_month:.2f}%",
            }
        )
    
    
    # --------------------ADMIN DASHBOARD---------------------------------------------------------------
    @st.fragment()
    def admin_dashboard():
        with st.expander(
            "Client Report Last Update - (refreshes hourly)",
            expanded=True,
            icon=":material/update:",
        ):
            # Define the number of columns per row in the grid
            columns_per_row = 4
            num_rows = math.ceil(len(user_data) / columns_per_row)
            # Create a grid layout and display user metrics
            for row in range(num_rows):
                cols = st.columns(columns_per_row)  #
                # Iterate over the users for this row
                for col_index, user_index in enumerate(
                    range(row * columns_per_row, (row + 1) * columns_per_row)
                ):
                    if user_index < len(user_data):  # Ensure valid user index
                        user = user_data[user_index]
                        with cols[col_index]:
                            with st.container(border=True):
                                # Title of the card (centered)
                                st.markdown(
                                    f"""
                                                    <div style="text-align: center;">
                                                        <h4>{user['territory']}</h4>
                                                    </div>
                                                    """,
                                    unsafe_allow_html=True,
                                )
                                st.markdown(
                                    f"<p><strong>Last updated on:</strong> <span style='color: {primary_color};'>{user['last_updated']}</span></p>",
                                    unsafe_allow_html=True,
                                )
                                # Time since last update
                                st.markdown(
                                    f"""
                                                    <div style="text-align: center; font-size: 14px; line-height: 1.6;">
                                                        <p>{user['time_since_last_update']}</p>
                                                    </div>
                                                    """,
                                    unsafe_allow_html=True,
                                )
                                # Total reports
                                st.markdown(
                                    f"""
                                                    <div style="text-align: center; font-size: 14px; line-height: 1.6;">
                                                        <p>{user['total_reports']}</p>
                                                    </div>
                                                    """,
                                    unsafe_allow_html=True,
                                )
    
        with st.container(key="Timeseries_charts"):
            from forms.newrouterform import get_week_of_month
    
            def current_time():
                timezone = pytz.timezone("Africa/Nairobi")
                return datetime.now(timezone)
    
            def get_current_month_details():
                current_date = current_time()
                current_month = current_date.strftime("%b")
                return current_month
    
            def get_month_options():
                return [datetime(2024, m, 1).strftime("%b") for m in range(1, 13)]
    
            clients_dailyrpt_df = load_daily_data()  # Load daily clients_dailyrpt_df
            # Convert TimeStamp to datetime
            clients_dailyrpt_df["TimeStamp"] = clients_dailyrpt_df["TimeStamp"].str.replace(
                "/", "-"
            )
            clients_dailyrpt_df["TimeStamp"] = pd.to_datetime(
                clients_dailyrpt_df["TimeStamp"],
                dayfirst=True,
                errors="coerce",
                format="%d-%m-%Y %H:%M:%S",
            )
    
            # Extract date (optional, depending on your level of granularity)
            clients_dailyrpt_df["Date"] = clients_dailyrpt_df["TimeStamp"].dt.date
            clients_dailyrpt_df["Year"] = clients_dailyrpt_df["TimeStamp"].dt.year
            clients_dailyrpt_df["Day"] = clients_dailyrpt_df["TimeStamp"].dt.date
            territories = clients_dailyrpt_df["Territory"].unique().tolist()
    
            territory_filters, yr_filters, mnth_filters, wk_filters, day_filters = (
                st.columns([1, 1, 1, 1, 1])
            )
            # ---------------FILTERS
            # Add "Select All" at the beginning
            territories.insert(0, "Select All")
            with territory_filters:
                territory_filter = st.selectbox(
                    "Territory",
                    options=territories,
                    index=0,
                    key="territory_filter",
                )
            with yr_filters:
                year_options = sorted(clients_dailyrpt_df["Year"].unique())
                year_options.insert(0, "Select All")  # Add "Select All" at the beginning
                yr_filter = st.selectbox(
                    "Year",
                    options=year_options,
                    index=0,
                    key="yr_filter",
                )
            with mnth_filters:
                month_options = get_month_options()
                month_options.insert(0, "Select All")  # Add "Select All" at the beginning
                mnth_filter = st.selectbox(
                    "Month",
                    options=month_options,
                    index=0,
                    key="mnth_filter",
                )
            with wk_filters:
                week_options = get_week_of_month()
                week_options.insert(0, "Select All")  # Add "Select All" at the beginning
                wk_filter = st.selectbox(
                    "Week",
                    options=week_options,
                    index=0,
                    key="wk_filter",
                )
            with day_filters:
                day_filter = st.date_input(
                    "Date",
                    value=None,
                    # format="DD-MM-YYYY",
                    key="date_filter",
                )
    
            # Create a time series plot
            def plot_time_series(data, show_legend):
                fig = px.line(
                    data,
                    x="Date",
                    y="Count",
                    color="Territory",
                    color_discrete_sequence=px.colors.sequential.Rainbow,
                    # title="Time Series Count by Territory",
                    labels={"Date": "", "Count": "Records"},
                    line_shape="spline",
                )
                fig.update_traces(mode="lines+markers")  # Add markers for better visibility
                fig.update_layout(
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False),
                    height=600,
                    showlegend=show_legend,
                    # plot_bgcolor="white",
                    # paper_bgcolor="black",
                )
                return fig
    
            # Function to generate Bar Chart
            def plot_bar_chart(data, show_legend):
                fig = px.bar(
                    data,
                    x="Date",
                    y="Count",
                    color="Territory",
                    # title="Bar Chart of Count by Territory",
                    color_discrete_sequence=px.colors.sequential.Rainbow,
                    labels={"Date": "", "Count": "Records"},
                )
                fig.update_layout(
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False, showticklabels=False),
                    height=600,
                    showlegend=show_legend,
                )
                # Add data labels to the bars
                fig.update_traces(
                    textposition="outside", textfont=dict(size=12), text=data["Count"]
                )
                return fig
    
            # Filter data based on selected filters
            filtered_data = clients_dailyrpt_df
            if territory_filter != "Select All":
                filtered_data = filtered_data[
                    filtered_data["Territory"] == territory_filter
                ]
            else:
                territory_filter = territories[1:]
    
            if yr_filter != "Select All":
                filtered_data = filtered_data[filtered_data["Year"] == yr_filter]
            else:
                yr_filter = yr_filter[1:]
    
            if mnth_filter != "Select All":
                filtered_data = filtered_data[filtered_data["Month"] == mnth_filter]
            else:
                mnth_filter = mnth_filter[1:]
    
            if wk_filter != "Select All":
                filtered_data = filtered_data[filtered_data["Week"] == wk_filter]
            else:
                wk_filter = wk_filter[1:]
            if day_filter:
                filtered_data = filtered_data[filtered_data["Day"] == day_filter]
    
            # Group filtered data for visualization
            grouped_filtered_data = (
                filtered_data.groupby(["Date", "Territory"])
                .size()
                .reset_index(name="Count")
            )
            with st.expander("Settings", expanded=True, icon=":material/settings:"):
                brchrttggl, lgndtgl = st.columns(2)
                with brchrttggl:
                    # Create the toggle switch using shadcn library
                    chart_toggle = ui.switch(
                        default_checked=False,
                        label="Switch to Bar Chart",
                        key="switch_visualization",
                    )
                    # chart_toggle = sac.switch(
                    #     label="Switch to Bar Chart",
                    #     description="toggle on to view bar chart",
                    #     position="left",
                    #     size="sm",
                    #     on_color="#8e00c6",
                    #     off_color="gray",
                    # )
                with lgndtgl:
                    # Create the toggle switch for showing/hiding the legend
                    legend_toggle = ui.switch(
                        default_checked=False, label="Legend", key="legend_toggle"
                    )
            # Get the value of the legend toggle
            show_legend = legend_toggle
            # Create and display the Plotly chart
            if not grouped_filtered_data.empty:
                if chart_toggle:
                    st.plotly_chart(
                        plot_bar_chart(grouped_filtered_data, show_legend),
                        use_container_width=True,
                    )
                else:
                    st.plotly_chart(
                        plot_time_series(grouped_filtered_data, show_legend),
                        use_container_width=True,
                    )
            else:
                sac.result(
                    label="Oops! No data available for the selected filter. Please try a different filter.",
                    status="empty",
                    key="router_table_empty_state",
                )
    
    
    # --------------------USER DASHBOARD---------------------------------------------------------------
    # def user_dashboard():
    #     with st.expander(
    #         "Metrics Summary - (based on clients reports)",
    #         icon=":material/bar_chart:",
    #         expanded=True,
    #     ):
    #         # Fetch data from API
    #         territory = user_territory
    #         cols = st.columns(3)
    #         with cols[0]:
    #             ui.metric_card(
    #                 title="Last Updated",
    #                 content=f"""{last_updated}""",
    #                 description=None,
    #                 key="user_metric_card1",
    #             )
    #         with cols[1]:
    #             ui.metric_card(
    #                 title="Time of the last update",
    #                 content=f"""{time_since_last_update}""",
    #                 description=None,
    #                 key="user_metric_card2",
    #             )
    #         with cols[2]:
    #             ui.metric_card(
    #                 title="Total Reports",
    #                 content=f"""{total_reports}""",
    #                 description=None,
    #                 key="user_metric_card3",
    #             )
    #     st.title("Upcoming Features")
    
    
    def user_dashboard():
        with st.expander(
            "Metrics Summary - (based on clients reports)",
            icon=":material/bar_chart:",
            expanded=True,
        ):
            # Fetch the user's territory
            territory = user_territory
    
            # Filter the DataFrame based on the user's territory
            user_data_df = df[df["Territory"].str.strip() == territory]
    
            if user_data_df.empty:
                st.warning(f"No data available for territory: {territory}")
                return
    
            # Calculate metrics for the filtered data
            current_time = datetime.now()
            total_reports = len(user_data_df)
            last_updated = user_data_df["TimeStamp"].max()
    
            # Time since the last update
            if pd.isna(last_updated) or last_updated is pd.NaT:
                last_updated_str = "N/A"
                time_since_last_update = "N/A"
            else:
                last_updated_str = last_updated.strftime("%d-%m-%Y")
                time_ago = (current_time - last_updated).total_seconds()
                days_ago = time_ago // (24 * 3600)
                hours_ago = (time_ago % (24 * 3600)) // 3600
                minutes_ago = (time_ago % 3600) // 60
                seconds_ago = time_ago % 60
                time_since_last_update = f"{int(days_ago)} Days {int(hours_ago)} hrs {int(minutes_ago)} mins {int(seconds_ago)} secs"
    
            # Display metrics in columns
            cols = st.columns(3)
            with cols[0]:
                ui.metric_card(
                    title="Last Updated",
                    content=f"""{last_updated_str}""",
                    description=None,
                    key="user_metric_card1",
                )
            with cols[1]:
                ui.metric_card(
                    title="Time of the last update",
                    content=f"""{time_since_last_update}""",
                    description=None,
                    key="user_metric_card2",
                )
            with cols[2]:
                ui.metric_card(
                    title="Total Reports",
                    content=f"""{total_reports}""",
                    description=None,
                    key="user_metric_card3",
                )
