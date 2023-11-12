import argparse
from pathlib import Path
from shutil import copytree

from .app import App
from .project import ProjectContext, load_project


def _create_new_project(project_dir: Path):
    template_dir = Path(__file__).parent.parent / "VXTool_template"
    copytree(template_dir, project_dir)


def _ffmpeg_movie_stitch(out_dir: Path, src_FPS: float):
    movie_FPS = 60
    img_path = str(out_dir / "frame_%05d.png")
    movie_path = str(out_dir / "movie.mp4")
    command = f"ffmpeg -framerate {src_FPS} -i {img_path} -c:v libx264 -pix_fmt yuv420p -vf scale=out_color_matrix=bt709 -r {movie_FPS} {movie_path}"  # noqa: E501
    from os import system

    system(command)


def _main():
    parser = argparse.ArgumentParser(prog="VXTool")
    parser.add_argument(
        "project_dir", type=Path, help="path specyfing project directory"
    )
    parser.add_argument(
        "-c",
        "--create",
        action="store_true",
        help="create an empty project at project_dir",
    )
    parser.add_argument(
        "-m",
        "--movie",
        action="store_true",
        help="produce a .mp4 file, composing .png files from out directory",
    )

    args = parser.parse_args()

    if args.create:
        _create_new_project(args.project_dir)
        return

    project: ProjectContext = load_project(args.project_dir)

    if args.movie:
        _ffmpeg_movie_stitch(project.config["out_dir"], project.config["FPS"])
        return

    app = App()

    app.run(project)


if __name__ == "__main__":
    _main()
