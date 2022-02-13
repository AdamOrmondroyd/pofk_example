"""
This file is an alternative to calling something like
$ python -m cobaya-run -p packages -o runs/pofk -r/-f --test etc

This exists so I can call it in debug mode in the way I know
"""

import cobaya

resume = True

## custom pofk
cobaya.run(
    "pofk.yaml",
    "packages",
    "runs/attempt_2/pofk",
    resume=resume,
    force=not resume,
    test=False,
    debug=False,
)
