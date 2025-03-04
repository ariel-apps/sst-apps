# SST-Spack

This repository contains Spack packages that build benchmarks that
are compatibile with [SST Elements](https://github.com/sstsimulator/sst-elements).
These benchmarks have been forked to add this support.
Currently, the only supported element is [Ariel](http://sst-simulator.org/sst-docs/docs/elements/ariel/intro).
We hope to suport other elements in the future, such as Vanadis and Mercury.

## Benchmarks
The following benchmarks are included:
- AMG2023
- BabelStream
- Branson
- HPCG
- LAMMPS

## Installing this repo
1. Install [Spack](https://spack-tutorial.readthedocs.io/en/latest/tutorial_basics.html)
2. Set up the spack environment `source ~/spack/share/spack/setup-env.sh`
3. Clone this repo `git clone git@github.com:ariel-apps/sst-spack.git`
4. Add this repo: `spack repo add sst-spack`

## Installing Benchmarks
After adding the repo it will be at the start of Spack's search path.
You can now install any of the supported benchmarks using `spack install`..
To see a list of included benchmarks, use the `spack list` command
```bash
$ spack list -r sst-spack
amg2023  ariel-apps  babelstream  branson  hpcg  lammps
==> 6 packages
$ spack install amg2023
```

If you want to ensure you are getting the right version of a benchmark
(i.e. the ariel-apps version and not the builtin verion), you can either prefix
the package name with the repo name, e.g. `spack install sst-spack.amg2023`, or you
can explicity enable the ariel variant, with `spack install amg2023+ariel`.

For your convience, you can install all of the benchmarks with the bundle package named `ariel-apps`.
```bash
spack install ariel-apps
```

## Running Benchmarks
To get access to the binaries and any associated input files and required libraries,
you need to use `spack load`. You can either load individual benchmarks, or
use the bundle package to load them all onto your `PATH`.
```bash
$ spack load ariel-apps
$ which amg
~/spack/opt/spack/linux-rocky8-skylake_avx512/gcc-12.2.0/amg2023-develop-zslus327ekd7hrr57jls4sirsklyauiz/bin/amg
```

Use `spack unload` to undo this.


## Notes
- All packages in this repo are derived from packages in the base repo, referred to as `builtin.`, with one execption, `HPCG`. We were unable to override the environment variables in our dervied packge so we were forced to copy the entire file to make changes. Otherwise, we tried to change as little as possible.
- Currently, the packages require the `develop` branch of sst-elements. Once SST 15.0 is released, we can pin to that version.
- The packages also require the `develop` branches of the code they are

## TODOs
- [ ] Once SST 15.0 is released, change the dependencies in the packages to that, instead of `develop`.
- [ ] Create releases for all of the forked benchmarks.
- [ ] Document where to find the Branson and LAMMPS input decks.
- [ ] Check that `spack load` has the right behavior when ~ariel is set.
