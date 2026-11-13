import argparse

from src.warehouse import build


def main():
    parser = argparse.ArgumentParser(
        description="Automated ETL Data Warehouse"
    )

    parser.add_argument(
        "--data-dir",
        default="../datasets"
    )

    parser.add_argument(
        "--db-path",
        default="warehouse.duckdb"
    )

    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Load only previously unseen orders"
    )

    args = parser.parse_args()

    result = build(
        args.data_dir,
        args.db_path,
        incremental=args.incremental
    )

    print(result)


if __name__ == "__main__":
    main()