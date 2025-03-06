from spack.package import *
from spack.pkg.builtin.hpcg import Hpcg as BuiltinHpcg
from spack.util.environment import EnvironmentModifications
from pathlib import Path
import os
import platform
import tempfile
import spack

class Hpcg(AutotoolsPackage):

    homepage = "https://www.hpcg-benchmark.org"
    git = "https://github.com/ariel-apps/hpcg.git"
    variant("ariel", default=True, description="Enable Ariel API integration")
    variant("openmp", default=True, description="Enable OpenMP support")

    version("develop", branch="master")

    depends_on("cxx", type="build")  # generated
    depends_on("sst-elements@develop+ariel_mpi")
    depends_on("mpi@1.1:")

    arch = "{0}-{1}".format(platform.system(), platform.processor())
    build_targets = ["arch={0}".format(arch)]


    def configure(self, spec, prefix):
        CXXFLAGS = "-O3 -ffast-math -ftree-vectorize "
        if (
            not spec.satisfies("%aocc")
            and not spec.satisfies("%cce")
            and not spec.satisfies("%arm")
            and not spec.satisfies("%intel")
            and not spec.satisfies("%oneapi")
            and not spec.satisfies("%clang")
        ):
            CXXFLAGS += " -ftree-vectorizer-verbose=0 "
        if spec.satisfies("%cce"):
            CXXFLAGS += " -Rpass=loop-vectorize"
            CXXFLAGS += " -Rpass-missed=loop-vectorize"
            CXXFLAGS += " -Rpass-analysis=loop-vectorize "
        if self.spec.satisfies("+openmp"):
            CXXFLAGS += self.compiler.openmp_flag
        if self.spec.satisfies("+ariel"):
            sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
            ariel_include = Path(self.spec['sst-elements'].prefix) / 'include' / 'sst' / 'elements' / 'ariel' / 'api'
            CXXFLAGS += f" -I{ariel_include} -L{sst_elements_lib} -larielapi -DUSE_ARIELAPI"
        config = [
            # Shell
            "SHELL         = /bin/sh",
            "CD            = cd",
            "CP            = cp",
            "LN_S          = ln -fs",
            "MKDIR         = mkdir -p",
            "RM            = /bin/rm -f",
            "TOUCH         = touch",
            # Platform identifier
            "ARCH          = {0}".format(self.arch),
            # HPCG Directory Structure / HPCG library
            "TOPdir        = {0}".format(os.getcwd()),
            "SRCdir        = $(TOPdir)/src",
            "INCdir        = $(TOPdir)/src",
            "BINdir        = $(TOPdir)/bin",
            # Message Passing library (MPI)
            "MPinc         = -I{0}".format(spec["mpi"].prefix.include),
            "MPlib         = -L{0}".format(spec["mpi"].prefix.lib),
            # HPCG includes / libraries / specifics
            "HPCG_INCLUDES = -I$(INCdir) -I$(INCdir)/$(arch) $(MPinc)",
            "HPCG_LIBS     =",
            "HPCG_OPTS     =",
            "HPCG_DEFS     = $(HPCG_OPTS) $(HPCG_INCLUDES)",
            # Compilers / linkers - Optimization flags
            "CXX           = {0}".format(spec["mpi"].mpicxx),
            "CXXFLAGS      = $(HPCG_DEFS) {0}".format(CXXFLAGS),
            "LINKER        = $(CXX)",
            "LINKFLAGS     = $(CXXFLAGS)",
            "ARCHIVER      = ar",
            "ARFLAGS       = r",
            "RANLIB        = echo",
        ]

        # Write configuration options to include file
        with open("setup/Make.{0}".format(self.arch), "w") as makefile:
            for var in config:
                makefile.write("{0}\n".format(var))
    def patch(self):
        pass

    def setup_run_environment(self, env):
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)

    def install(self, spec, prefix):
        # Manual installation
        install_tree("bin", prefix.bin)

    def test_native_execution_hpcg(self):
        """ Test that hpcg can run."""

        outfile = tempfile.NamedTemporaryFile(
            dir=self.test_suite.stage,
            suffix=".csv",
            delete=False)
        outfile_name = outfile.name
        outfile.close()

        env = spack.util.environment.EnvironmentModifications()
        env.set('HPCG_OUT', outfile_name)
        env.apply_modifications()

        prog = which(self.prefix.bin.xhpcg)
        out = prog(output=str.split, error=str.split)

        with open(outfile_name) as of:
            expected = "Final Summary::HPCG result is VALID with a GFLOP/s"
            assert expected in of.readlines()[-9], f"Expected '{expected}' in the output"

    def test_arielapi_hpcg(self):
        """ Test that arielapi output is present."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")
        expected = "ARIEL: ENABLE called in Ariel API."
        prog = which(self.prefix.bin.xhpcg)
        out = prog(output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def test_sst_hpcg(self):
        """ Test that the app can run in Ariel."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")

        # Pick a name for the output file
        outfile = tempfile.NamedTemporaryFile(
            dir=self.test_suite.stage,
            suffix=".csv",
            delete=False)
        outfile_name = outfile.name
        outfile.close()

        print(f"Outputting stats to file: {outfile_name}")
        prog = which(self.spec['sst-core'].prefix.bin.sst)
        exe = which(self.prefix.bin.xhpcg)
        repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # hacky, I know
        sdl = os.path.join(repo_dir, 'shared_files', 'test-ariel.py')
        out = prog(sdl, "--", str(exe), "-o", outfile_name, output=str.split, error=str.split)
        # Open the file and read the third line, which should have a non-zero
        # value in the seventh column
        with open(outfile_name) as of:
            line2 = of.readlines()[2]
            val = int(line2.split(',')[6])
            assert (val > 0)


