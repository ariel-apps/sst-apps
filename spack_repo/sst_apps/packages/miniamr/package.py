from spack.package import *
from spack_repo.builtin.packages.miniamr.package import Miniamr as BuiltinMiniamr
from spack.util.environment import EnvironmentModifications
from pathlib import Path
import tempfile
import os

class Miniamr(BuiltinMiniamr):

    git = "https://github.com/ariel-apps/miniAMR.git"
    variant("ariel", default=True, description="Enable Ariel API integration")

    depends_on("sst-elements@develop")
    depends_on("omp", when="backend=openmp")

    depends_on(
        "sst-elements+ariel_mpi",
    )

    variant(
        "build",
        default="ref",
        values=["ref", "openmp"],
        description="Whether to build the reference or OpenMP version",
    )

    # Custom build targets so we can choose the OpenMP version
    @property
    def build_targets(self):
        targets = []
        targets.append('ENABLE_ARIELAPI=true')
        targets.append(f"CC={self.spec['mpi'].mpicc}")
        targets.append(f"LD={self.spec['mpi'].mpicc}")
        targets.append("LDLIBS=-lm")

        if self.spec.satisfies("build=ref"):
            targets.append("--directory=ref")
        else:
            targets.append("--directory=openmp")

        if self.spec.satisfies("+ariel"):
            targets.append('ENABLE_ARIEL=true')
            targets.append('LDLIBS=-lm -larielapi')
            targets.append('LDFLAGS=-fopenmp')

        return targets



    # Custom install method so we can choose the OpenMP version
    def install(self, spec, prefix):
        # Manual installation
        mkdir(prefix.bin)
        mkdir(prefix.docs)

        if spec.satisfies("@1.6.4:"):
            if spec.satisfies("build=ref"):
                install("ref/miniAMR.x", prefix.bin)
            else:
                install("openmp/miniAMR.x", prefix.bin)
        else:
            install("ref/ma.x", prefix.bin)

        # Install Support Documents
        install("ref/README", prefix.docs)


    #TODO
    # SST_ELEMENTS_INSTALL
    # MINIAMR_WITH_ARIELAPI
    # Linker flags
    # loader flags
    # Test cases
    # Variants - DONE


#    def cmake_args(self):
#        cmake_options = super().cmake_args()
#        cmake_options.append(self.define_from_variant("AMG_WITH_ARIELAPI", "ariel"))
#
#        env_mod = EnvironmentModifications()
#        env_mod.set('SST_ELEMENTS_INSTALL', self.spec['sst-elements'].prefix)
#        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
#        env_mod.apply_modifications()
#
#        cmake_options.append("-DCMAKE_EXE_LINKER_FLAGS=-L{0}".format(sst_elements_lib))
#        return cmake_options
#
#    def setup_run_environment(self, env):
#        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
#        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)
#
#    def test_native_execution_amg2023(self):
#        """ Test that amg can run."""
#        expected = "FOM_Solve:"
#        prog = which(self.prefix.bin.amg)
#        out = prog(output=str.split, error=str.split)
#        assert expected in out, f"Expected '{expected}' in the output"
#
#    def test_arielapi_amg2023(self):
#        """ Test that arielapi output is present."""
#        if self.spec.satisfies("~ariel"):
#            raise SkipTest("Test only available if compiled with Ariel API support")
#        expected = "ARIEL: ENABLE called in Ariel API."
#        prog = which(self.prefix.bin.amg)
#        out = prog(output=str.split, error=str.split)
#        assert expected in out, f"Expected '{expected}' in the output"
#
#    def test_sst_amg2023(self):
#        """ Test that the app can run in Ariel."""
#        if self.spec.satisfies("~ariel"):
#            raise SkipTest("Test only available if compiled with Ariel API support")
#
#        # Pick a name for the output file
#        outfile = tempfile.NamedTemporaryFile(
#            dir=self.test_suite.stage,
#            suffix=".csv",
#            delete=False)
#        outfile_name = outfile.name
#        outfile.close()
#
#        print(f"Outputting stats to file: {outfile_name}")
#        prog = which(self.spec['sst-core'].prefix.bin.sst)
#        exe = which(self.prefix.bin.amg)
#        repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # hacky, I know
#        sdl = os.path.join(repo_dir, 'shared_files', 'test-ariel.py')
#        out = prog(sdl, "--", str(exe), "-o", outfile_name, output=str.split, error=str.split)
#        # Open the file and read the third line, which should have a non-zero
#        # value in the seventh column
#        with open(outfile_name) as of:
#            line2 = of.readlines()[2]
#            val = int(line2.split(',')[6])
#            assert (val > 0)

