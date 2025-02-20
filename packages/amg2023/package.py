from spack.package import *
from spack.pkg.builtin.amg2023 import Amg2023 as BuiltinAmg2023

class Amg2023(BuiltinAmg2023):

    git = "https://github.com/ariel-apps/AMG2023.git"
    variant("ariel", default=True, description="Enable Ariel API integration")

    depends_on("sst-elements")

    depends_on(
        "sst-elements+ariel_mpi",
        when="+mpi",
    )

    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("AMG_WITH_ARIELAPI", "ariel"))
        return cmake_options
