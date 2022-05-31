from math import e, log

import pandas as pd
from matplotlib.axes import Axes


def get_fuel_load(
    fuel_ss: float,
    k: float,
    p: float,
    t: int,
) -> float:
    """
    Calculates the fuel load for a given year 't' since the last fire occured.
    """
    tx = -log(1 - p) / k
    current_fuel_load = fuel_ss * (1 - e ** (-k * (t + tx)))
    return current_fuel_load


def get_fuel_loads(
    fuel_ss: float,
    k: float,
    p: float,
    no_of_years: int,
) -> pd.DataFrame:
    """
    Calculates all the fuel loads for the specified number of years.

    The result returned is a pandas.DataFrame with 'year' & 'fuel_load' columns.
    """
    # Ensure we include year zero plus the specified number of years
    years = range(no_of_years + 1)

    # Calculate all the fuel loads
    fuel_loads = [get_fuel_load(fuel_ss, k, p, i) for i in years]

    # Build the fuel load DataFrame
    fuel_load_df = pd.DataFrame(
        {
            "year": years,
            "fuel_load": fuel_loads,
        }
    )
    return fuel_load_df


def build_fuel_curve_plot(
    ax: Axes,
    fuel_load_df: pd.DataFrame,
) -> None:
    """
    Takes the the matplotlib Axes and builds the fuel curve plot given
    a pandas.DataFrame with the calculated fuel load values.

    This function also provides default behaviour for when the fuel
    loads aren't calculated yet.
    """
    if len(fuel_load_df) > 0:
        ax.plot(fuel_load_df["year"], fuel_load_df["fuel_load"])
    else:
        ax.set_xticks([])
        ax.set_yticks([])

    ax.set_title("Olson Fuel Accumulation Curve", fontsize=12)
    ax.set_ylabel("Predicted fuel load (t/ha)")
    ax.set_xlabel("Time since fire (years)")
