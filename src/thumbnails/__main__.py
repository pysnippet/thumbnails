from .cli import cli
from .generator import Generator


@cli
def main(inputs=None, **options):
    """This command delegates the functionality of the `thumbnails` Python package
    to the CLI. Read more at https://github.com/pysnippet/thumbnails#readme."""

    generator = Generator(inputs)

    for option, value in options.items():
        setattr(generator, option, value)

    generator.generate()


if __name__ == "__main__":
    main()
