from spack.package import *
from spack_repo.builtin.packages.babelstream.package import Babelstream as BuiltinBabelstream
from spack.util.environment import EnvironmentModifications
from pathlib import Path
import os
import tempfile

from spack_repo.builtin.packages.babelstream.package import CMakeBuilder as BuiltinCMakeBuilder

class Babelstream(BuiltinBabelstream):

    git = "https://github.com/ariel-apps/BabelStream.git"
    variant("ariel", default=True, description="Enable Ariel API integration")

    depends_on("sst-elements@develop+ariel_mpi")

    def setup_run_environment(self, env):
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)

    def test_native_execution_babelstream(self):
        """ Test that babelstream can run."""
        prog = which(os.path.join(self.prefix.bin, 'omp-stream'))
        out = prog('-n', '10', output=str.split, error=str.split)
        expected = "Function"
        assert expected in out, f"Expected '{expected}' in the output"
        expected = "Copy"
        assert expected in out, f"Expected '{expected}' in the output"

    def test_arielapi_babelstream(self):
        """ Test that arielapi output is present."""
        if self.spec.satisfies("~ariel"):
            raise SkipTest("Test only available if compiled with Ariel API support")
        expected = "ARIEL: ENABLE called in Ariel API."
        #prog = which(self.prefix.bin.omp-stream)
        prog = which(os.path.join(self.prefix.bin, 'omp-stream'))
        out = prog('-n', '10', output=str.split, error=str.split)
        assert expected in out, f"Expected '{expected}' in the output"

    def test_sst_babelstream(self):
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
        exe = which(os.path.join(self.prefix.bin, 'omp-stream'))
        repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # hacky, I know
        sdl = os.path.join(repo_dir, 'shared_files', 'test-ariel.py')
        out = prog(sdl, "--", "-o", outfile_name, str(exe), "--exe_args", "-n 2 -s 100", output=str.split, error=str.split)
        # Open the file and read the third line, which should have a non-zero
        # value in the seventh column
        with open(outfile_name) as of:
            line2 = of.readlines()[2]
            val = int(line2.split(',')[6])
            assert (val > 0)


class CMakeBuilder(BuiltinCMakeBuilder):
    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("ENABLE_ARIELAPI", "ariel"))

        env_mod = EnvironmentModifications()
        env_mod.set('SST_ELEMENTS_INSTALL', self.spec['sst-elements'].prefix)
        env_mod.apply_modifications()

        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        cmake_options.append("-DCMAKE_EXE_LINKER_FLAGS=-L{0}".format(sst_elements_lib))

        return cmake_options


