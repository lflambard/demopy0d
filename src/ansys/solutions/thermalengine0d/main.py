# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Entry point."""

from ansys.saf.glow.runtime import glow_main

from ansys.solutions.thermalengine0d.solution import definition

from ansys.solutions.thermalengine0d.ui import app



def main():
    """Entry point."""

    glow_main(definition,  app )


if __name__ == "__main__":
    main()
