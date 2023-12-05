import socket
import time
import os
import threading
import xml.etree.ElementTree as ET
import traceback
import json
from Spinsolve_NMR.MySQLReader import *
# from MySQLReader import *
from phase_sensor_CSV_naming import get_your_abs_project_path
import asyncio

SETUP_INFO_JSON = '../experimental_setup.json'
with open(SETUP_INFO_JSON) as json_file:
    experimental_setup = json.load(json_file)

NMR_NUCELUS = experimental_setup["nmr_nucleus"]
NMR_SETTINGS = experimental_setup["nmr_settings"]

class Spinsolve:
    '''
    Class that handles the communication with the Magritec NMR spectrometer through the use of SPINSOLVE
    '''

    def __init__(self, mysql_reader):
        '''
        Initialise the class by creating a Spinsolve object which will handle the communication between the
        spectrometer and software.

        :param mysql_reader: MySQLReader object with access to the config (from MYSQLReader.py)

        '''

        # finds the nmr folder
        self.NMRFolder = (
                            get_your_abs_project_path()
                            + '/NMR_DATA/'
                            )
        # Make sure the path is in the format we want

        if self.NMRFolder[-1] != "/" and self.NMRFolder[-1] != "\\":
            self.NMRFolder += "/"
        self.socket = False
        self.protocols = False
        self.options = False
        self.last_status = 0
        self.progress = 0

        # flags for measurements. will be reset in the measurement functions.
        self.completed = False
        self.completed2 = False
        self.successful = False

        # start listener daemon which reads the status of the NMR spectrometer.
        self.listener = threading.Thread(target=self.listen, args=())
        self.listener.daemon = True
        self.listener.start()

        # # NMR Connections
        # self.spinsolve = Spinsolve(mysql_reader)
        # self.spinsolve.connect()
        #
        # # Database connections
        self.xampp_location = "C:/xampp"
        self.mysql_uname = "root"
        self.mysql_passwd = ""
        self.mysql_host = "localhost"
        self.mysql_db = "autosampler.sql"
        #self.mysql_reader = mysql_reader
        self.mysql_reader = MySQLReader('root',
                                   '',
                                   'localhost',
                                   'autosampler.sql',
                                   'C:/xampp')
        config = self.mysql_reader.read_config()


    def connect(self):
        '''
        Connect to the magritek NMR spectrometer.

        :return: True if successful, False otherwise.

        '''
        # read configuration and define IP:port combination for the spectrometer
        config = self.mysql_reader.read_config()
        nmr_ip = '127.0.0.1'
        port = 13000

        # try the connection to the spectrometer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((nmr_ip, port))
            return True
        except:
            logging.error("Failed to connect to Spinsolve!")
            return False

    def disconnect(self):
        '''
        Close the connection to the Spinsolve NMR.
        '''
        try:
            self.socket.close()
        except:
            pass
        self.socket = False

    def is_connected(self):
        '''
        check if socket is connected or not
        '''
        if self.socket:
            return True
        else:
            return False

    def listen(self):
        '''
        Background process collection, this reads the status of the NMR connection/measurement continuously
        and updates the relevant class attributes accordingly.
.
        '''

        def process_status_notification(root):
            '''
            checks for process status notifications and updates class attributes.
            :param root:
            :return:
            '''
            # Process a status notification
            SN = root.find("StatusNotification")
            if SN != None:
                # refresh the progress attribute, if available
                if SN.find("Progress") != None:
                    self.progress = SN.find("Progress").get("percentage")
                # set a flag that the measurement was completed/successful.
                # this will be reset by the function which is waiting for
                # this flag to be set.
                if SN.find("Completed") != None:
                    self.completed = True
                    logging.debug(
                        "YEAH! A measurement has just been completed! :)")
                    if SN.find("Completed").get("completed") == "true":
                        # in the case of an aborted shim, completed will be
                        # True, but completed2 will be False.
                        self.completed2 = True
                        logging.debug(" -- 'Completed' is True")
                    if SN.find("Completed").get("successful") == "true":
                        self.successful = True
                        logging.debug(" -- 'Successful' is True")

        while True:
            if self.socket != False:
                try:
                    message = self.socket.recv(4096)
                    message = message.decode("UTF-8")
                    try:
                        root = ET.fromstring(message)
                        process_status_notification(root)
                    except ET.ParseError:
                        # something unexpeced happened in the xml recieved from the spectrometer.
                        # this happens sometimes when multiple xml messages are received
                        messages = message.split("<?xml ")
                        messages.pop(0)  # remove first string which is empty
                        for message in messages:
                            message = "<?xml " + message
                            try:
                                root = ET.fromstring(message)
                                process_status_notification(root)
                            except:
                                # now this is complete bullshit, no idea what
                                # happened here, just print the goddamn error
                                logging.error(
                                    "Problem occured with the following  "
                                    "message: " + str(message))
                                traceback.print_exc()
                    # Write down the date of the contact with the spectrometer.
                    self.last_status = int(time.time())
                except:
                    logging.warning(
                        "It appears that the Spinsolve software is not "
                        "running,  has crashed or was closed by the user.  "
                        "Aborting...")
                    self.disconnect()
                    conn, cur = self.mysql_reader.connect_db()
                    if conn is not None and cur is not None:
                        cur.execute("UPDATE QueueAbort SET QueueStat = 0")
                        conn.close()
            time.sleep(0.2)

    def shim(self, shimtype):
        '''
        Asks the NMR to perform a shim. (IE: a calibration of the magnetic field)

        :param shimtype: can be a string, either "CheckShim", "QuickShim" or "PowerShim",
        which specifies the shimming which should be performed.

        :return retval: True if the measurement was successful, and False otherwise.
        :return aborted: True if the measurement was aborted by user, False otherwise.
        '''

        # initialise the time and parse it to a string in the preferred format
        t = time.localtime()
        tstr = time.strftime("%Y-%m-%d_%H%M%S", t)
        # initialise the return values
        retval = False
        aborted = False
        # set the request message to send to the nmr
        message = self.message_set("<Sample>Shim" + tstr + "</Sample>")
        message += self.message_set(
            "<DataFolder><UserFolder>" + self.NMRFolder + "Shim" +  tstr +
            "</UserFolder></DataFolder>",
            False)
        message += ("<Message>"
                    "<Start protocol='SHIM'>"
                    "<Option name='Shim' value='" + shimtype + "' />"
                                                               "</Start>"
                                                               "</Message>")

        # send the request to the NMR
        self.socket.send(message.encode())

        # check if successful
        timeouts = {"CheckShim": 1, "QuickShim": 6,
                    "PowerShim": 60}  # in minutes
        timeout = timeouts[shimtype] * 10 * 60  # in 100 ms
        i = 0
        while i < timeout:
            i += 1
            # did anyone press the abort button?
            # queueabort = self.mysql_reader.read_queueabort()
            # if queueabort['QueueStat'] == 0 and not aborted:
            #     self.abort()
            #     i = timeout - 10  # Give it one second to abort.
            #     aborted = True
            if self.completed:
                self.completed = False
                if self.successful:
                    self.successful = False
                    SuccessFile = self.NMRFolder + "Shim" + tstr + \
                                  "/protocol.par"
                    if os.path.isfile(SuccessFile):
                        retval = True
                break
            time.sleep(0.1)
        self.progress = 0  # reset progress
        return retval, aborted

    def measure_sample(self, name, protocol, options, solvent="None",
                       comment=""):
        '''
        Requests for the spectrometer to measure the sample that is currently residing in the sample chamber.
        Writes the spectrum file in the folder specified as self.NMRFolder.

        :param name: string, name of the sample
        :param protocol: string, the protocol (proton, fluorine, etc)
        :param options: dictionary, containing the options for the measurement (which options need to be given depends on the protocol)
        :param solvent: string, the solvent
        :param comment: string, a comment

        :return retval: True if the measurement was successful, and False otherwise.
        :return aborted: True if the measurement was aborted by user, False otherwise.

        '''
        # initialise the return values
        retval = False
        aborted = False
        self.progress = 0

        # Generation of the request message:
        # Sample name
        message = self.message_set("<Sample>" + name + "</Sample>")
        # Solvent
        message += self.message_set("<Solvent>" + solvent + "</Solvent>", False)
        # Comment
        message += self.message_set(
            "<UserData><Data key='Comment' value='" + comment +
            "'/></UserData>",
            False)
        # Folder
        message += self.message_set(
            "<DataFolder><UserFolder>" + self.NMRFolder + name +
            "</UserFolder></DataFolder>", False)
        # send all the options in raw format.
        message += "<Message>"
        message += "    <Start protocol='" + protocol + "'>"
        for option in options:
            message += "        <Option name='" + option + "' value='" + str(
                options[option]) + "'/>"
        message += "        <Processing>"
        message += "            <Press Name='MNOVA'/>"
        message += "        </Processing>"
        message += "    </Start>"
        message += "</Message>"
        print(message)
        # send the request to the NMR
        self.socket.send(message.encode())
        # now wait for the measurement to finish...
        timeout = 60 * 2  # in minutes
        timeout = timeout * 10 * 60  # in 100 ms
        i = 0
        while i < timeout:
            i += 1
            if self.completed:
                self.completed = False
                # sometimes there is a delay on slow computers here,
                # need  timeout here
                for j in range(10):  # 10x100 ms = 1 sec
                    if self.successful == True:
                        break
                    time.sleep(0.1)
                if self.successful:
                    self.successful = False
                    # wait for a few seconds, sometimes spinsolve is kind of
                    # slow when generating the files.
                    SuccessFile = self.NMRFolder + name + "/spectrum.1d"
                    for j in range(10):  # 10 seconds maximum
                        if os.path.isfile(SuccessFile):
                            retval = True
                            break
                        time.sleep(1)
                break
            time.sleep(0.1)
        self.progress = 0  # reset progress
        return retval, aborted

    def abort(self):
        '''
        Requests the spectrometer to abort the currently running measurement.
        WARNING: When a measurement is aborted, the StatusNotification for "completed"
        will be sent out, which will automatically kick out any running loop.
        '''

        # tries to send the abort-request, but if it fails just continues (prevents crashes)
        try:
            message = ("<?xml version='1.0' encoding='UTF-8'?>"
                       "<Message>"
                       "<Abort />"
                       "</Message>")
            self.socket.send(message.encode())
        except:
            pass

    def message_set(self, message, doctype=True):
        '''
        Wraps the message in a XML code that the spectrometer can understand.
        More in depth generates a message in the following format:
        <?xml version='1.0' encoding='UTF-8'?>
        <Message>
            <Set>
                ---- adds here the string from the argument "message"
            </Set>
        </Message>

        :param message: string, the message to be wrapped
        :param doctype: boolean, if True, the doctype string will be added to the message, if False, it will be left out.

        :return xml_code: string, the wrapped message
        '''
        xml_code = ""
        if doctype:
            xml_code += "<?xml version='1.0' encoding='UTF-8'?>"
        xml_code += ("<Message>"
                     "<Set>"
                     + str(message) +
                     "</Set>"
                     "</Message>")
        return xml_code

    async def run_nmr(self,
                      experiment_name):
        '''
        Runs the NMR measurement, full sequence. Async as it waits for the results from the NMR spectrometer.
        :param experiment_name: string, the name of the experiment
        :param pulse_angle: int, the pulse angle default 90 degrees
        :param number: int, number of scans default 4
        :param repetition_time: int, repetition time default 30 seconds
        :param acquisition_time: float, acquisition time default 6.4 seconds
        :return:
        '''

        spinsolve = Spinsolve(self.mysql_reader)
        spinsolve.connect()
        spinsolve.measure_sample(str(experiment_name),
                                 NMR_NUCELUS,
                                 NMR_SETTINGS
                                 )
        await asyncio.sleep(5)

if __name__ == '__main__':
    xampp_location = "C:/xampp"
    mysql_uname = "root"
    mysql_passwd = ""
    mysql_host = "localhost"
    mysql_db = "autosampler.sql"
    mysql_reader = MySLReader(mysql_uname,
                               mysql_passwd,
                               mysql_host,
                               mysql_db,
                               xampp_location)
    spinsolve = Spinsolve(mysql_reader)
    spinsolve.connect()

    spinsolve.measure_sample("Test",
                             "1D EXTENDED+",
                             {"PulseAngle": "90",
                              "Number": "16",
                              "RepetitionTime": "10",
                              "AcquisitionTime": "1.64",
                              "centreFrequency": "-165",
                              "decouplePower": "0"
                              }
                             )

    # asyncio.run(Spinsolve(mysql_reader=None).run_nmr())
