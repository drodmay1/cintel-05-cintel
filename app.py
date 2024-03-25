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
ui.page_opts(title="PyShiny Express: Live Data (Basic)", fillable=True)

# Define the UI Layout Sidebar
with ui.sidebar(open="open"):
    
    ui.h2("Antarctic Explorer", class_="text-center")
    
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/drodmay1/cintel-05-cintel",
        target="_blank",
    )
    ui.a(
        "GitHub App",
        href="https://github.com/drodmay1/cintel-05-cintel/blob/main/app.py",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

# Display current temperature in the mail panel
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("snowman"),
        theme="yellow",
        style="color: black;"
    ):
        
        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        # Display message in mail panel
        "warning frio"

# Display current day and time card
with ui.card(full_screen=True):
    # Customize card header with background color, text, and icon
    ui.card_header(
        "Current Date and Time",
        style="background-color: green; color: black;",
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

with ui.card():
    ui.card_header("Chart with Current Trend")

    @render_plotly
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Create scatter plot for readings
            # pass in the df, the name of the x column, the name of the y column,
            # and more
        
            fig = px.scatter(df,
            x="timestamp",
            y="temp",
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°C)", "timestamp": "Time"},
            color_discrete_sequence=["blue"] )
            
            # Linear regression - we need to get a list of the
            # Independent variable x values (time) and the
            # Dependent variable y values (temp)
            # then, it's pretty easy using scipy.stats.linregress()

            # For x let's generate a sequence of integers from 0 to len(df)
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            # Add the regression line to the figure
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            # Update layout as needed to customize further
            fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")

        return fig
