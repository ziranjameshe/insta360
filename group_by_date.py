from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from subprocess import run


def bash_move(src: Path, dst: Path) -> None:
    run(f"cp {src.as_posix()} '{dst.as_posix()}'", shell=True, check=True)
    run(f"rm {src.as_posix()}", shell=True, check=True)


def process_file(iter: int, src_file: Path, dst_path: Path, total_files: int) -> None:
    date_str: str = src_file.stem.split("_")[1]
    dst_dir = dst_path / date_str
    dst_file = dst_dir / src_file.name

    if dst_file.exists():
        assert src_file.stat().st_size == dst_file.stat().st_size, (
            f"File {dst_file} already exists but sizes differ: "
            f"{src_file.stat().st_size} vs {dst_file.stat().st_size}"
        )
        print(f"File {dst_file} already exists, skipping.")
        return

    percent = ("{0:." + str(1) + "f}").format(100 * (iter / float(total_files)))
    print(f"Moving {src_file} to {dst_dir} [{percent}% Done]")

    bash_move(src_file, dst_file)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--src",
        type=Path,
        default=Path("/Volumes/Untitled/DCIM/Camera01/"),
        help="Path to the input files.",
    )
    parser.add_argument(
        "--dst",
        type=Path,
        required=True,
        help="Path to the output directory.",
    )

    args = parser.parse_args()
    assert args.src.is_dir(), f"Source path {args.src} is not a directory."
    assert args.dst.is_dir(), f"Destination path {args.dst} is not a directory."

    src_files = list(args.src.iterdir())
    total_files = len(src_files)

    for i, src_file in enumerate(src_files):
        if not src_file.is_file():
            raise AssertionError(f"Not expecting directory {src_file}")
        if src_file.name.startswith("."):
            raise Exception(f"Not expecting hidden file {src_file}")

        assert (
            len(src_file.stem.split("_")) == 4
        ), f"Unexpected file name format: {src_file.name}"

        date_str: str = src_file.stem.split("_")[1]
        dst_dir = args.dst / date_str
        dst_dir.mkdir(exist_ok=True)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(process_file, i, src_file, args.dst, total_files)
            for i, src_file in enumerate(src_files)
        ]

        # Surface exceptions cleanly
        for future in as_completed(futures):
            future.result()
