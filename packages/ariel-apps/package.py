# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install ariel-apps
#
# You can edit this file again by typing:
#
#     spack edit ariel-apps
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class ArielApps(BundlePackage):
    """This packkage contains all of the benchmarks that have been modified to work with libarielapi."""

    # TODO: Update this once a new page is added to sstsimulator
    homepage = "https://github.com/ariel-apps"

    maintainers("plavin")

    # FIXME: Add the SPDX identifier of the project's license below.
    license("UNKNOWN", checked_by="plavin")

    # TODO
    version("0.1.0")


    # TODO: Once verions are added, change these to remove @develop
    depends_on("amg2023@develop+mpi+ariel")
    depends_on("branson@develop+ariel")
    depends_on("lammps@develop+ariel")
    depends_on("babelstream@main+omp+ariel")
    depends_on("hpcg@develop+openmp+ariel")
