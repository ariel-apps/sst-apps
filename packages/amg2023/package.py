from spack.package import *
from spack.pkg.builtin.amg2023 import Amg2023 as BuiltinAmg2023
from spack.util.environment import EnvironmentModifications
from pathlib import Path
import tempfile
import os

class Amg2023(BuiltinAmg2023):

    git = "https://github.com/ariel-apps/AMG2023.git"
    variant("ariel", default=True, description="Enable Ariel API integration")

    depends_on("sst-elements@develop")

    depends_on(
        "sst-elements+ariel_mpi",
        when="+mpi",
    )

    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("AMG_WITH_ARIELAPI", "ariel"))

        env_mod = EnvironmentModifications()
        env_mod.set('SST_ELEMENTS_INSTALL', self.spec['sst-elements'].prefix)
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env_mod.apply_modifications()

        cmake_options.append("-DCMAKE_EXE_LINKER_FLAGS=-L{0}".format(sst_elements_lib))
        return cmake_options

    def setup_run_environment(self, env):
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)

    def test_native_execution_amg2023(self):
        """ Test that amg can run."""
        expected = "FOM_Solve:"
        prog = which(self.prefix.bin.amg)
        out = prog(output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def test_arielapi_amg2023(self):
        """ Test that arielapi output is present."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")
        expected = "ARIEL: ENABLE called in Ariel API."
        prog = which(self.prefix.bin.amg)
        out = prog(output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def test_sst_amg2023(self):
        """ Test that the app can run in Ariel."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")

        # Don't need file open...
        outfile = tempfile.NamedTemporaryFile(
            dir=self.test_suite.stage,
            suffix=".csv",
            delete=False)
        outfile_name = outfile.name
        outfile.close()

        print(f"Outputting stats to file: {outfile_name}")
        prog = which(self.spec['sst-core'].prefix.bin.sst)
        exe = which(self.prefix.bin.amg)
        repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # hacky, I know
        sdl = os.path.join(repo_dir, 'shared_files', 'test-ariel.py')
        out = prog(sdl, "--", str(exe), "-o", outfile_name, output=str.split, error=str.split)
        # Open the file and read the third line, which should have a non-zero
        # value in the seventh column
        with open(outfile_name) as of:
            line2 = of.readlines()[2]
            val = int(line2.split(',')[6])
            assert (val > 0)

