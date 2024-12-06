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
from data import (
    load_route_data,
    load_daily_data,
    load_hcp_clients_data,
    load_institution_data,
    # load_pending_clients_data,
)
from forms.newrouterform import get_week_of_month


# --------------------ADMIN DASHBOARD---------------------------------------------------------------
@st.fragment(run_every="1h")
def admin_dashboard():
    alertcol, butncol = st.columns([4, 1])
    with alertcol:
        sac.alert(
            label="Dashboard **Refreshes Hourly**. Dashboard is meant to track performance and activities of the team.",
            description=None,
            banner=sac.Banner(play=True, direction="left", speed=30, pauseOnHover=True),
            icon=sac.BsIcon(name="info-circle", size=25, color=None),
            color="success",
            # closable=True,
        )
    with butncol:
        refresh_button = st.empty()

    df = load_daily_data()
    df["TimeStamp"] = df["TimeStamp"].str.replace("/", "-")
    df["TimeStamp"] = pd.to_datetime(
        df["TimeStamp"], format="%d-%m-%Y %H:%M:%S", dayfirst=True, errors="coerce"
    )
    current_time = datetime.now()
    user_data = []
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
        total_reports_this_month = len(
            df[df["TimeStamp"].dt.month == current_time.month]
        )
        activity_share = (
            (total_reports / total_reports_in_df) * 100
            if total_reports_in_df > 0
            else 0
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
    # ============CLIENTS===================================================================
    with st.expander("Clients", expanded=False, icon=":material/groups:"):
        # ------- METRICS--------------------------------
        client_data = load_hcp_clients_data()
        total_clients = len(client_data)
        ui.metric_card("Total Clients", content=f"{total_clients}", description=None)
        # Create a grid layout and display TERRITORY metrics
        st.write("By Territories")
        clients_agg = []
        for territory in df["Territory"].unique():
            territory_client_data = client_data[
                client_data["Territory"].str.strip() == territory
            ]
            if territory_client_data.empty:
                continue
            agent_total_clients = len(territory_client_data)
            clients_agg.append(
                {
                    "territory": territory,
                    "agent_total_clients": agent_total_clients,
                }
            )
        for user in user_data:
            territory = user["territory"]
            matching_client = next(
                (client for client in clients_agg if client["territory"] == territory),
                None,
            )
            if matching_client:
                user["agent_total_clients"] = matching_client["agent_total_clients"]
            else:
                user["agent_total_clients"] = 0  # Default to 0 if no clients found

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
                        ui.metric_card(
                            title=f"{user['territory']}",
                            content=f"{user['agent_total_clients']}",
                            description=None,
                        )
        # -----------------CLIENTS DISTRIBUTION----------------------------------
        (
            territory_filters,
            address_filters,
            workplaceType_filters,
            workplace_filters,
            clearfilters,
        ) = st.columns([1, 1, 1, 1, 1], vertical_alignment="bottom")
        # ---------------FILTERS
        with clearfilters:

            def reset_filters():
                st.session_state.CLNTDBterritory_filter = "Select All"
                st.session_state.clntdb_address_filter = "Select All"
                st.session_state.clntdb_workplaceType_filter = "Select All"
                st.session_state.clntdb_workplace_filter = "Select All"

            # Add a reset button
            if st.button(
                "Reset Filters",
                icon=":material/rule_settings:",
                key="reset_clntdb_filters",
            ):
                reset_filters()
        territories = client_data["Territory"].unique().tolist()
        # Add "Select All" at the beginning
        # Insert "Select All" as the first option for Territories
        territories = client_data["Territory"].unique().tolist()
        territories.insert(0, "Select All")  # Add "Select All" at the beginning

        # Start with the full dataset
        filtered_data = client_data.copy()

        # Territory filter
        with territory_filters:
            territory_filter = st.selectbox(
                "Territory",
                options=territories,
                index=0,
                key="CLNTDBterritory_filter",
            )

        # Filter data based on the selected Territory
        if territory_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Territory"] == territory_filter
            ]

        # Dynamically update addresses based on filtered data
        addresses = filtered_data["Line_Address"].unique().tolist()
        addresses.insert(0, "Select All")  # Add "Select All" at the beginning

        # Address filter
        with address_filters:
            address_filter = st.selectbox(
                "Address",
                options=addresses,
                index=0,
                key="clntdb_address_filter",
            )

        # Filter data further based on Address selection
        if address_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Line_Address"] == address_filter
            ]

        # Dynamically update Workplace Types based on filtered data
        workplaceTypes = filtered_data["Workplace_Type"].unique().tolist()
        workplaceTypes.insert(0, "Select All")  # Add "Select All" at the beginning

        # Workplace Type filter
        with workplaceType_filters:
            workplaceType_filter = st.selectbox(
                "Workplace Type",
                options=workplaceTypes,
                index=0,
                key="clntdb_workplaceType_filter",
            )

        # Filter data further based on Workplace Type selection
        if workplaceType_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Workplace_Type"] == workplaceType_filter
            ]

        # Dynamically update Workplaces based on filtered data
        workplaces = filtered_data["Workplace"].unique().tolist()
        workplaces.insert(0, "Select All")  # Add "Select All" at the beginning

        # Workplace filter
        with workplace_filters:
            workplace_filter = st.selectbox(
                "Workplace",
                options=workplaces,
                index=0,
                key="clntdb_workplace_filter",
            )

        # Filter data further based on Workplace selection
        if workplace_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Workplace"] == workplace_filter
            ]

        # Filter data based on selected filters
        filtered_data = client_data
        if territory_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Territory"] == territory_filter
            ]
        else:
            territory_filter = territories[1:]
        if address_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Line_Address"] == address_filter
            ]
        else:
            address_filter = addresses[1:]

        if workplaceType_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Workplace_Type"] == workplaceType_filter
            ]
        else:
            workplaceType_filter = workplaceTypes[1:]
        if workplace_filter != "Select All":
            filtered_data = filtered_data[
                filtered_data["Workplace"] == workplace_filter
            ]
        else:
            workplace_filter = workplaces[1:]

        # Function to generate Bar Chart
        def plot_bar_chart(data, show_legend):
            data = data.sort_values(by="Count", ascending=False)
            fig = px.bar(
                data,
                x="Cadre",
                y="Count",
                color="Cadre",
                labels={"Count": "Number of Clients"},
                color_discrete_sequence=px.colors.sequential.Rainbow,
                text="Count",
            )
            fig.update_layout(
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                height=600,
                showlegend=show_legend,
            )
            # Add data labels to the bars
            fig.update_traces(
                textposition="outside",
                textfont=dict(size=12),
            )

            return fig

        # Group filtered data for visualization
        grouped_filtered_data = (
            filtered_data.groupby("Cadre").size().reset_index(name="Count")
        )

        # Create the toggle switch for showing/hiding the legend
        legend_toggle = ui.switch(
            default_checked=False,
            label="Legend",
            key="clntdblegend_toggle",
        )
        # Get the value of the legend toggle
        show_legend = legend_toggle
        # Create and display the Plotly chart
        if not grouped_filtered_data.empty:
            st.plotly_chart(
                plot_bar_chart(grouped_filtered_data, show_legend),
                use_container_width=True,
            )
        else:
            sac.result(
                label="Oops! No data available for the selected filter. Please try a different filter.",
                status="empty",
                key="lporouter_table_empty_state",
            )

    # ==============DAILY CLIENTS REPORTING===================================================================
    with st.expander(
        "Client Reporting Trend", expanded=False, icon=":material/assignment_ind:"
    ):
        # -------lAST UPDATED METRICS--------------------------------
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

        # -------------------CHARTS-----------------------------------------------
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
        # ---------------FILTERS---------------------
        resetfltrscol, brchrttggl, lgndtgl = st.columns(3)
        with resetfltrscol:

            def reset_filters():
                st.session_state.territory_filter = "Select All"
                st.session_state.yr_filter = "Select All"
                st.session_state.mnth_filter = "Select All"
                st.session_state.wk_filter = "Select All"
                st.session_state.day_filter = datetime.now().date()
                # Add a reset button

            if st.button(
                label="Reset Filters",
                on_click=reset_filters,
                icon=":material/rule_settings:",
                key="reset_admnclntdb_filters",
            ):
                pass

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

        # Create a time series plot
        def plot_time_series(data, show_legend):
            fig = px.line(
                data,
                x="Date",
                y="Count",
                color="Territory",
                color_discrete_sequence=px.colors.sequential.Rainbow,
                labels={"Date": "", "Count": "Records"},
                line_shape="spline",
            )
            fig.update_traces(mode="lines+markers")  # Add markers for better visibility
            fig.update_layout(
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                height=600,
                showlegend=show_legend,
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
                # barmode="overlay",
                text="Count",
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

        # Group filtered data for visualization
        grouped_filtered_data = (
            filtered_data.groupby(["Date", "Territory"])
            .size()
            .reset_index(name="Count")
        )
        # --------------------------------------------
        with brchrttggl:
            # Create the toggle switch using shadcn library
            chart_toggle = ui.switch(
                default_checked=False,
                label="Switch to Bar Chart",
                key="switch_visualization",
            )
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
    # ================DAILY INSTITUTION REPORTING===================================================================
    with st.expander(
        "Institution Reporting Trend", expanded=False, icon=":material/apartment:"
    ):

        def current_time():
            timezone = pytz.timezone("Africa/Nairobi")
            return datetime.now(timezone)

        def get_current_month_details():
            current_date = current_time()
            current_month = current_date.strftime("%b")
            return current_month

        def get_month_options():
            return [datetime(2024, m, 1).strftime("%b") for m in range(1, 13)]

        clients_dailyrpt_df = load_institution_data()  # Load daily clients_dailyrpt_df
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
        # ---------------FILTERS-------------------------------
        rstfltrinst, brchrttggl, lgndtgl = st.columns(3)
        with rstfltrinst:
            # reset filters
            def reset_filters():
                st.session_state.istterritory_filter = "Select All"
                st.session_state.istyr_filter = "Select All"
                st.session_state.istmnth_filter = "Select All"
                st.session_state.istwk_filter = "Select All"
                st.session_state.istdate_filter = None
                # Add a reset button

            st.button(
                "Reset Filters",
                on_click=reset_filters,
                icon=":material/rule_settings:",
                key="reset_admnistdb_filters",
            )
        # Add "Select All" at the beginning
        territories.insert(0, "Select All")
        with territory_filters:
            territory_filter = st.selectbox(
                "Territory",
                options=territories,
                index=0,
                key="istterritory_filter",
            )
        with yr_filters:
            year_options = sorted(clients_dailyrpt_df["Year"].unique())
            year_options.insert(0, "Select All")  # Add "Select All" at the beginning
            yr_filter = st.selectbox(
                "Year",
                options=year_options,
                index=0,
                key="istyr_filter",
            )
        with mnth_filters:
            month_options = get_month_options()
            month_options.insert(0, "Select All")  # Add "Select All" at the beginning
            mnth_filter = st.selectbox(
                "Month",
                options=month_options,
                index=0,
                key="istmnth_filter",
            )
        with wk_filters:
            week_options = get_week_of_month()
            week_options.insert(0, "Select All")  # Add "Select All" at the beginning
            wk_filter = st.selectbox(
                "Week",
                options=week_options,
                index=0,
                key="istwk_filter",
            )
        with day_filters:
            day_filter = st.date_input(
                "Date",
                value=None,
                # format="DD-MM-YYYY",
                key="istdate_filter",
            )
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

        # Create a time series plot
        def plot_time_series(data, show_legend):
            fig = px.line(
                data,
                x="Date",
                y="Count",
                color="Territory",
                color_discrete_sequence=px.colors.sequential.Rainbow,
                labels={"Date": "", "Count": "Records"},
                line_shape="spline",
            )
            fig.update_traces(mode="lines+markers")  # Add markers for better visibility
            fig.update_layout(
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                height=600,
                showlegend=show_legend,
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

        # Group filtered data for visualization
        grouped_filtered_data = (
            filtered_data.groupby(["Date", "Territory"])
            .size()
            .reset_index(name="Count")
        )

        with brchrttggl:
            # Create the toggle switch using shadcn library
            chart_toggle = ui.switch(
                default_checked=False,
                label="Switch to Bar Chart",
                key="istswitch_visualization",
            )
        with lgndtgl:
            # Create the toggle switch for showing/hiding the legend
            legend_toggle = ui.switch(
                default_checked=False, label="Legend", key="istlegend_toggle"
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
                key="istrouter_table_empty_state",
            )
    # ==============DEAL SIZE/LPO TRENDS===================================================================
    with st.expander(
        "Deal Size/LPO Trends",
        icon=":material/shopping_cart:",
        expanded=False,
    ):

        def current_time():
            timezone = pytz.timezone("Africa/Nairobi")
            return datetime.now(timezone)

        def get_current_month_details():
            current_date = current_time()
            current_month = current_date.strftime("%b")
            return current_month

        def get_month_options():
            return [datetime(2024, m, 1).strftime("%b") for m in range(1, 13)]

        clients_dailyrpt_df = load_institution_data()
        # clients_dailyrpt_df = clients_dailyrpt_df[
        #     clientdata["Territory"].str.strip() == territory
        # ]
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

        (
            territory_filters,
            yr_filters,
            mnth_filters,
            wk_filters,
            day_filters,
        ) = st.columns([1, 1, 1, 1, 1])
        # ---------------FILTERS-----------------------
        rstfltlpo, brchrttggl, lgndtgl = st.columns(3)
        with rstfltlpo:
            # reset filters
            def reset_filters():
                st.session_state.lpo_territory_filter = "Select All"
                st.session_state.lpoyr_filter = "Select All"
                st.session_state.lpomnth_filter = "Select All"
                st.session_state.lpowk_filter = "Select All"
                st.session_state.lpodate_filter = None
                # Add a reset button

            st.button(
                "Reset Filters",
                on_click=reset_filters,
                icon=":material/rule_settings:",
                key="reset_admnlpo_filters",
            )
        # Add "Select All" at the beginning
        territories.insert(0, "Select All")
        with territory_filters:
            territory_filter = st.selectbox(
                "Territory",
                options=territories,
                index=0,
                key="lpo_territory_filter",
            )
        with yr_filters:
            year_options = sorted(clients_dailyrpt_df["Year"].unique())
            year_options.insert(0, "Select All")  # Add "Select All" at the beginning
            yr_filter = st.selectbox(
                "Year",
                options=year_options,
                index=0,
                key="lpoyr_filter",
            )
        with mnth_filters:
            month_options = get_month_options()
            month_options.insert(0, "Select All")  # Add "Select All" at the beginning
            mnth_filter = st.selectbox(
                "Month",
                options=month_options,
                index=0,
                key="lpomnth_filter",
            )
        with wk_filters:
            week_options = get_week_of_month()
            week_options.insert(0, "Select All")  # Add "Select All" at the beginning
            wk_filter = st.selectbox(
                "Week",
                options=week_options,
                index=0,
                key="lpowk_filter",
            )
        with day_filters:
            day_filter = st.date_input(
                "Date",
                value=None,
                # format="DD-MM-YYYY",
                key="lpodate_filter",
            )
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

        # Create a time series plot
        def plot_time_series(data, show_legend):
            fig = px.line(
                data,
                x="Date",
                y="Value",
                color="LPO_Type",
                labels={
                    "Date": "Date",
                    "Value": "LPO Value",
                    "LPO_Type": "LPO Category",
                },
                color_discrete_sequence=px.colors.sequential.Rainbow,
                line_shape="spline",
            )
            fig.update_traces(mode="lines+markers")  # Add markers for better visibility
            fig.update_layout(
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                height=600,
                showlegend=show_legend,
            )
            return fig

        # Function to generate Bar Chart
        def plot_bar_chart(data, show_legend):
            fig = px.bar(
                data,
                x="Date",
                y="Value",
                color="LPO_Type",
                labels={
                    "Date": "Date",
                    "Value": "LPO Value",
                    "LPO_Type": "LPO Category",
                },
                color_discrete_sequence=px.colors.sequential.Rainbow,
                barmode="group",
            )
            fig.update_layout(
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                height=600,
                showlegend=show_legend,
            )
            # Add data labels to the bars
            fig.update_traces(
                textposition="outside",
                textfont=dict(size=12),
                text=data["Value"],
            )
            return fig

        # Group filtered data for visualization
        filtered_data = (
            filtered_data.groupby(
                [
                    "Date",
                    "Territory",
                    "LPO(A1)",
                    "LPO(A2)",
                    "TotalLPO",
                ]
            )
            .size()
            .reset_index(name="Count")
        )
        grouped_filtered_data = filtered_data.melt(
            id_vars=["Date"],
            value_vars=[
                "LPO(A1)",
                "LPO(A2)",
                "TotalLPO",
            ],  # Specify the columns to plot
            var_name="LPO_Type",
            value_name="Value",
        )
        with brchrttggl:
            # Create the toggle switch using shadcn library
            chart_toggle = ui.switch(
                default_checked=False,
                label="Switch to Bar Chart",
                key="lposwitch_visualization",
            )
        with lgndtgl:
            # Create the toggle switch for showing/hiding the legend
            legend_toggle = ui.switch(
                default_checked=False,
                label="Legend",
                key="lpolegend_toggle",
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
                key="lporouter_table_empty_state",
            )

    # ==================REFRESH BUTTON===============================================
    if refresh_button.button(
        "Refresh All",
        key="refresh_dashboard",
        use_container_width=True,
        icon=":material/autorenew:",
    ):
        st.rerun(scope="fragment")
