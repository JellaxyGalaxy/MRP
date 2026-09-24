from matplotlib import pyplot as plt
from scipy.signal import lombscargle
from astroquery.simbad import Simbad
from pathlib import Path
from tqdm import tqdm
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



def get_simbad(names):
    """
    Function description
    """

    if isinstance(names, str):
        names = [names]

    names_list = ", ".join(f"'{n}'" for n in names)
    query = f"""
    SELECT ident.id AS matched_id, basic.main_id, basic.ra, basic.dec
    FROM basic
    JOIN ident ON ident.oidref = basic.oid
    WHERE ident.id IN ({names_list})
    """
    table = simbad.query_tap(query)

    found = set(table["matched_id"])
    missing = [n for n in names if n not in found]

    # print(f"Found {len(found)} / {len(names)} names")
    # if missing:
    #     print(f"{len(missing)} stars missing: \n{missing}")

    return table

# function that prints simbad information


def get_rv(name):
    """
    Function description
    """

    try:
        d = RV(name, verbose=False)
    except Exception as e:
        print(f"{name}: no observation ({e})")
        return None, None, None, None

    # d.remove_instrument("ESPRESSO19")

    time = d.time       # timestamp of measurement in Barycentric Julian Date - 2.400.000 [days]
    rv = d.vrad         # radial velocity measurement [m/s]
    err = d.svrad       # error on radial velocity measurement [m/s]

    return d, time, rv, err



def periodogram(time, vrad, freq=np.linspace(0.001, 1, 1000)):

    period = 2 * np.pi / freq
    pgram = lombscargle(time, vrad, freq, normalize=True)

    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.plot(period, pgram)
    ax.set_xscale("log")
    ax.set_xlabel("Period [days]")
    ax.set_ylabel("Normalized power")
    plt.show()

if __name__ == "__main__":

    simbad = Simbad()

    repo = Path.home() / "MRP"
    data_folder = repo / "data"

    # SIMBAD QUERY
    # target_names = get_object_names(data_folder)
    # simbad_table = get_coords(target_names)
    # print(simbad_table)

    target_names = "TOI-2449"

    for name in tqdm(target_names):
        target = name #"TOI-2449"

        coords_table = get_simbad(target)
        d, time, rv, err = get_rv(target)
        if d is None:
            continue

        # print(f"star: {target}")
        # print(f"simbad main ID: {coords_table['main_id'].value[0]}")
        # print(f"ra: {coords_table['ra'].value[0]} {coords_table['ra'].unit}")
        # print(f"dec: {coords_table['dec'].value[0]} {coords_table['dec'].unit}")

        fig, axs = d.plot()
        plt.show()  

        periodogram(time=time, vrad=rv)








