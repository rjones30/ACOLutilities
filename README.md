# ACOLutilities - tools for calibration and analysis of data from the GlueX active collimator

## Authors

* Richard Jones, University of Connecticut, Storrs, CT

## Description

The GlueX active collimator consists of eight 60-degree sectors of tungsten modules called wedges arranged in two concentric rings around a central collimator aperture. The purpose of this device is to measure the azimuthal and radial distribution of the photon beam that strikes the collimator, while letting the central part of the beam pass through the collimator unimpeded. The tungesten wedges are built as individual base plates with a dense array of vertical pins out perpendicular to the plate, aligned with the collimator axis. Photons that interact in the tungsten plate send a shower of e+/e- particles through the pin array, some of which have large-angle collisions with electrons in the metal. These so-called knock-on electrons exit the tungsten and pass downstream into the primary collimator, where they stop. The current generated by these knock-on electrons is proportional to the total photon flxu striking each wedge. These currents are amplified using high-gain preamplifiers, digitized using a flash adc, and recorded. The tools in this repository have been constructed to facilitate the analysis of these data, and the extraction of information about the photon beam, such as its total intensity and its spatial moments.

## History

This library was developed for use with the active collimator developed and built for the GlueX experiment by the University of Connecticut.  It was packaged into a repository because it may also be useful for running bias calibrations at Jefferson Lab.

## Release history

Initial release on March 31, 2018.

## Usage synopsis

To see the usage synopsis for any of the utilities listed above under Description, invoke it with the option "--help".

## Dependencies

To use this package, you must have the ROOT package from CERN installed on the Linux host. It should work on any flavor of Linux, not tested on Windows or Mac, but if the pcap library is installed then it should be straight-forward to modify the Makefile for building on those platforms. One of the tools also relies on having mdautils, a package for conducting and analyzing EPICS scans, installed on the local host.

## Building instructions

Currently there is nothing to build, as the tools are written in python. If I do add C++ tools at some point, simply cd to the top-level project directory and type "make".

## Documentation

Just this README.

## Troubleshooting

You are on your own here, but a good place to start in case of problems would be to read the comments in the TAGMcontroller.h and TAGMcontroller.cc source files. This is the best documentation that exists on the ethernet protocol supported by the controller firmware.

## Bugs

Please report to the author richard.t.jones at uconn.edu in case of problems.

## How to contribute

Addition of a high-level EPICS gui designed in a similar fashion to the other EPICS gui's in use by GlueX would be much appreciated.

## Contact the authors

Contact the author richard.t.jones at uconn.edu for more information.
