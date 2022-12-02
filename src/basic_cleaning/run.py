#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info(f'Downloading input artifact {args.input_artifact}')
    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()
    local_path = wandb.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)

    logger.info('Cleaning data')
    # Filter price column
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info(f'Saving cleaned data to wandb as {args.output_artifact}')
    df.to_csv("clean_sample.csv", index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

    run.finish()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name of the input artifact (data file to clean) and version to get from wandb",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of output artifact (cleaned data) to save to wandb",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="The output type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="A description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price threshold",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price threshold",
        required=True
    )


    args = parser.parse_args()

    go(args)
