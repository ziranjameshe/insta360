from argparse import ArgumentParser
from pathlib import Path
from shutil import move

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

    total_files = len(list(args.src.iterdir()))
    for i, src_file in enumerate(args.src.iterdir()):
        if not src_file.is_file():
            assert False, f"Not expecting directory {src_file}"

        if src_file.name.startswith("."):
            raise Exception(f"Not expecting hidden file {src_file}")

        assert (
            len(src_file.stem.split("_")) == 4
        ), f"Unexpected file name format: {src_file.name}"

        date_str: str = src_file.stem.split("_")[1]
        dst_dir: Path = args.dst / date_str
        dst_dir.mkdir(exist_ok=True)
        dst_file = dst_dir / src_file.name
        if dst_file.exists():
            assert src_file.stat().st_size == dst_file.stat().st_size, (
                f"File {dst_file} already exists but sizes differ: "
                f"{src_file.stat().st_size} vs {dst_file.stat().st_size}"
            )
            print(f"File {dst_file} already exists, skipping.")
            continue

        percent = ("{0:." + str(1) + "f}").format(100 * (i / float(total_files)))
        print(f"Moving {src_file} to {dst_dir} [{percent}% Done]")
        move(src_file.as_posix(), dst_file.as_posix())
