'''
Generic gui base class
Common class methods to be inherited by ccn_proccesing and cpc_processing
Author: Kristina Johnson
'''

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import atmoscripts

class GenericBaseGui(ttk.Frame):

    def load_and_process(self):
        '''
        Once all parameters have been chosen, checks all the input values and
        begins the processing.
        '''

        # Initialise
        msg = 'There is an error with your input! \n'
        # Check input variables
        try:
            self.files_raw
        except AttributeError:
        	# if self.files_raw is None:
            msg = msg + '\n Please select raw input files'

        try:
            self.output_path
            if not os.path.exists(self.output_path):
                msg = msg + '\n Chosen output path does not exist'
        except AttributeError:
            msg = msg + '\n Please select output path'


        if msg != 'There is an error with your input! \n':
            self._alert_bad_input(msg)
            return

        if self.cb_output_filetype.get() == 'netcdf':
            if os.path.exists(self.output_path):
                os.chdir(self.output_path)

            atmoscripts.save_temp_glob_att(self.nc_global_title,
                                           self.nc_global_description,
                                           self.nc_author,
                                           self.nc_global_institution,
                                           self.nc_global_comment)

        # Open new window showing status with the option to cancel execution
        # and disable input window
        self._build_status_window()

        # Setup input
        output_time_res = [self.output_1s.get(),
                           self.output_5s.get(),
                           self.output_10s.get(),
                           self.output_15s.get(),
                           self.output_30s.get(),
                           self.output_1m.get(),
                           self.output_5m.get(),
                           self.output_10m.get(),
                           self.output_15m.get(),
                           self.output_30m.get(),
                           self.output_1h.get(),
                           self.output_3h.get(),
                           self.output_6h.get(),
                           self.output_12h.get(),
                           self.output_1d.get()]

        # Change to boolean array
        output_time_res = [True if item == 1
                           else False
                           for item in output_time_res]

        if self.cb_file_freq.get() == 'Single file':
            concat_file_freq = 'all'
        elif self.cb_file_freq.get() == 'Daily files':
            concat_file_freq = 'daily'
        elif self.cb_file_freq.get() == 'Weekly files':
            concat_file_freq = 'weekly'
        elif self.cb_file_freq.get() == 'Monthly files':
            concat_file_freq = 'monthly'
        else:
            print('Something has gone terribly wrong here...')
            self.destroy()

        try:
            flow_cal_df = CCNC.load_flow_cals(file_FULLPATH=self.flowcal_file)
        except:
            flow_cal_df = None

        try:
            mask_df = CCNC.load_manual_mask(file_FULLPATH=self.mask_file)
        except:
            mask_df = None

        if self.cb_output_filetype.get() == 'netcdf':
            output_filetype = 'nc'
        elif self.cb_output_filetype.get() == 'hdf':
            output_filetype = 'h5'
        else:
            output_filetype = 'csv'

        print("Loading data from file")

        t = threading.Thread(target=self.loadAndProcess_Multithread,
                             args=(output_filetype,
                                   output_time_res,
                                   concat_file_freq,
                                   mask_df,
                                   flow_cal_df))
        t.start()

