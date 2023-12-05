/*globals Application*/

/*jslint indent: 4*/



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function procReaction() {

    "use strict";

    var procFileName, spec = Application.nmr.activeSpectrum();

    if (!spec.isValid()) {

        return;

    }

    if (spec.dimCount === 1) {

        if (spec.nucleus() === "1H") {

            procFileName = "C:/Users/Platform/code/RoboChem_auto-optimization-platform/Platform_/NMR_control_loop/processing_files/example.mnp";

        } else if (spec.nucleus() === "19F") {

            procFileName = "C:/Users/Platform/code/RoboChem_auto-optimization-platform/Platform_/NMR_control_loop/processing_files/example.mnp";

        } else if (spec.nucleus() === "13C") {

            procFileName = "c:/mnova/13C.mnp";

        }

        if (procFileName) {

            Application.nmr.processSpectrum(spec, procFileName);

        }

    } else if (spec.dimCount === 2) {

        if (spec.nucleus(1) === "1H" && spec.nucleus(2) === "1H") {

            procFileName = "c:/mnova/COSY.mnp";

        }

        if (procFileName) {

            Application.nmr.processSpectrum(spec, procFileName);

        }

    }

}

/*globals Application, File, TextStream*/

/*jslint indent: 4, plusplus: true*/

function dumpAbsoluteReaction() {

    "use strict";

    //To get the active spectrum

    var spec = Application.nmr.activeSpectrum();

    var intList = new Integrals(spec.integrals());

    var myInt = new Integral(intList.at(0));

    var dumpFile = new File("C:/Users/Platform/code/RoboChem_auto-optimization-platform/Platform_/NMR_control_loop/processing_files/last_integral.txt");

    //The function isValid informs about if the spectrum obtained is correct

    if (spec.isValid()) {

        //print("Spectrum valid")

        if (dumpFile.open(File.WriteOnly)) {

            //(print("dump file IS open"))

            var dumpStream = new TextStream(dumpFile);

            try {

                //To dump the spectrum information

                dumpStream.writeln(myInt.integralValue());

            } finally {

                dumpFile.close();

                //print("Here end")

            }

        } //else (print("dump file not open"))

    }

}


function ProcessReaction() {

    procReaction();
    dumpAbsoluteReaction();

}
