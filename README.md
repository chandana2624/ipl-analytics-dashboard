# IPL Analytics Dashboard

A Python-based desktop application for analyzing Indian Premier League (IPL) cricket data. This interactive dashboard provides insights, key performance indicators (KPIs), and visual representations of historical IPL match data.

## Features

- **KPI Cards**: Instantly view summary statistics like Total Runs, Total Wickets, Matches Played, and Number of Players.
- **Interactive Analysis**: Filter data by specific seasons or across all seasons.
- **Top Performers Insights**:
  - Orange Cap (Top Run Scorers)
  - Purple Cap (Top Wicket Takers)
  - Team Runs (Total Runs scored by each team)
  - Most Sixes
  - Most Fours
- **Data Visualization**: View bar charts for the top 10 results of your selected analysis directly in the app.
- **Export Capabilities**: Save the customized analysis results as a `.csv` file for external use.

## Technologies Used

- **Python**: Core programming language.
- **Tkinter**: For building the Graphical User Interface (GUI).
- **Pandas**: For data manipulation and aggregation.
- **Matplotlib**: For plotting data and rendering charts within the Tkinter window.

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/chandana2624/ipl-analytics-dashboard.git
   cd ipl-analytics-dashboard
   ```

2. **Install dependencies**:
   Make sure you have Python installed. Then, install the required packages using pip:
   ```bash
   pip install pandas matplotlib
   ```
   *Note: Tkinter is usually included with Python by default.*

3. **Data Source Setup**:
   - The script currently looks for a CSV dataset. 
   - Please update the `CSV_PATH` variable on line 14 in `app.py` to point to the correct location of your dataset.

4. **Run the Application**:
   ```bash
   python app.py
   ```
