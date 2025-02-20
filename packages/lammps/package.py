from spack.package import *
from spack.pkg.builtin.lammps import Lammps as BuiltinLammps

class Lammps(BuiltinLammps):

    git = "https://github.com/ariel-apps/lammps.git"
    variant("ariel", default=True, description="Enable Ariel API integration")
    #version("develop", branch="develop", preferred=True)

    depends_on("sst-elements")

    depends_on(
        "sst-elements+ariel_mpi",
        when="+mpi",
    )

    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("LAMMPS_WITH_ARIELAPI", "ariel"))
        return cmake_options
