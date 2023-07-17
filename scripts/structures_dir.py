"""A script for submitting a directory of stricture files to BigChem for calculation

Modify DRIVER, METHOD or BASIS as desired

Example Usage:
    poetry run python scripts/structures_dir.py ~/Downloads/my_structures/ psi4 100

This example looks in the ~/Downloads/my_structures directory and limits to the first
100 structures. It uses psi4 for the engine. If running terachem use "terachem_fe"
"""

import math
from pathlib import Path
from typing import List, Optional

from qcio import Molecule, ProgramInput

from bigchem.tasks import compute

DRIVER = "energy"  # or "gradient" or some packages support "hessian" too
METHOD = "b3lyp"  # or any method supported by your program of choice
BASIS = "6-31g"  # or any basis supported by your program of choice

if __name__ == "__main__":
    import sys

    # Get arguments from command line
    directory = Path(sys.argv[1])
    program = sys.argv[2]
    try:
        limit: Optional[int] = int(sys.argv[3])
    except IndexError:
        limit = None

    # Load molecular structures
    print(f"Using program: {program}")
    print(f"Limiting the number of structures to {limit or 'no limit'}")
    print("Loading molecular structures...")
    molecules: List[Molecule] = []
    for path in directory.iterdir():
        if len(molecules) == (limit or math.inf):
            break
        molecule = Molecule.open(path, extras={"name": str(path.stem)})
        molecules.append(molecule)

    print("Done!")

    # Submit computations to BigChem
    future_results = []
    print("Submitting computations to BigChem using...")
    for molecule in molecules:
        fr = compute.delay(
            program,
            ProgramInput(
                molecule=molecule,
                model={"method": METHOD, "basis": BASIS},
                driver=DRIVER,
            ),
        )
        print(f"Submitted {molecule.extras['name']}")
        future_results.append(fr)
    print("Done!")

    # Collect results from BigChem
    results = Path("results")
    results.mkdir(exist_ok=True)
    print(
        f"Collecting results from BigChem and writing them to {results.absolute()}..."
    )
    for fr in future_results:
        # Collect result from backend
        result = fr.get()
        # Delete result from backend
        fr.forget()
        result.save(f"{result.input_data.molecule.extras['name']}.json")
        print(f"Collected result for {result.input_data.molecule.extras['name']}")

    print("Done!")
    print(f"Your results are stored as JSON files in {results.absolute()}")
    print("Results can be opened and explored in python by running: ")
    print(">>> from qcio import SinglePointOutput")
    print(">>> output = SinglePointOutput.open('path_to_file.json')")
    print(
        "Explore results and properties at output.return_result, output.results, "
        "and output.stdout"
    )

    # This command is unnecessary. It just cleans up keep-alive connections if the
    # backend is running behind a reverse proxy.
    fr.backend.client.connection_pool.disconnect()
