from spack.package import *
from spack.pkg.builtin.branson import Branson as BuiltinBranson
from spack.util.environment import EnvironmentModifications
from pathlib import Path

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
