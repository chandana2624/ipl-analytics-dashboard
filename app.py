import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =====================================================
# LOAD DATASET
# =====================================================

CSV_PATH = r"C:\Users\chand\Downloads\ball_by_ball_data.csv"

df = pd.read_csv(CSV_PATH)

df.drop_duplicates(inplace=True)

# =====================================================
# MAIN WINDOW
# =====================================================

root = tk.Tk()
root.title("IPL Analytics Dashboard")
root.geometry("1400x850")

# =====================================================
# KPI CARDS
# =====================================================

top_frame = tk.Frame(root)
top_frame.pack(fill="x", pady=10)

def create_card(parent, title, value):

    card = tk.Frame(
        parent,
        relief="ridge",
        bd=3,
        padx=20,
        pady=10
    )

    card.pack(
        side="left",
        padx=15
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 12, "bold")
    ).pack()

    tk.Label(
        card,
        text=str(value),
        font=("Arial", 18)
    ).pack()

create_card(
    top_frame,
    "Total Runs",
    int(df["total_runs"].sum())
)

create_card(
    top_frame,
    "Total Wickets",
    int(df["is_wicket"].sum())
)

create_card(
    top_frame,
    "Matches",
    int(df["match_id"].nunique())
)

create_card(
    top_frame,
    "Players",
    int(df["batter"].nunique())
)

# =====================================================
# CONTROL PANEL
# =====================================================

control_frame = tk.Frame(root)
control_frame.pack(fill="x", pady=10)

tk.Label(
    control_frame,
    text="Select Analysis:",
    font=("Arial", 11, "bold")
).pack(side="left", padx=5)

analysis_combo = ttk.Combobox(
    control_frame,
    values=[
        "Orange Cap",
        "Purple Cap",
        "Team Runs",
        "Most Sixes",
        "Most Fours"
    ],
    width=25
)

analysis_combo.current(0)
analysis_combo.pack(side="left", padx=10)

tk.Label(
    control_frame,
    text="Select Season:",
    font=("Arial", 11, "bold")
).pack(side="left", padx=5)

season_list = ["All Seasons"] + list(
    sorted(df["season_id"].unique())
)

season_combo = ttk.Combobox(
    control_frame,
    values=season_list,
    width=15
)

season_combo.current(0)
season_combo.pack(side="left", padx=10)

# =====================================================
# BUTTONS
# =====================================================

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# =====================================================
# MAIN DISPLAY AREA
# =====================================================

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

output = ScrolledText(
    main_frame,
    width=70,
    height=35,
    font=("Consolas", 10)
)

output.pack(
    side="left",
    padx=10,
    pady=10,
    fill="both"
)

chart_frame = tk.Frame(main_frame)

chart_frame.pack(
    side="right",
    fill="both",
    expand=True
)

# =====================================================
# FILTER DATA
# =====================================================

def get_filtered_df():

    selected_season = season_combo.get()

    if selected_season == "All Seasons":
        return df

    return df[
        df["season_id"] == int(selected_season)
    ]

# =====================================================
# ANALYSIS
# =====================================================

def get_analysis():

    filtered_df = get_filtered_df()

    analysis = analysis_combo.get()

    if analysis == "Orange Cap":

        result = (
            filtered_df.groupby("batter")
            ["batter_runs"]
            .sum()
            .reset_index()
            .sort_values(
                by="batter_runs",
                ascending=False
            )
        )

    elif analysis == "Purple Cap":

        result = (
            filtered_df[
                filtered_df["is_wicket"] == True
            ]
            .groupby("bowler")
            .size()
            .reset_index(name="wickets")
            .sort_values(
                by="wickets",
                ascending=False
            )
        )

    elif analysis == "Team Runs":

        result = (
            filtered_df.groupby("team_batting")
            ["total_runs"]
            .sum()
            .reset_index()
            .sort_values(
                by="total_runs",
                ascending=False
            )
        )

    elif analysis == "Most Sixes":

        result = (
            filtered_df[
                filtered_df["batter_runs"] == 6
            ]
            .groupby("batter")
            .size()
            .reset_index(name="Sixes")
            .sort_values(
                by="Sixes",
                ascending=False
            )
        )

    elif analysis == "Most Fours":

        result = (
            filtered_df[
                filtered_df["batter_runs"] == 4
            ]
            .groupby("batter")
            .size()
            .reset_index(name="Fours")
            .sort_values(
                by="Fours",
                ascending=False
            )
        )

    return result

# =====================================================
# SHOW DATA
# =====================================================

def show_data():

    result = get_analysis()

    output.delete("1.0", tk.END)

    output.insert(
        tk.END,
        f"Season Selected : {season_combo.get()}\n"
    )

    output.insert(
        tk.END,
        f"Analysis : {analysis_combo.get()}\n\n"
    )

    output.insert(
        tk.END,
        result.to_string(index=False)
    )

# =====================================================
# SHOW GRAPH
# =====================================================

def show_graph():

    for widget in chart_frame.winfo_children():
        widget.destroy()

    result = get_analysis().head(10)

    fig = Figure(
        figsize=(8, 5),
        dpi=100
    )

    ax = fig.add_subplot(111)

    x = result.iloc[:, 0]
    y = result.iloc[:, -1]

    ax.bar(x, y)

    ax.set_title(
        f"{analysis_combo.get()} ({season_combo.get()})"
    )

    ax.tick_params(
        axis="x",
        rotation=45
    )

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(
        fig,
        master=chart_frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )

# =====================================================
# SAVE CSV
# =====================================================

def save_csv():

    result = get_analysis()

    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[
            ("CSV Files", "*.csv")
        ]
    )

    if filepath:

        result.to_csv(
            filepath,
            index=False
        )

        messagebox.showinfo(
            "Success",
            "CSV File Saved Successfully"
        )

# =====================================================
# BUTTONS
# =====================================================

show_data_btn = tk.Button(
    button_frame,
    text="Show Data",
    command=show_data,
    width=18,
    font=("Arial", 11, "bold")
)

show_data_btn.grid(
    row=0,
    column=0,
    padx=10
)

show_graph_btn = tk.Button(
    button_frame,
    text="Show Graph",
    command=show_graph,
    width=18,
    font=("Arial", 11, "bold")
)

show_graph_btn.grid(
    row=0,
    column=1,
    padx=10
)

save_btn = tk.Button(
    button_frame,
    text="Save As CSV",
    command=save_csv,
    width=18,
    font=("Arial", 11, "bold")
)

save_btn.grid(
    row=0,
    column=2,
    padx=10
)

# =====================================================
# START APP
# =====================================================

root.mainloop()
