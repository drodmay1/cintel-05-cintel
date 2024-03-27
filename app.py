# Import libraries
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from ipyleaflet import Map
from shinywidgets import render_widget

# import icons
from faicons import icon_svg

# Set a constant UPDATE INTERVAL for all live data
UPDATE_INTERVAL_SECS: int = 5

# Initialize reactive value, wrapper around deque
DEQUE_SIZE: int = 4
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Initialize reactive calculation
@reactive.calc()
def reactive_calc_combined():

    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between -18 and -16 C, rounded to 1 decimal place
    temp = round(random.uniform(-18, -16), 1)

    # Get a timestamp for "now"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # Get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple everything we need
    return deque_snapshot, df, latest_dictionary_entry
    
# Define the Shiny UI Page layout, set the title
ui.page_opts(title="PyShiny Express: Penguin Climate Monitoring", fillable=True)

# Display icon and title in the main panel
with ui.layout_columns():
    with ui.value_box(
        title="❅ Penguin Climate Monitoring Dashboard",
        showcase=icon_svg("snowman"),
        theme="yellow",
        style="color: black;",
        value="",
    ):
        pass

# Define the UI Layout Sidebar with background color
with ui.sidebar(open="open", style="background-color: lightblue; font-family: 'Comic Sans MS', cursive;"):
    
    # Header with two lines
    with ui.h2(class_="text-center"):
        ui.div("Penguin Climate", style="font-size: 1.0em;"),
        ui.div("Monitoring Dashboard", style="font-size: 1.0em;")

    # Add an icon with custom size using CSS
    ui.div(
    icon_svg("snowflake"),
    class_="text-center", 
    style="color: blue; font-size: 100px",
    )
    
    # Description
    ui.p(
        "Real-time temperature readings in Antarctica for penguin habitat monitoring.",
        class_="text-center",
    )
    ui.hr() # Horizontal line for visual separation
    
    # Links section
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/drodmay1/cintel-05-cintel",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "GitHub App",
        href="https://github.com/drodmay1/cintel-05-cintel/blob/main/app.py",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "PyShiny", 
        href="https://shiny.posit.co/py/", 
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )

# Display current temperature in the main panel
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("snowflake"),
        theme="yellow",
        style="color: black;"
    ):
        
        "❅ Current Temperature ❅"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        # Display message in main panel
        "❄️ Penguin Habitat Temperature ❄️"

# Display current day and time card
with ui.card(full_screen=True):
    # Customize card header with background color, text, and icon
    ui.card_header(
        "📅 Current Date and Time",
        style="background-color: blue; color: white;",
    )

    # Customize card content text color
    @render.text
    def display_time():
        """Get the latest reading and return a timestamp string"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        return f"{latest_dictionary_entry['timestamp']}"

    # Add icon
    icon_svg("clock")

# Display more recent readings card
with ui.card(full_screen=True):
    # Customize card header
    ui.card_header("📚 Most Recent Readings", style="background-color: blue; color: white;")

    # Define custom card content using layout columns
    with ui.layout_columns():
        with ui.card():
            ui.card_header("🌡️ Temperature Readings", style="background-color: #d1ecf1; color: black;")
            ui.p("Below are the most recent temperature readings:")

        # Display the DataFrame
        with ui.card():
            ui.card_header("📊 Readings Data Table", style="background-color: #d1ecf1; color: black;")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")

# Display the chart with current trend
with ui.card():
    ui.card_header("Chart with Current Trend")

    # Initialize an empty figure
    fig = px.line(title="Temperature Trend Over Time", labels={"temp": "Temperature (°C)", "timestamp": "Time"})

    @render_plotly
    def display_plot():
        # Fetch data from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before updating the plot
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Add trace for temperature data
            fig.add_scatter(x=df["timestamp"], y=df["temp"], mode="lines", name="Temperature")

            # Configure animation settings
            fig.update_layout(updatemenus=[dict(type="buttons", showactive=False, buttons=[dict(label="Play", method="animate", args=[None, {"fromcurrent": True}]),])])

            # Update layout as needed to customize further
            fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")

        return fig

ui.h2("Antarctica Map")


@render_widget
def map():
    return Map(center=(-70, -50), zoom=1
              )
