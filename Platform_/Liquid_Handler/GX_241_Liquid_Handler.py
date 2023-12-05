"""
:mod.:"GX_241_class" -- API for GX-241 Liquid handler control
==============================
  module:: GX_241_class
   :platform: Windows
   :synopsis: Control GX-241 Liquid handler
  module_author:: Zhenghui Wen, Diego Pintossi, Aidan Slattery

(c) 2021 Noel Research Group, University of Amsterdam

This provides a python class for controlling the GX-241 liquid handler
over a local network. Command implementation is based on the manual
"LT375050-02 Commands List GX-241 Rel 2.pdf".
"""

# system imports
import sys
sys.path.append('C:\\Users\\Platform\\code\\RoboChem_auto-optimization-platform\\Platform_')
import pandas as pd
import ctypes
from ctypes import *
import asyncio
import numpy as np
from phase_sensor_CSV_naming import get_your_abs_project_path
from Logging_organizer.Logging_Setting import setup_logger
# from Sample_info import SampleInfo
import time


class LiquidHandler(object):
    """
    API for interfacing with the Gilson GX-241 liquid handler.
    Args:
        name (str): Optional name of the liquid handler modules
    """
    def __init__(self, name=""):
        self.name = name
        self.device_type = "GX-241"
        self.logger = setup_logger('LiquidHandler_logger', 'LiquidHandler.log')

        self.coordinate = pd.read_excel(
            get_your_abs_project_path()
            + '/Liquid_Handler/XYZ_Values.xlsx',
            engine='openpyxl'
        )

        self.coordinate_value_338S = self.coordinate.iloc[6:22, 1:5]
        self.coordinate_value_335S = self.coordinate.iloc[6:18, 6:10]

        self.GX_241_current_error = [0, 0, 0]
        self.XYZ_coordinate = [0.0, 0.0, 122.0]  # home position
        self.X_travel_range = 162  # Unit is mm.
        self.Y_travel_range = 263
        self.Z_travel_range = 125  # It is dependent on the clamp height.
        self.XY_speed_range = 350  # Unit is mm/sec
        self.Z_speed_range = 150
        # TODO set speed for X, Y, and Z as attributes to avoid hardcoding
        self.current_volume = 0
        # Maximum volume of each sample,
        # [sub_A, sub_B, cat, additive(optional), co_cat]
        self.sample_volume = np.array([4.0, 4.0, 4.0, 4.0, 4.0])
        self.sample_bottle = np.array([0, 0, 0, 0, 0])
        # self.sample_info = SampleInfo()

    def get_dll_version(self):
        try:
            # load the Gsioc32.dll and function
            lib = windll.gsioc32
            # interface -> void GetDllVersion(char* rsp, int maxrsp)
            getdllver = lib.GetDllVersion
            # setup the parameters
            rsp = ctypes.create_string_buffer(256)
            rsplen = ctypes.c_int(256)
            # execute the call into the Gsioc32.dll
            getdllver(rsp, rsplen)
            # return the response
            return rsp.value
        except OSError as ex:
            return "Error"

    # -----------------------------------------------------------------------
    # Returns the result of an immediate command
    #   unit_id is the unit id of the instrument (0..63)
    #   command is the command string to send to the instrument
    def immediate(self, unit_id, command):
        try:
            # load the Gsioc32.dll and function
            lib = windll.LoadLibrary(r'C:\Users\Platform\code\RoboChem_auto-optimization-platform\Platform_\Liquid_Handler\Gsioc32.dll')
            # interface ->
            # int ICmd(int unit, char const* cmd, char* rsp, int maxrsp)
            icmd = lib.ICmd
            # setup the parameters
            rsp = ctypes.create_string_buffer(256)
            rsplen = ctypes.c_int(256)
            # execute the call into the Gsioc32.dll
            icmd(unit_id, command, rsp, rsplen)
            # return the response
            return rsp.value
        except Exception as e:
            print(f'Error with reset: {e}')
            time.sleep(5)
            pass
    # -----------------------------------------------------------------------
    # Returns the result of a buffered command
    #   unit_id is the unit id of the instrument (0..63)
    #   command is the command string to send to the instrument

    def buffered(self, unit_id, command):
        try:
            # load the Gsioc32.dll and function
            lib = windll.gsioc32
            # interface ->
            # int BCmd(int unit, char const* cmd, char* rsp, int maxrsp)
            bcmd = lib.BCmd
            # setup the parameters
            rsp = ctypes.create_string_buffer(256)
            rsplen = ctypes.c_int(256)
            # execute the call into the Gsioc32.dll
            bcmd(unit_id, command, rsp, rsplen)
            # return the response
            return rsp.value
        except OSError as ex:
            return "Error"

    def request_module_identification(self):
        """
        Sending immediate command "%" to the instrument to request the module
        identifications.

        :return:
            character string:
            "GX-241 II va.b.c.d" for liquid handler;
            "GX Syringe Pump va.b.c.d" for syringe pump;
            "GX D Inject vx.y.z" for Direct Injection module.
        """
        liquid_handler_identification = self.immediate(35, '%')
        syringe_pump_identification = self.immediate(7, '%')
        direct_injection_module_identification = self.immediate(9, '%')
        self.logger.debug(
            f"The version of GX-241 is {liquid_handler_identification}."
            + f"The version of syringe pump is {syringe_pump_identification}."
            + "The version of direct injection module "
            + f"is {direct_injection_module_identification}"
        )

    def reset(self):
        """Reset liquid handler.

        :return:
            Character string '$'.
        """
        time.sleep(1)
        liquid_handler_reset = self.immediate(35, '$')
        print('LH Reset: Successful')
        time.sleep(1)
        self.clear_error()
        syringe_pump_reset = self.immediate(7, '$')

        time.sleep(1)
        direct_injection_module_reset = self.immediate(9, '$')

        self.logger.debug(
            f"The response of GX-241 is {liquid_handler_reset}."
            + f"The response of syringe pump is {syringe_pump_reset}."
            + "The response of direct injection module "
            + f"is {direct_injection_module_reset}"
        )

    async def home(self):
        """Homes liquid handler, syringe pump and direct injection module.

        """
        liquid_handler_home = self.buffered(35, 'H')
        await asyncio.sleep(10)

        syringe_pump_home = self.buffered(7, 'p')
        await asyncio.sleep(15)

        direct_injection_module_home = await self.switch_valve_position('VI')

        await asyncio.sleep(5)
        if liquid_handler_home == bytes('.', encoding='utf8') \
                and syringe_pump_home == bytes('.', encoding='utf8') \
                and direct_injection_module_home == bytes('.', encoding='utf8'):
            self.read_XY_coordinate()
            self.read_Z_coordinate()
            await asyncio.sleep(1)
            valve_position, self.current_volume = \
                self.read_syringe_pump_status()
            injection_valve_position = self.read_valve_status()
            if self.XYZ_coordinate == [0.0, 0.0, 122.0] \
                    and valve_position == 'N' \
                    and self.current_volume == 0 \
                    and injection_valve_position == 'I':
                self.logger.debug("The liquid handler is successfully homed.")
            else:
                await self.move_Z(122.0)
                await self.move_XY(0.0, 0.0)
        else:
            self.logger.debug(
                "There is a problem with homing. "
                + "The responses of liquid handler, syringe pump and "
                + f"direct injection module are {liquid_handler_home}, "
                + f"{syringe_pump_home} and {direct_injection_module_home}."
            )

    async def Gilson_identification(self):
        """Function to identify, reset and home the Gilson liquid handler.
        """
        self.request_module_identification()

        await asyncio.sleep(5)
        self.reset()

        await asyncio.sleep(5)
        await self.home()


    def get_error(self):
        """Get the current error number ans

        :return:
            The current error number and descriptive text.
            (e.g., '10, Unknown Command').
        """
        # liquid_handler_current_error
        liquid_handler_current_error = self.immediate(35, 'e')
        # syringe_pump_current_error
        syringe_pump_current_error = self.immediate(7, 'e')
        # direct_injection_module_current_error
        direct_injection_module_current_error = self.immediate(9, 'e')
        self.logger.error(
            "The current error of GX-241 is"
            + f" {liquid_handler_current_error}."
            + "The current error of syringe pump is "
            + f"{syringe_pump_current_error}."
            + "The current error of direct injection module is "
            + f"{direct_injection_module_current_error}."
        )

    def clear_error(self):
        """Clear the error number

        :return:
            self.GX_241_error
        """
        self.GX_241_current_error[0] = self.buffered(35, 'e')
        self.GX_241_current_error[1] = self.buffered(7, 'e')
        self.GX_241_current_error[2] = self.buffered(9, 'e')
        self.logger.info(
            "The error of GX-241 is cleared. "
            + f"The error number is {self.GX_241_current_error}."
        )

    def read_XYZ_coordinate(self):
        """Reads XYZ coordinates for the location of the arm.
        (THIS IS NOT ACCURATE!!!)

        :return:
            self.XYZ_coordinates
        """
        read_coordinate_response = self.immediate(35, 'P')
        self.XYZ_coordinate[0] = \
            read_coordinate_response.decode('utf-8').split('/')[0]
        self.XYZ_coordinate[1] = \
            read_coordinate_response.decode('utf-8').split('/')[1]
        self.XYZ_coordinate[2] = \
            read_coordinate_response.decode('utf-8').split('/')[2]
        return self.XYZ_coordinate

    def read_XY_coordinate(self):
        """Reads X and Y positions.

        :return:
            "xxx.xx/yyy.yy" where:
        xxx.xx is the X position in mm, with a resolution of 0.01 mm
        yyy.yy is the Y position in mm, with a resolution of 0.01 mm.
        """
        read_XY_coordinate_response = self.immediate(35, 'X')
        self.XYZ_coordinate[0] = float(
            read_XY_coordinate_response.decode('utf-8').split('/')[0])
        self.XYZ_coordinate[1] = float(
            read_XY_coordinate_response.decode('utf-8').split('/')[1])
        self.logger.debug(
            f"X position: {self.XYZ_coordinate[0]}; "
            + f"Y position: {self.XYZ_coordinate[1]}"
        )
        return self.XYZ_coordinate

    def read_Z_coordinate(self):
        """Read Z position

        :return:
            "zzz.zz", which is the Z height in mm
            (with a resolution of 0.01 mm) above the reference surface.
        """
        read_Z_coordinate_response = self.immediate(35, 'Z')
        self.XYZ_coordinate[2] = float(
            read_Z_coordinate_response.decode('utf-8')
        )
        self.logger.debug(f"Z position: {self.XYZ_coordinate[2]}.")
        return self.XYZ_coordinate

    async def move_XY(self, px, py):
        """Move the arm to the target XY position with the default
        speed 300 mm/sec and default drive level (100%).

        :param px:
            the target X position
        :param py:
            the target Y position
        """
        self.clear_error()
        if px < self.X_travel_range and py < self.Y_travel_range:
            self.XYZ_coordinate[0] = px
            self.XYZ_coordinate[1] = py
            Move_XY_command = bytes(
                "X " + str(px) + ":300:100/" + str(py)
                + ":300:100", encoding='utf-8'
            )
            Move_XY_response = self.buffered(35, Move_XY_command)
            current_XY_coordinate = self.read_XY_coordinate()
            await asyncio.sleep(
                (abs(px-current_XY_coordinate[0])
                 + abs(py-current_XY_coordinate[1])) / 300 + 1
            )
            self.logger.debug(
                f"Moving XY position is {Move_XY_response}. "
                + f"The new XY coordinate is X:{self.XYZ_coordinate[0]}, "
                + f"Y:{self.XYZ_coordinate[1]}."
            )
        else:
            self.logger.warning(
                "The XY axis target are out of range. "
                "Please fill in the right range X:[0-162], Y:[0-263] mm."
            )
        return self.XYZ_coordinate

    async def move_XY_with_speed_and_drive(self, px, py, sx=300, dx=100,
                                           sy=300, dy=100):
        """Move the arm to the target XY position with the different speeds
        and drive levels.

        :param px:
            The target X position
        :param sx:
            (Optional) the speed for X-axis.
        :param dx:
            (Optional) the drive level for X-axis.
        :param py:
            The target Y position
        :param sy:
            (Optional) the speed for Y-axis.
        :param dy:
            (Optional) the drive level for Y-axis.
        The default speed is 300 mm/sec.
        The maximum speed is 350 mm/sec.
        If speeds are not specified, the defaults will be used.
        If drive levels are not specified, the default (100%) will be used.
        """
        if px < self.X_travel_range and py < self.Y_travel_range:
            if sx < self.XY_speed_range and sy < self.XY_speed_range:
                self.XYZ_coordinate[0] = px
                self.XYZ_coordinate[1] = py
                Move_XY_command = bytes(
                    'X' + str(px) + ':' + str(sx) + ':' + str(dx)
                    + '/' + str(py) + ':' + str(sy) + ':'
                    + str(dy), encoding='utf-8'
                )
                Move_XY_response = self.buffered(35, Move_XY_command)
                await asyncio.sleep(px / sx + py / sy)
                self.logger.debug(
                    "Moving XY position with speed and drive "
                    + f"level is {Move_XY_response}. The new XY coordinate "
                    + f"is X:{self.XYZ_coordinate[0]}, "
                    + f"Y:{self.XYZ_coordinate[1]}."
                )
            else:
                self.logger.warning(
                    "The speed for XY axis is out of range. "
                    + "Please fill in the right range XY:[0-350] mm/sec."
                )
        else:
            self.logger.warning(
                "The XY axis target are out of range. Please fill in the "
                "right range X:[0-162], Y:[0-263] mm."
            )
        return self.XYZ_coordinate

    async def move_Z(self, pz, sz=40, dz=100):
        """Move the Z axis to the new position with different speed and
        drive level.

        :param pz:
            The target Z position
        :param sz:
            (Optional) the speed for Z axis
        :param dz:
            (Optional) the drive level (percent) for Z axis
        The default speed is 125 mm/sec.
        The maximum speed is 150 mm/sec.
        If the speed is not specified, the default will be used.
        If a drive level is not specified, the default(100%) will be used.
        """
        self.clear_error()
        if pz < self.Z_travel_range:
            if sz < self.Z_speed_range:
                self.XYZ_coordinate[2] = pz
                Move_Z_command = bytes(
                    'Z' + str(pz) + ':' + str(sz)
                    + ':' + str(dz), encoding='utf-8'
                )
                Move_Z_response = self.buffered(35, Move_Z_command)
                await asyncio.sleep(1)
                self.logger.debug(
                    f"Moving Z position is {Move_Z_response}. "
                    f"The new Z coordinate is Z:{self.XYZ_coordinate[2]}."
                )
            else:
                self.logger.warning(
                    "The speed for Z axis is out of range. Please fill in "
                    "the right range Z:[0-150] mm/sec."
                )
        else:
            self.logger.warning(
                "The Z axis target are out of range. "
                "Please fill in the right range Z:[0-122]."
            )
        return self.XYZ_coordinate

    async def move_Z_with_liquid_level_detection(self, pz, sz=40, dz=100):
        """Move the Z axis to the new position with different speed and
        drive level, and also with liquid level detection.

        :param pz:
            The target Z position
        :param sz:
            (Optional) the speed for Z axis
        :param dz:
            (Optional) the drive level (percent) for Z axis
        The default speed is 125 mm/sec.
        The maximum speed is 150 mm/sec.
        If the speed is not specified, the default will be used.
        If a drive level is not specified, the default(100%) will be used.
        If liquid is encountered (on a downward movement) or air is encountered
        (on an upward movement) the movement stops immediately.
        After movement stops, the position at which liquid (or air) was found
        can be read using the immediate Z command.
        If the position is the same as the target specified,
        it may be assumed that liquid (or air) was not encountered.
        """
        if pz < self.Z_travel_range:
            if sz < self.Z_speed_range:
                self.XYZ_coordinate[2] = pz
                Move_Z_command = bytes(
                    'Z' + str(pz) + ':' + str(sz)
                    + ':' + str(dz), encoding='utf-8'
                )
                Move_Z_response = self.buffered(35, Move_Z_command)
                await asyncio.sleep(pz / sz)
                self.logger.debug(
                    f"Moving Z position is {Move_Z_response}. "
                    + f"The new Z coordinate is Z:{self.XYZ_coordinate[2]}."
                )
            else:
                self.logger.warning(
                    "The speed for Z axis is out of range. "
                    + "Please fill in the right range Z: [0-150] mm/sec."
                )
        else:
            self.logger.warning(
                "The Z axis target are out of range. "
                + "Please fill in the right range Z:[0-122]."
            )
        return self.XYZ_coordinate

    def read_syringe_info(self):
        """Read the syringe information

        :return:
            Syringe size, minimum flow rate, maximum flow rate and default
        flow rate
        """
        syringe_info = self.immediate(7, 'F')
        self.logger.debug(
            f"The syringe information is shown as following: {syringe_info}."
        )

    def read_motor_status(self):
        """Read motor status

        :return:
            'ab', where:
            a = valve motor status;
                E for Error,
                R for Running (or Homing),
                U for Unpowered (also Unhomed),
                P for Parked;
            b = syringe motor status;
                E for Error,
                R for Running (or Homing),
                U for Unpowered (also Unhomed),
                P for Parked.
        """
        motor_status = self.immediate(7, 'M')
        valve_motor_status = list(motor_status.decode('utf-8'))[0]
        syringe_motor_status = list(motor_status.decode('utf-8'))[1]
        self.logger.debug(
            f"The valve_motor status is {valve_motor_status} "
            + f"and the syringe_motor_status is {syringe_motor_status}."
        )
        return list(motor_status.decode('utf-8'))

    async def stop_syringe_pump(self):
        """ Stop the syringe pump and read syringe pump status

        """
        stop_syringe_pump = self.buffered(7, 'PX')
        await asyncio.sleep(0.05)
        valve_position, current_volume = self.read_syringe_pump_status()
        self.logger.debug(
            f"The response of stopping pump is {stop_syringe_pump}. "
            + f"The pump is stopped. The valve position is {valve_position} "
            + f"and the current volume inside the syringe "
            + f"is {current_volume} μL."
        )

    def read_syringe_pump_status(self):
        """ Read syringe pump status

        :return:
            “nv.vvv” where:
            n = valve position;
                N if for needle (probe) position,
                R if in reservoir position;
            v.vvv - Current volume in μL in syringe or if unknown (unhomed),
                returns ?
        """
        syringe_pump_status = self.immediate(7, 'P')
        syringe_pump_status_list = syringe_pump_status.decode(
            'utf-8').split(':')
        valve_position = syringe_pump_status_list[0]
        if str('?') in syringe_pump_status_list:
            self.logger.debug(
                "the syringe pump is unknown or unhomed. "
                + "Please home the syringe pump."
            )
        else:
            self.current_volume = syringe_pump_status_list[1]
            self.logger.debug(f"The valve position is {valve_position}"
                              f" and the current volume in microliter "
                              f"in syringe is {self.current_volume}.")
        return valve_position, self.current_volume

    async def switch_valve_position(self, position):
        """Switches the direct injection valve position

        :param position:
            'VI' for inject position; 'VL' for Load position
        """
        switch_valve_position_command = bytes(position, encoding='utf-8')
        valve_position_response = self.buffered(
            9, switch_valve_position_command
        )
        await asyncio.sleep(0.5)
        valve_status = self.read_valve_status()
        self.logger.debug(
            f"The response of switching valve is {valve_position_response}. "
            + f"The valve is switched to {position} and "
            + f"the status is {valve_status}"
        )

    def read_valve_status(self):
        """Read valve_status

        :return:
            R for Moving
            L for Load position
            I for Inject position
        """
        injection_valve_position = self.immediate(9, 'X').decode('utf-8')
        self.logger.debug(
            f"The injection valve position is {injection_valve_position}."
        )
        return injection_valve_position

    async def set_syringe_pump(self, valve_position, volume, flow_rate=1.0):
        """Sets syringe pump parameters

        :param valve_position:
            'N' for needle (probe) position, 'R' for reservoir position
        :param volume:
            Volume (in microliters) to aspirate (+) or dispense (-)
        :param flow_rate:
            (Optional) flow rate in mL/min. If flow rate is not specified,
            the default flow rate for the selected syringe will be used.
        Use read_motor_status() to obtain that information.
        Example: Use buffered PN:-500:2 to dispense 500 μL at 2 mL/min to the
                    needle (probe).
                 Use buffered PR:2500:5 to aspirate 2500 μL (2.5 mL) at
                    5 mL/min from the reservoir.
        """
        self.valve_position, self.current_volume = \
            self.read_syringe_pump_status()
        # if sum(int(self.current_volume), volume) < 100:
        syringe_pump_parameters = bytes(
            'P' + str(valve_position) + ':' + str(volume)
            + ':' + str(flow_rate), encoding='utf-8'
        )
        syringe_pump_response = self.buffered(7, syringe_pump_parameters)
        if volume < 0:
            volume *= -1
        else:
            pass
        await asyncio.sleep(60 * (volume / 1000) / flow_rate + 1)
        self.logger.debug(
            f"The valve position is {valve_position}, {volume} microliters "
            + f"are pumped with this flow rate {flow_rate} mL/min."
        )

    def get_sample_coordinate(self, rack_name, row, column):
        """Get the sample coordinate from sample position.

        :param rack_name:
            338S (left) and 335S (right)
        :param row:
        :param column:
        :return:
            sample_coordinate
        """
        if rack_name == '338S':
            self.sample_coordinate = \
                self.coordinate_value_338S.iloc[row, column].split(",")
        elif rack_name == '335S':
            self.sample_coordinate = \
                self.coordinate_value_335S.iloc[row, column].split(",")
        else:
            pass
        return self.sample_coordinate

    async def take_single_sample(self, rack_name, row, column, volume):
        """Take a single sample from one vial.

        :param rack_name:
            '338S' for the left one, '335S' for the right one.
        :param row:
            range [0,15] for 338S rack; [0,11] for 335S rack
        :param column:
            range [0,4]
        :param volume:
            volume for pump, uL
        """
        self.clear_error()
        self.sample_coordinate = self.get_sample_coordinate(
            rack_name=rack_name,
            row=row,
            column=column
        )
        await self.move_XY(
            float(self.sample_coordinate[0]),
            float(self.sample_coordinate[1])
        )
        await self.move_Z(float(self.sample_coordinate[2]))
        await asyncio.sleep(0.1)
        await self.set_syringe_pump(
            valve_position='N', volume=volume, flow_rate=4
        )
        await self.move_Z(122)
        await asyncio.sleep(0.1)

    async def take_solvent(self):

        await self.take_single_sample(
            rack_name='335S', row=11, column=0, volume=30
        )
        await self.move_XY(146.05, 0)
        await self.move_Z(91.1)
        await self.set_syringe_pump(
            valve_position='N', volume=-30, flow_rate=2
        )
        await self.move_Z(122)

    async def measure_cali(self):

        for i in range(4):
            for j in range(3):
                await self.set_syringe_pump(
                    valve_position='N', volume=20, flow_rate=2
                )
                await self.take_single_sample(
                    rack_name='338S', row=15, column=i, volume=100
                )
                await self.move_XY(146.05, 0)
                await self.move_Z(91.1)
                await asyncio.sleep(1)
                await self.set_syringe_pump(
                    valve_position='N', volume=-120, flow_rate=2
                )
                await self.move_Z(122)
                j += 1
            await self.move_Z(91.1)
            for k in range(4):
                await self.set_syringe_pump(
                    valve_position='R', volume=100, flow_rate=10
                )
                await self.set_syringe_pump(
                    valve_position='N', volume=-100, flow_rate=10
                )
                k += 1
            await self.move_Z(122)
            i += 1

    async def cleaning_test(self):

        for i in range(1):
            for j in range(2):
                await self.set_syringe_pump(
                    valve_position='N', volume=20, flow_rate=2
                )
                await self.take_single_sample(
                    rack_name='338S', row=14, column=0, volume=70
                )
                await asyncio.sleep(0.2)
                await self.clean_needle_tip()
                await self.move_XY(146.05, 0)
                await self.move_Z(91.1)
                await asyncio.sleep(1)
                await self.set_syringe_pump(
                    valve_position='N', volume=-90, flow_rate=2
                )
                await self.move_Z(122)
                j += 1
            await self.move_Z(91.1)
            for k in range(5):
                await self.set_syringe_pump(
                    valve_position='R', volume=100, flow_rate=10
                )
                await self.set_syringe_pump(
                    valve_position='N', volume=-100, flow_rate=10
                )
                k += 1
            await self.move_Z(122)
            await self.move_Z(91.1)
            await self.set_syringe_pump(
                valve_position='R', volume=100, flow_rate=10
            )
            await self.set_syringe_pump(
                valve_position='N', volume=-100, flow_rate=10
            )
            await self.move_Z(122)
            i += 1

    async def clean_needle_tip(self):
        """The function to clean the needle after each sampling to avoid
        cross-contamination.

        """
        self.logger.debug("Cleaning the needle tip.")
        self.sample_coordinate = self.get_sample_coordinate(
            rack_name='335S', row=11, column=0
        )
        await asyncio.sleep(0.1)
        await self.move_XY(
            float(self.sample_coordinate[0]),
            float(self.sample_coordinate[1])
        )
        await self.move_Z(float(self.sample_coordinate[2]))
        await asyncio.sleep(0.1)
        await self.move_Z(122)

    async def sample_mixing(self):
        """Insert the needle into the inert gas vial and then withdraw/infuse
        sample mixture four times to eliminate gas bubbles and mix the samples.

        """
        self.sample_coordinate = self.get_sample_coordinate(
            rack_name='335S', row=10, column=0
        )
        await self.move_XY(
            float(self.sample_coordinate[0]),
            float(self.sample_coordinate[1])
        )
        await self.move_Z(float(self.sample_coordinate[2]))
        for i in range(3):
            await self.set_syringe_pump(
                valve_position='N', volume=70, flow_rate=3
            )
            await self.set_syringe_pump(
                valve_position='N', volume=-70, flow_rate=3
            )
            i += 1
        # await self.set_syringe_pump(
        #     valve_position='N', volume=5, flow_rate=5
        # )

    async def clean_needle(self):
        """Function to clean the needle, sample mixer and direct injection
        module after each sampling.

        """
        for i in range(3):
            # pump clean solvent through needle
            await self.move_Z(91.1)
            await self.set_syringe_pump(
                valve_position='R', volume=500, flow_rate=2
            )
            await self.set_syringe_pump(
                valve_position='N', volume=-500, flow_rate=2
            )
            # pump in N2
            # await self.move_Z(122)
            # await self.set_syringe_pump(
            #     valve_position='R', volume=500, flow_rate=2
            # )
            # # pump out N2
            # await self.move_Z(91.1)
            # await self.set_syringe_pump(
            #     valve_position='N', volume=-500, flow_rate=2
            # )
        await self.move_Z(122)
        self.buffered(35, 'H')

    async def prepare_reaction_sample_rack(self, *reaction_sample):
        """Function to prepare the reaction sample.

        :param reaction_sample: tuple
            Each entry in the tuple follows this format:
        ['rack', row, col, vol-in-μL]
        """
        # await self.take_single_sample(rack_name='335S', row=10, column=0)
        # Position of insert gas vial
        self.logger.debug(f"Sample: {reaction_sample}")
        self.total_volume = 10
        await self.set_syringe_pump(
            valve_position='N', volume=10
        )
        # Prepare the sample
        for sample in reaction_sample:
            self.logger.debug(sample)
            await self.take_single_sample(
                rack_name=sample[0], row=int(sample[1]),
                column=int(sample[2]), volume=float(sample[3])
            )
            await asyncio.sleep(0.5)
            await self.clean_needle_tip()
            self.total_volume += sample[3]

        await self.sample_mixing()
        await self.move_Z(122)  # raise needle
        await self.move_XY(146.05, 0)
        await self.move_Z(91.1)  # dock into injection module
        await self.move_Z(122)
        await self.move_XY(146.05, 0)
        await self.move_Z(91.1)
        await self.switch_valve_position('VL')
        await self.set_syringe_pump(valve_position='N',
                                    volume=-self.total_volume,
                                    flow_rate=4)
        await self.switch_valve_position('VI')
        await self.move_Z(122)

    async def prepare_reaction_sample(self, sample_info):
        """Function to prepare the reaction sample.

        :param sample_info:
        List containing different sample info
            (from the function prepare_sample_info() in Sample_info.py)
        """
        self.total_volume = 50
        await self.set_syringe_pump(
            valve_position='N', volume=50, flow_rate=1.5
        )
        for sample in sample_info:
            await self.move_XY(float(sample[0].split(',')[0]),
                               float(sample[0].split(',')[1]))
            await asyncio.sleep(0.5)
            await self.move_Z(float(sample[0].split(',')[2]))
            await self.set_syringe_pump(
                valve_position='N', volume=round(sample[1] * 1000, 1), flow_rate=1.5)
            self.total_volume += round(sample[1] * 1000, 1)
            await asyncio.sleep(2)
            await self.move_Z(122)
            await asyncio.sleep(0.5)
            await self.clean_needle_tip()

        await self.sample_mixing()
        await self.move_Z(122)
        await asyncio.sleep(0.5)
        await self.move_XY(146.05, 0)
        await asyncio.sleep(0.5)
        await self.move_Z(91.1)
        await asyncio.sleep(0.5)
        await self.switch_valve_position('VL')
        await self.set_syringe_pump(
            valve_position='N', volume=-self.total_volume, flow_rate=3
        )
        await self.switch_valve_position('VI')
        await self.move_Z(122)
        await asyncio.sleep(1)


if __name__ == '__main__':
    GX_241 = LiquidHandler()

    GX_241.reset()
    asyncio.run(GX_241.Gilson_identification())
    GX_241.get_error()
    GX_241.clear_error()
    asyncio.run(GX_241.move_XY(146.05, 0)) # move to inj. module
    asyncio.run(GX_241.move_Z(91.1))  # dock into injection module
    asyncio.run(GX_241.clean_needle())

