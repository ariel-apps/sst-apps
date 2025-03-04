import sst
import sys
import os
import argparse
import pathlib

parser = argparse.ArgumentParser(
    prog=f'sst [sst-args] test-ariel.py --',
    description='Used for testing Ariel\'s MPI features')

parser.add_argument('prog', help='Path to the binary and any arguments, enclosed in quotes')
parser.add_argument('-r', dest='ranks', default=1, help='How many ranks of the traced program to run.')
parser.add_argument('-a', dest='tracerank', default=0, help='Which of the MPI ranks will be traced.')
parser.add_argument('-t', dest='threads', default=1, help='The number of OpenMP threads to use per rank.')

args = parser.parse_args()

ncores    = int(args.threads)
mpiranks  = int(args.ranks)
tracerank = int(args.tracerank)

exe      = args.prog.split(" ")[0]
exe_args = args.prog.split(" ")[1:]

if not pathlib.Path(exe).exists():
    raise FileNotFoundError(f"Executable {exe} not found.")

print(f'test-ariel.py: Running {exe} with {mpiranks} rank(s) and {ncores} thread(s) per rank. Tracing rank {tracerank}')

os.environ['OMP_NUM_THREADS'] = str(ncores)

#########################################################################
## Declare components
#########################################################################
core    = sst.Component("core", "ariel.ariel")
cache   = [sst.Component("cache_"+str(i), "memHierarchy.Cache") for i in range(ncores)]
memctrl = sst.Component("memory", "memHierarchy.MemController")
bus     = sst.Component("bus", "memHierarchy.Bus")

#########################################################################
## Set component parameters and fill subcomponent slots
#########################################################################

# 2.4GHz cores. One for each omp thread
core.addParams({
    "clock"        : "2.4GHz",
    "verbose"      : 1,
    "executable"   : exe,
    "arielmode"    : 0, # Disable tracing at start
    "corecount"    : ncores,
    "mpimode"      : 1,
    "mpiranks"     : mpiranks,
    "mpitracerank" : tracerank,
})

if len(exe_args) > 0:
    core.addParams({"appargcount" : len(exe_args)})
    for i in range(len(exe_args)):
        core.addParams({ f"apparg{i}" : exe_args[i]})

# Cache: L1, 2.4GHz, 2KB, 4-way set associative, 64B lines, LRU replacement, MESI coherence
for i in range(ncores):
    cache[i].addParams({
        "L1" : 1,
        "cache_frequency" : "2.4GHz",
        "access_latency_cycles" : 2,
        "cache_size" : "2KiB",
        "associativity" : 4,
        "replacement_policy" : "lru",
        "coherence_policy" : "MESI",
        "cache_line_size" : 64,
    })

# Memory: 50ns access, 1GB
memctrl.addParams({
    "clock" : "1GHz",
    "backing" : "none", # We're not using real memory values, just addresses
    "addr_range_end" : 1024*1024*1024-1,
})
memory = memctrl.setSubComponent("backend", "memHierarchy.simpleMem")
memory.addParams({
    "mem_size" : "1GiB",
    "access_time" : "50ns",
})

bus.addParams({
    "bus_frequency": "2.0GHz",
})

#########################################################################
## Declare links
#########################################################################
core_cache = [sst.Link("core_to_cache_"+str(i)) for i in range(ncores)]
cache_bus  = [sst.Link("cache_" + str(i) + "_to_bus") for i in range(ncores)]
bus_mem    = sst.Link("bus_to_memory")

#########################################################################
## Connect components with the links
#########################################################################
[core_cache[i].connect( (core, "cache_link_"+str(i), "100ps"), (cache[i], "highlink", "100ps") ) for i in range(ncores)]
[cache_bus[i].connect( (cache[i], "lowlink", "100ps"), (bus, "highlink"+str(i), "100ps") ) for i in range(ncores)]
bus_mem.connect( (bus, "lowlink0", "100ps"), (memctrl, "highlink", "100ps") )

#########################################################################
## Define SST core options
#########################################################################
sst.setProgramOption("stop-at", "200ms")
sst.setStatisticOutput("sst.statoutputtxt")
sst.setStatisticOutputOptions( { "filepath"  : "stats.csv" })
sst.setStatisticLoadLevel(5)
sst.enableAllStatisticsForAllComponents()
