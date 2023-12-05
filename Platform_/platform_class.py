"""
Aidan Slattery, Zhenghui Wen, Pauline Tenblad, Diego Pintossi
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)


Script to control the entire platform and perform auto-optimization of chemical
reactions.

1. Connection to all the hardware and logging setup
2. Function wrapping single experiment in one function
3. Input of experimental parameter space
4. Loop of experiments determined by Bayesian Optimimzation (initialization +
    exploration till optimal value is attained)

Hardware:
- Acrylate box enclosing all the liquid handling (N2 atmosphere and suction)
- Logilink USB hubs (2x)
- Syringe pumps (Chemyx Fusion Series)
- Motorized switch valves (3-way [2x], 4-way [2x] from Runze fluid)
- Arduino UNO [x8]
- 24V power source (Mean Well LRS-150-24)
- 12V power source
- 5V DC relay modules [x4]
- Bronkhorst MFC
- TT electronics OCB350 phase sensor [x7]
- Gilson GX-241 liquid handler with syringe pump and injection module
- Eagle reactor from Signify (variable volume, 6x high-power LEDs)
- Flow NMR (Magritek Spinsolve 60)

"""

from Syringe_pumps.Syringe_pump import SyringePump
from Switch_valves.Switch_valves_control_Arduino_sketch import SwitchValveArduino
from MFC_control.MFC_control import BronkhorstMFC


class Platform(object):
    # class opening all serial connections
    def __init__(self,
                 syringe_pump_a=None,
                 syringe_pump_b=None,
                 syringe_pump_c=None,
                 switch_valves=None,
                 mfc=None,
                 export_freq=0.5
                 ):
        """ Platform_ initialization establishing a serial connection to all
        elements (except liquid handler and flow NMR, which are handled by
        a .dll and software, respectively).

        :param syringe_pump_a: dict
            Dictionary containing the information to connect to syringe_pump_a
            {'port': the name of the port,
             'baudrate': the baudrate (38400 for USB connection),
             'name': name to be used for the logging files
             }
        :param syringe_pump_b: dict
            Dictionary containing the information to connect to syringe_pump_b
            {'port': the name of the port,
             'baudrate': the baudrate (38400 for USB connection),
             'name': name to be used for the logging files
             }
        :param syringe_pump_c: dict
            Dictionary containing the information to connect to syringe_pump_c
            {'port': the name of the port,
             'baudrate': the baudrate (38400 for USB connection),
             'name': name to be used for the logging files
             }
        :param switch_valves: dict
            Dictionary containing all information to connect to the Arduino UNO
            controlling all switch valves
            {'port': the name of the port
            'pins': list with the digital pin numbers where the relays are
                    connected
            'name': name to be used for the logging files
            'valve types': list with the valve type corresponding to each
                           digital pin from 'pins'
            }
        :param mfc: dict
            Dictionary containing all information to connect to the mass flow
            controller
            {'port': the name of the port
             }
        """
        self.syringe_pump_a = SyringePump(
            syringe_pump_a['port'],
            syringe_pump_a['baudrate'],
            syringe_pump_a['name'],
            mode=0,
            x=0,
        )
        self.syringe_pump_b = SyringePump(
            syringe_pump_b['port'],
            syringe_pump_b['baudrate'],
            syringe_pump_b['name'],
            mode=0,
            x=0,
        )
        self.syringe_pump_c = SyringePump(
            syringe_pump_c['port'],
            syringe_pump_c['baudrate'],
            syringe_pump_c['name'],
            mode=0,
            x=0,
        )
        self.switch_valves = SwitchValveArduino(
            switch_valves['port'],
            switch_valves['name'],
            switch_valves['pins'],
            switch_valves['valve types'],
        )
        self.mfc = BronkhorstMFC(mfc['port'])
