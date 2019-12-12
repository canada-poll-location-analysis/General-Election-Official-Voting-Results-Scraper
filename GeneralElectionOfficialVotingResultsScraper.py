import logging
import os

import pandas as pd
import wget as wget
from tqdm import tqdm

from sean_logger import setup_logging
from toolbox import make_directory


def scrape_election_results(prov_id=35, base_url=None, results_format=1):
    setup_logging()
    if results_format == 1:
        results_format = "pollbypoll_bureauparbureau"
    elif results_format == 2:
        results_format = "pollresults_resultatsbureau"
    if base_url is None:
        base_url = "https://www.elections.ca/res/rep/off/ovr2015app/41/data_donnees/"
    num_except_in_a_row = 0
    exceptions = []
    for fed_num in tqdm(range(prov_id * 1000, ((prov_id + 1) * 1000) - 1)):
        logging.info(f"fed num {fed_num}")
        try:
            url = f"{base_url}{results_format}{fed_num}.csv"
            outfile = f"./data_donnees/{results_format}{fed_num}.csv"
            logging.debug(url)
            logging.debug(outfile)
            make_directory(outfile)
            wget.download(url, outfile)
            num_except_in_a_row = 0
        except:
            logging.exception(f"Exception!! {fed_num}")
            exceptions.append(fed_num)
            num_except_in_a_row += 1
        if num_except_in_a_row > 10:
            logging.info(f"Probably finished at {fed_num - num_except_in_a_row}")
            break
    logging.info(f"Missed FED Nums:")
    for fed in exceptions:
        logging.info(fed)
    logging.info()
    print('fin')


def combine_result_csvs(folder=None, cols=None):
    if folder is None:
        folder = "./data_donnees/"
    files = os.listdir(folder)
    if cols is None:
        cols = "Electoral District Number/Numéro de circonscription," \
               "Electoral District Name/Nom de circonscription," \
               "Polling Station Number/Numéro du bureau de scrutin," \
               "Polling Station Name/Nom du bureau de scrutin," \
               "Rejected Ballots/Bulletins rejetés," \
               "Total Votes/Total des votes," \
               "Electors/Électeurs".split(',')
    print("Reading...")
    frames = [pd.read_csv(folder + file, usecols=cols) for file in tqdm(files)]
    print("Combining...")
    data = pd.concat(frames)
    print("Writing...")
    data.to_csv("turnout_data_ontario_42nd_federal.csv", index=False)
    print("Fin.")


if __name__ == '__main__':
    scrape_election_results()
    combine_result_csvs()
