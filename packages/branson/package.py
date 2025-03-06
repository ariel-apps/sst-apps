from spack.package import *
from spack.pkg.builtin.branson import Branson as BuiltinBranson
from spack.util.environment import EnvironmentModifications
from pathlib import Path
import tempfile
import os

class Branson(BuiltinBranson):

    git = "https://github.com/ariel-apps/branson.git"
    variant("ariel", default=True, description="Enable Ariel API integration")
    version("develop", branch="develop", preferred=True)

    depends_on("sst-elements+ariel_mpi@develop")

    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("BRANSON_WITH_ARIELAPI", "ariel"))

        env_mod = EnvironmentModifications()
        env_mod.set('SST_ELEMENTS_INSTALL', self.spec['sst-elements'].prefix)
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env_mod.apply_modifications()

        cmake_options.append("-DCMAKE_EXE_LINKER_FLAGS=-L{0}".format(sst_elements_lib))

        return cmake_options

    def install(self, spec, prefix):
        super().install(spec, prefix)
        install_tree(str(Path(self.stage.source_path) / 'inputs'), str(Path(prefix) / 'inputs'))

    def setup_run_environment(self, env):
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)
        env.set('BRANSON_INPUTS', str(Path(self.prefix) / 'inputs'))

    def test_native_execution_branson(self):
        """ Test that amg can run."""
        expected = "Photons Per Second (FOM):"
        prog = which(self.prefix.bin.BRANSON)
        input_dir = os.getenv("BRANSON_INPUTS")
        input_file = os.path.join(input_dir, "marshak_wave_dd.xml")
        out = prog(input_file, output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def test_arielapi_branson(self):
        """ Test that arielapi output is present."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")
        expected = "ARIEL: ENABLE called in Ariel API."
        prog = which(self.prefix.bin.BRANSON)
        input_dir = os.getenv("BRANSON_INPUTS")
        input_file = os.path.join(input_dir, "marshak_wave_dd.xml")
        out = prog(input_file, output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def test_sst_branson(self):
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

        exe = which(self.prefix.bin.BRANSON)
        input_dir = os.getenv("BRANSON_INPUTS")
        input_file = os.path.join(input_dir, "marshak_wave_dd.xml")

        repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # hacky, I know
        sdl = os.path.join(repo_dir, 'shared_files', 'test-ariel.py')

        out = prog(sdl, "--", "-o", outfile_name, str(exe), "--exe_args", input_file, output=str.split, error=str.split)
        # Open the file and read the third line, which should have a non-zero
        # value in the seventh column
        with open(outfile_name) as of:
            line2 = of.readlines()[2]
            val = int(line2.split(',')[6])
            assert (val > 0)

