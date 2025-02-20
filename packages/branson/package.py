from spack.package import *
from spack.pkg.builtin.branson import Branson as BuiltinBranson

class Branson(BuiltinBranson):

    git = "https://github.com/ariel-apps/branson.git"
    variant("ariel", default=True, description="Enable Ariel API integration")
    version("develop", branch="develop", preferred=True)

    depends_on("sst-elements+ariel_mpi")

    def cmake_args(self):
        cmake_options = super().cmake_args()
        cmake_options.append(self.define_from_variant("BRANSON_WITH_ARIELAPI", "ariel"))
        return cmake_options

    #def install(self):
    #    TODO Ensure sameple input decks are installed
    #    super().install()
