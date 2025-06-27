from spack.package import *
from spack.pkg.builtin.lammps import Lammps as BuiltinLammps
from spack.util.environment import EnvironmentModifications
from pathlib import Path
import os
#import tempfile

class Lammps(BuiltinLammps):

    git = "https://github.com/ariel-apps/lammps.git"
    variant("ariel", default=True, description="Enable Ariel API integration")

    depends_on("sst-elements@develop")

    depends_on(
        "sst-elements+ariel_mpi",
        when="+mpi",
    )

    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("LAMMPS_WITH_ARIELAPI", "ariel"))
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        cmake_options.append("-DCMAKE_EXE_LINKER_FLAGS=-L{0}".format(sst_elements_lib))
        return cmake_options

    def setup_build_environment(self, env):
        env.set('SST_ELEMENTS_INSTALL', self.spec['sst-elements'].prefix)
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)

    def setup_run_environment(self, env):
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)
        env.set('LAMMPS_EXAMPLES', str(Path(self.prefix) / 'examples'))

    @run_after("install")
    def install_examples(self):
        install_tree(str(Path(self.stage.source_path) / 'examples'), str(Path(prefix) / 'examples'))

    def test_basic(self):
        assert True
    def _test_native_execution_lammps(self):
        """ Test that amg can run."""
        expected = "Ave neighs/atom"
        prog = which(self.prefix.bin.lmp)
        input_dir = os.getenv("LAMMPS_EXAMPLES")
        input_file = os.path.join(input_dir, "grid", "in.grid.2d")
        out = prog("-in", input_file, output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def _test_arielapi_branson(self):
        """ Test that arielapi output is present."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")
        expected = "ARIEL: ENABLE called in Ariel API."
        prog = which(self.prefix.bin.lmp)
        input_dir = os.getenv("LAMMPS_EXAMPLES")
        input_file = os.path.join(input_dir, "grid", "in.grid.2d")
        out = prog("-in", input_file, output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

