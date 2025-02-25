from spack.package import *
from spack.pkg.builtin.amg2023 import Amg2023 as BuiltinAmg2023
from spack.util.environment import EnvironmentModifications
from pathlib import Path

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

