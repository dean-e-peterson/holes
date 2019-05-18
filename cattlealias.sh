# Create alias for viewing latest log file.
alias catl='cat ./log/$(ls -1 -tr ./log/ | tail -n 1)'

# Stick editor file list, ordered sensibly, in an env var for easy use.
edfs="holey.py holes/_util.py holes/_base.py holes/iterbased.py holes/bitbased.py holes/bitnumpy.py"

# Stick editor file list for testing in an env var, too.
tdfs="test/test_holes.py test/test_holes_util.py test/test_holes_base.py test/test_holes_data.py"

