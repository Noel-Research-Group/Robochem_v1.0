import pymysql  # using a python3-compatible fork called mysqlclient, see https://www.lfd.uci.edu/~gohlke/pythonlibs/
import pymysql.cursors
import logging
import subprocess


class MySQLReader:
    """
    The MySQLReader class handles reading/writing to the mySQL database.
    """

    def __init__(self, mysql_user, mysql_passwd, mysql_host, mysql_db,
                 xampp_location):
        # connect to mysql database
        self.mysql_user = mysql_user
        self.mysql_pass = mysql_passwd
        self.mysql_host = mysql_host
        self.mysql_db = mysql_db
        # xampp location in case a restart of apache or mysql is necessary
        self.xampp_location = xampp_location

    def open_xampp_control(self):
        '''Opens connection to the xampp control panel.'''

        xampp_location = self.xampp_location
        if xampp_location != "":
            if xampp_location[-1] != "/" and xampp_location[-1] != "\\":
                xampp_location += "/"
            subprocess.Popen([xampp_location + "xampp-control.exe"])

    def start_apache(self):
        '''starts the apache server using the xampp batch script function'''
        logging.info("Starting Apache2.")
        self.run_xampp_batch_script("apache_start.bat")

    def start_mysqld(self):
        '''starts the mysql server using the xampp batch script function'''
        logging.info("Starting MySQL.")
        self.run_xampp_batch_script("mysql_start.bat")

    def run_xampp_batch_script(self, scriptname):
        '''
        Helper function that runs the batch-scripts located in the xampp directory
        :param: scriptname: string, name of the batch script to run
        '''
        xampp_location = self.xampp_location
        if xampp_location != "":
            if xampp_location[-1] != "/" and xampp_location[-1] != "\\":
                xampp_location += "/"
            subprocess.Popen([xampp_location + scriptname], shell=True)

    def is_apache_running(self):
        '''
        checks if apache is running by checking if the httpd.exe process is running
        :return: boolean, True if apache is running, False if not
        '''
        return self.process_exists("httpd.exe")

    def is_mysqld_running(self):
        '''
        checks if mysqld is running by checking if the mysqld.exe process is running
        :return: boolean, True if mysqld is running, False if not
        '''
        return self.process_exists("mysqld.exe")

    def process_exists(self, process_name):
        '''
        function that used to check if the process exists given the process name, for reference see:
        https://stackoverflow.com/questions/7787120/python-check-if-a-process-is-running-or-not

        :param: process_name: string, name of the process to check
        :return: boolean, True if process is running, False if not
        '''

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
        # use buildin check_output right away
        output = subprocess.check_output(call, startupinfo=startupinfo).decode()
        # check in last line for process name
        last_line = output.strip().split('\r\n')[-1]
        # because Fail message could be translated
        return last_line.lower().startswith(process_name.lower())

    def connect_db(self):
        '''
        Function to connect to the MySQL database, returns a connection and a cursor object:
        WARINING:
        For reasons unknown, only one cursor per connection works properly
        Please after using the DB, close the connection with conn.close

        :return: conn, cur: connection and cursor objects
        '''
        try:
            conn = pymysql.connect(user=self.mysql_user, passwd=self.mysql_pass,
                                   host=self.mysql_host, db=self.mysql_db,
                                   cursorclass=pymysql.cursors.DictCursor)
        except pymysql.OperationalError:
            logging.error("Connection to the MySQL DB has failed!")
            return None, None
        conn.autocommit(True)
        cur = conn.cursor()
        return conn, cur

    def read_config(self):
        '''
        Reads the configuration table from the MySQL database
        :return: config: dictionary containing the configuration
        '''

        conn, cur = self.connect_db()
        if conn is None:
            return None
        cur.execute("SELECT * from config")
        config = cur.fetchall()
        conn.close()
        return config[0]

    def read_fnmr_standards(self):
        '''
        Reads the fnmr_standards table from the MySQL database.
.
        :return: standard_shift: dictionary of lists containing the chemical shifts of the standards. The lists have in
        position 0 the chemical shift and in position 1 the number of F atoms in the standard.

        :optional return: if no connection is established, returns None
        '''
        conn, cur = self.connect_db()
        if conn is None:
            return None
        cur.execute("SELECT * from fnmr_standards")
        fnmr_standards = cur.fetchall()
        conn.close()
        standard_shift = {}
        for fnmr_standard in fnmr_standards:
            standard_shift[fnmr_standard['name']] = [
                str(fnmr_standard['shift']), fnmr_standard['fluorine_atoms']]
        return standard_shift

    def read_samples(self, conn=None, cur=None):
        '''
        Reads the sample tables form the MySQL database.

        :param: conn: connection object, optional, if not supplied, a new connection will be established
        :param: cur: cursor object, optional, if not supplied, a new cursor will be established

        :return: samples: nested dictionary containing the samples
        '''
        new_conn = False
        if conn == None or cur == None:
            conn, cur = self.connect_db()
            if conn is None:
                return None
            new_conn = True
        cur.execute("SELECT * from samples")
        samples = cur.fetchall()
        if new_conn:
            conn.close()
        return samples

    def read_shimming(self, conn=None, cur=None):
        '''
        Reads shimming table from the MySQL database.

        :param: conn: connection object, optional, if not supplied, a new connection will be established
        :param: cur: cursor object, optional, if not supplied, a new cursor will be established

        :return: shimming: dictionary containing the shimming table, the reference for the flags is as follows:
        shimming['Shimming']:  0 = shimming ok
                               1 = someone gave the order for shimming, we are performing checkshim now
                               2 = we are performing quickshim now
                               3 and 4 = the other quickshims failed and we are performing more quickshims
                               5 = 3x quickshim failed, we are aborting now
        '''
        new_conn = False
        if conn == None or cur == None:
            conn, cur = self.connect_db()
            if conn is None:
                return None
            new_conn = True
        cur.execute("SELECT * from shimming")
        shimming = cur.fetchall()
        shimming = shimming[0]
        if new_conn:
            conn.close()
        return shimming

    def read_queueabort(self, conn=None, cur=None):
        '''
        Reads queueabort table from the MySQL database.

        :param: conn: connection object, optional, if not supplied, a new connection will be established
        :param: cur: cursor object, optional, if not supplied, a new cursor will be established

        :return: queueabort: dictionary containing the queueabort table, a.k.a. the abort flag, the reference for the flags is as follows:
        queueabort['QueueStat']: 0 = queue is either not running, or was aborted.
                                 1 = someone gave the order to start the queue.
        '''
        new_conn = False
        if conn == None or cur == None:
            conn, cur = self.connect_db()
            if conn is None:
                return None
            new_conn = True
        cur.execute("SELECT * from queueabort")
        queueabort = cur.fetchall()
        queueabort = queueabort[0]
        if new_conn:
            conn.close()
        return queueabort

    def write_result(self, sample_name, result):
        '''
        Writes the result of the sample in the MySQL database and then closes the connection to the database.
        :param sample_name: string, name of the sample
        :param result: string, result of the sample
        :return: True

        '''
        conn, cur = self.connect_db()
        if conn is None:
            return None
        cur.execute("SELECT ID FROM samples WHERE Name = %s LIMIT 1",
                    (sample_name,))
        sample = cur.fetchall()
        sample = sample[0]
        cur.execute("UPDATE samples SET result = %s WHERE ID = %s",
                    (result, sample["ID"]))
        conn.close()
        return True