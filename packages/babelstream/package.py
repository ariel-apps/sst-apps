from spack.package import *
from spack.pkg.builtin.babelstream import Babelstream as BuiltinBabelstream
from spack.util.environment import EnvironmentModifications
from pathlib import Path

from spack.pkg.builtin.babelstream import CMakeBuilder as BuiltinCMakeBuilder

class Babelstream(BuiltinBabelstream):

    git = "https://github.com/ariel-apps/BabelStream.git"
    variant("ariel", default=True, description="Enable Ariel API integration")

    depends_on("sst-elements@develop+ariel_mpi")

    def setup_run_environment(self, env):
        sst_elements_lib = Path(self.spec['sst-elements'].prefix) / 'lib' / 'sst-elements-library'
        env.prepend_path('LD_LIBRARY_PATH', sst_elements_lib)

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

