import argparse
import os
import sys

import docplex.cp.utils_visu as visu
from docplex.cp.model import CpoModel


# -----------------------------------------------------------------------------
# Initialize the problem data
# -----------------------------------------------------------------------------
# Read the input data file.
# Available files are jobshop_ft06, jobshop_ft10 and jobshop_ft20
# First line contains the number of jobs, and the number of machines.
# The rest of the file consists of one line per job.
# Each line contains list of operations, each one given by 2 numbers: machine and duration

def get_args(argv):
    parser = argparse.ArgumentParser()
    # Required arguments.
    parser.add_argument(
        "--instance_name",
        default="ft06",
        help="Input video file.", )
    return parser.parse_args()


args = get_args(sys.argv)
file_name = args.instance_name
path_file = os.path.dirname(os.path.abspath(os.getcwd())) + "/JSPLIB/instances/" + file_name

JOBS = []
NB_JOBS, NB_MACHINES = 0, 0

with open(path_file, "r") as file_name:
    # NB_JOBS, NB_MACHINES = [int(v) for v in file.readline().split()]
    # JOBS = [[int(v) for v in file.readline().split()] for i in range(NB_JOBS)]
    lines = file_name.readlines()
    for line in lines:
        if line.rfind('#') == -1:
            print(line)
            if NB_JOBS == 0 and NB_MACHINES == 0:
                NB_JOBS, NB_MACHINES = [int(str) for str in line.split()]
            else:
                JOBS.append([int(v) for v in line.split()])

# -----------------------------------------------------------------------------
# Prepare the data for modeling
# -----------------------------------------------------------------------------

# Build list of machines. MACHINES[j][s] = id of the machine for the operation s of the job j
MACHINES = [[JOBS[j][2 * s] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]

# Build list of durations. DURATION[j][s] = duration of the operation s of the job j
DURATION = [[JOBS[j][2 * s + 1] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]

# -----------------------------------------------------------------------------
# Build the model
# -----------------------------------------------------------------------------

# Create model
mdl = CpoModel()

# Create one interval variable per job operation
job_operations = [[mdl.interval_var(size=DURATION[j][m], name="O{}-{}".format(j, m)) for m in range(NB_MACHINES)] for j
                  in range(NB_JOBS)]

# Each operation must start after the end of the previous
for j in range(NB_JOBS):
    for s in range(1, NB_MACHINES):
        mdl.add(mdl.end_before_start(job_operations[j][s - 1], job_operations[j][s]))

# Force no overlap for operations executed on a same machine
machine_operations = [[] for m in range(NB_MACHINES)]
for j in range(NB_JOBS):
    for s in range(0, NB_MACHINES):
        machine_operations[MACHINES[j][s]].append(job_operations[j][s])
for lops in machine_operations:
    mdl.add(mdl.no_overlap(lops))

# Minimize termination date
mdl.add(mdl.minimize(mdl.max([mdl.end_of(job_operations[i][NB_MACHINES - 1]) for i in range(NB_JOBS)])))

# -----------------------------------------------------------------------------
# Solve the model and display the result
# -----------------------------------------------------------------------------

# Solve model
print("Resolution...")
msol = mdl.solve(TimeLimit=15)
print("Solution : ")
msol.print_solution()

# Draw solution
if msol and visu.is_visu_enabled():
    visu.timeline("Solution pour le fichier  " + path_file)
    visu.panel("Jobs")
    for i in range(NB_JOBS):
        visu.sequence(name='J' + str(i),
                      intervals=[
                          (msol.get_var_solution(job_operations[i][j]), MACHINES[i][j], 'M' + str(MACHINES[i][j])) for j
                          in
                          range(NB_MACHINES)])
    visu.panel("Machines")
    for k in range(NB_MACHINES):
        visu.sequence(name='M' + str(k),
                      intervals=[(msol.get_var_solution(machine_operations[k][i]), k, 'J' + str(i)) for i in
                                 range(NB_JOBS)])
    visu.show()
