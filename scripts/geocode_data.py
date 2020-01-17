#!/usr/bin/env python

"""
Geocode addresses in data in a CSV file using the Census Batch Geocoder.

Usage:

    geocode_data.py data_with_addresses.csv 'output/data__geocoded__{:04d}.csv'

Assumptions:

- Pandas package installed.
- Census Batch Geocoder package installed. See https://github.com/datadesk/python-censusbatchgeocoder

Caveats:

- This assumes your data can have duplicate addresses and therefore extracts
  and geocodes the addresses. You'll have to merge them back into your source
  data after geocoding.

"""

import argparse
import logging
import math

import censusbatchgeocoder
import numpy as np
import pandas as pd


# This is how many chunks the Census batch geocoder can handle at a time.
CENSUS_BATCH_GEOCODER_CHUNK_SIZE = 10_000


def format_addresses(addresses):
    """Format addresses so they match the expected format of the geocoder API"""

    # TODO: Edit this to match any transformations that need to be done for your
    # particular data.
    # The addresses need to have these columns:
    # - address
    # - city
    # - state
    # - zipcode
    return addresses\
        .assign(
            address=lambda df: df['addr_number'].str.cat(df['address_line1'], sep=' ')
        )\
        .drop(['addr_number', 'address_line1'], axis=1)\
        .rename(columns={'zip': 'zipcode'})\
        .assign(
            id=lambda df: df.index,
        )\
        [['id', 'address', 'city', 'state', 'zipcode']]\
        .reset_index(drop=True)

def prepare_addresses_for_geocoding(data):
    """Extract and format addrsses for geocoding."""
    
    removals = pd.read_feather(args.removals)

    # Edit this to match the names of the columns in your data
    addr_cols = ['addr_number', 'address_line1', 'city', 'state', 'zip']

    return data[addr_cols]\
        .drop_duplicates()\
        .pipe(format_addresses)

def generate_chunk_path_fn(pattern):
    """
    Returns a function that will return a path to an output chunk given a
    chunk number.

    This function is suitable for passing as the argument to
    `census_batch_geocoder_geocode_chunk_and_save`.

    """
    return lambda chunk_num: pattern.format(chunk_num)

def census_batch_geocoder_geocode_chunk(chunk):
    """Geocode a set of addresses in a DataFrame using the Census Batch Geocoder"""
    result = censusbatchgeocoder.geocode(chunk.to_dict("records"))

    return pd.DataFrame(result)

def census_batch_geocoder_geocode_chunk_and_save(chunk, chunk_number, filename_fn):
    """
    Geocode a set of addresses in a DataFrame using Census Batch Geocoder and save
    output to a CSV file.

    Returns:
        Path of saved file.

    """
    output_path = filename_fn(chunk_number)
    if os.path.exists(output_path):
        logging.warning(
            (
                "Output path `%s` already exists for chunk %s. Skipping "
                "geocoding for this chunk."
            ),
            output_path,
            chunk_number
        )
        return output_path

    geocoded = census_batch_geocoder_geocode_chunk(chunk)

    geocoded.to_csv(output_path, index=False)

    logging.info(
        "Saved geocoded output of chunk %s to `%s`.",
        chunk_number,
        output_path
    )

    return output_path

def parse_args():
    """Define and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Geocode addresses in data in a CSV file using the Census Batch Geocoder."
        )
    )

    parser.add_argument(
        'data',
        help="Path to CSVS file containing addresses."
    )
    parser.add_argument(
        'output_pattern',
        help=(
            "Prefix of CSV files that will be used to make filenames "
            "for each geocoded chunk."
        )
    )

    return parser.parse_args()

def geoocode_data():
    """Geocode addresses in data in a CSV file using the Census Batch Geocoder."""
    args = parse_args()

    data = pd.read_csv(args.data)

    addresses = prepare_addresses_for_geocoding(data)

    # Split addresses into batches
    n_chunks = math.ceil(addresses.shape[0] / CENSUS_BATCH_GEOCODER_CHUNK_SIZE)

    addresses_chunks = np.array_split(addresses, n_chunks)

    output_filename_fn = generate_chunk_path_fn(args.output_pattern)

    for i, chunk in enumerate(addresses_chunks):
        census_batch_geocoder_geocode_chunk_and_save(
            chunk,
            i,
            output_filename_fn
        )


if __name__ == '__main__':
    geoocode_data()