#-----------------------------------------------------------
# GUI Functionality
#-----------------------------------------------------------
    def raw_file_dialog(self):
        '''Prompts user to select input files'''
        self.files_raw = filedialog.askopenfilenames()
        self.raw_path = os.path.dirname(self.files_raw[0])

        # remove previous input
        self.lb_openFiles.delete(0, tk.END)

        # Update the text box
        self.lb_openFiles.delete(0, tk.END)
        for i in range(0, len(self.files_raw)):
            self.lb_openFiles.insert(i, self.files_raw[i])
        try:
            if self.output_path == '':
                self.update_output_path()
        except AttributeError:
            self.update_output_path()
        return

    def update_output_path(self):
        self.t_outputPath.insert(tk.END, self.raw_path)
        self.output_path = self.raw_path


    def browse_for_file(self):
        '''Prompts user to select input file'''
        file = filedialog.askopenfilename()
        return file

    def ask_mask_file(self):
        ''' Asks for the mask file input and shows it in the gui'''
        self.mask_file = self.browse_for_file()
        self.tb2.insert(tk.END, self.mask_file)
        return

    def ask_flowcal_file(self):
        ''' Asks for the flow cal file input and shows it in the gui'''
        self.flowcal_file = self.browse_for_file()
        self.tb3.insert(tk.END, self.flowcal_file)
        return

    def output_path_dialog(self):
        '''Selecting output path, if not chosen, use the input directory'''
        self.output_path = filedialog.askdirectory()
        self.t_outputPath.delete(0, tk.END)
        self.t_outputPath.insert(tk.END, self.output_path)

    def launch_netcdf_input(self, event):
        '''
        Launches netcdf input when the combobox option is selected
        '''
        if self.cb_output_filetype.get() == 'netcdf':
            self._build_netcdf_input_window()

    def close_netcdf_window(self):
        '''
        Closes the netcdf window on the OK button press and saves the input
        as a temporary file which can be read by the code later.
        '''
        self.nc_global_title = self.nc_e0.get()
        self.nc_global_description = self.nc_e1.get()
        self.nc_author = self.nc_e2.get()
        self.nc_global_institution = self.nc_e3.get()
        self.nc_global_comment = self.nc_e4.get()
        self.w_netcdf_input.destroy()

#-----------------------------------------------------------
# Variable check window
#-----------------------------------------------------------
    def _alert_bad_input(self, message='Nothing to see here...'):
        self.top = tk.Toplevel()
        self.top.title('Bad input!')
        self.top.geometry("%dx%d" % (300, 200))
        txt = tk.Message(self.top,
                         text=message,
                         justify=tk.CENTER,
                         width=300)
        txt.pack(fill='x')

        bt_ok = tk.Button(self.top, text="OK", command=self.dismiss)
        bt_ok.pack(side=tk.BOTTOM)

    def dismiss(self):
        self.top.destroy()


#-----------------------------------------------------------
# NetCDF Description input window
#-----------------------------------------------------------
    def _build_netcdf_input_window(self):
        self.w_netcdf_input = tk.Toplevel()
        self.w_netcdf_input.title('NetCDF Input')
        self.w_netcdf_input.geometry("300x310")

        self.w_netcdf_input.description = tk.Label(self.w_netcdf_input,
                text='Please provide descriptions (global attributes) to be \
                included in the self-describing NetCDF file \n',
                wraplength=300)
        self.w_netcdf_input.description.pack()

        text = 'Dataset title'
        self.nc_l0 = tk.Label(self.w_netcdf_input, text=text, wraplength=200)
        self.nc_l0.pack()
        self.nc_e0 = tk.Entry(self.w_netcdf_input, width=200)
        self.nc_e0.pack()

        text = 'Dataset description'
        self.nc_l1 = tk.Label(self.w_netcdf_input, text=text, wraplength=200)
        self.nc_l1.pack()
        self.nc_e1 = tk.Entry(self.w_netcdf_input, width=200)
        self.nc_e1.pack()

        text = 'Author of dataset'
        self.nc_l2 = tk.Label(self.w_netcdf_input, text=text, wraplength=200)
        self.nc_l2.pack()
        self.nc_e2 = tk.Entry(self.w_netcdf_input, width=200)
        self.nc_e2.pack()

        text = 'Institution where dataset is produced'
        self.nc_l3 = tk.Label(self.w_netcdf_input, text=text, wraplength=200)
        self.nc_l3.pack()
        self.nc_e3 = tk.Entry(self.w_netcdf_input, width=200)
        self.nc_e3.pack()

        text = 'Comment'
        self.nc_l4 = tk.Label(self.w_netcdf_input, text=text, wraplength=200)
        self.nc_l4.pack()
        self.nc_e4 = tk.Entry(self.w_netcdf_input, width=50)
        self.nc_e4.pack()

        self.w_netcdf_input.spacer = tk.Label(self.w_netcdf_input, text='').pack()

        self.nc_bt_ok = tk.Button(self.w_netcdf_input,
                                  text="OK",
                                  width=30,
                                  command=self.close_netcdf_window)
        self.nc_bt_ok.pack()
