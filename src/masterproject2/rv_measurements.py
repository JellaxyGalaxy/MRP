from matplotlib import pyplot as plt
from scipy.signal import lombscargle
from astroquery.simbad import Simbad
from pathlib import Path
import numpy as np
import pandas as pd
import random

from arvi import RV
import kima


def get_object_names(folder):
    """
    Description of function
    """

    file = folder / "targets.xlsx"
    df = pd.read_excel(file)

    names = df["ID"]
    n_stars = len(names)

    first_names = []

    for i in range(n_stars):
        name = names[i]

        if " / " in name:
            idx = name.index(" / ")
            name = name[:idx]

        first_names.append(name)

    return first_names



def get_coords(name):
    """
    Function description
    """

    star = simbad.query_object(name)
    coords = star["matched_id", "ra", "dec"]

    return coords



def get_rv(name):
    """
    Function description
    """

    d = RV(name, verbose=False)
    d.remove_instrument("ESPRESSO19")

    time = d.time       # timestamp of measurement in Barycentric Julian Date - 2.400.000 [days]
    rv = d.vrad         # radial velocity measurement [m/s]
    err = d.svrad       # error on radial velocity measurement [m/s]

    return d, time, rv, err

if __name__ == "__main__":

    simbad = Simbad()

    repo = Path.home() / "MRP"
    data_folder = repo / "data"

    names = get_object_names(data_folder)

    target = "TOI-2449"

    coords = get_coords(target)
    d, time, rv, err = get_rv(target)
    max_rv = np.max(rv)

    print(f"star: {target} \nra: {coords["ra"].value[0]} {coords["ra"].unit} \ndec: {coords["dec"].value[0]} {coords["dec"].unit}")
    print(f"maximum measured radial velocity: {max_rv}")

    fig, axs = d.plot()
    plt.show()  

    if max_rv < 300:
        print(f"{target} has a radial velocity that fits the presence of an exo-planet.")
    elif max_rv > 1000:
        print(f"{target} has a radial velocity that fits a binary system.")
    else:
        print(f"{target} has a radial velocity with unclear origin.")





