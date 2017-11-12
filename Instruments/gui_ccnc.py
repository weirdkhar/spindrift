'''
Code for the gui of the processing of aerosol gear

Written by Ruhi Humphries
Edited by Kristina Johnson

Useful documentation:
    http://www.tkdocs.com/tutorial/widgets.html
    http://pyinmyeye.blogspot.com.au/2012/08/tkinter-combobox-demo.html
    http://www.python-course.eu/tkinter_layout_management.php
'''
import re
import os
import time
import sys
import threading
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime as dt

import Instruments.CCNC as CCNC
from Instruments.gui_base import GenericBaseGui
from Instruments.gui_plot import AnnotateablePlot
import ToolTip

import atmoscripts

class ccn_processing(GenericBaseGui, AnnotateablePlot):
    '''
    CCN processing
    '''
    def __init__(self, isapp=True):
        """
        Initialise the gui
        KJ - new version using grid
        """
        tk.Frame.__init__(self, name='ccnprocessing')
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.master.title('DMT CCN Processing')
        self.master.geometry('1760x1160')    # original 880x560
        self.isapp = isapp
        self.globalMainFrame = ''


    def __repr__(self):
        return 'ccn_processing()'

    def __str__(self):
        return 'member of ccn_processing'

    def load_and_process(self):
        '''
        Once all parameters have been chosen, checks all the input values and
        begins the processing.
        '''
        self.plot_list = []

        # Initialise
        msg = 'There is an error with your input! \n'
        # Check input variables
        try:
            self.ccn_files_raw
            print('self.ccn_files_raw = ', self.ccn_files_raw)
        except AttributeError:
        	# if self.ccn_files_raw is None:
            msg = msg + '\n Please select raw input files'

        try:
            self.ccn_output_path
            if not os.path.exists(self.ccn_output_path):
                msg = msg + '\n Chosen output path does not exist'
        except AttributeError:
            msg = msg + '\n Please select output path'

        if msg != 'There is an error with your input! \n':
            self._alert_bad_input(msg)
            return

        if self.ccn_cb_output_filetype.get() == 'netcdf':
            if os.path.exists(self.ccn_output_path):
                os.chdir(self.ccn_output_path)

            atmoscripts.save_temp_glob_att(self.nc_global_title,
                                           self.nc_global_description,
                                           self.nc_author,
                                           self.nc_global_institution,
                                           self.nc_global_comment)

        # Open new window showing status with the option to cancel execution
        # and disable input window
        self._build_status_window()

        output_time_res = []
        for i in range(0, 15):
            output_time_res.append(False)

        if self.ccn_cb_output_time_resolution.get() == '1 second':
            output_time_res[0] = True
        elif self.ccn_cb_output_time_resolution.get() == '5 seconds':
            output_time_res[1] = True
        elif self.ccn_cb_output_time_resolution.get() == '10 seconds':
            output_time_res[2] = True
        elif self.ccn_cb_output_time_resolution.get() == '15 seconds':
            output_time_res[3] = True
        elif self.ccn_cb_output_time_resolution.get() == '30 seconds':
            output_time_res[4] = True
        elif self.ccn_cb_output_time_resolution.get() == '1 minute':
            output_time_res[5] = True
        elif self.ccn_cb_output_time_resolution.get() == '5 minutes':
            output_time_res[6] = True
        elif self.ccn_cb_output_time_resolution.get() == '10 minutes':
            output_time_res[7] = True
        elif self.ccn_cb_output_time_resolution.get() == '15 minutes':
            output_time_res[8] = True
        elif self.ccn_cb_output_time_resolution.get() == '30 minutes':
            output_time_res[9] = True
        elif self.ccn_cb_output_time_resolution.get() == '1 hour':
            output_time_res[10] = True
        elif self.ccn_cb_output_time_resolution.get() == '3 hours':
            output_time_res[11] = True
        elif self.ccn_cb_output_time_resolution.get() == '6 hours':
            output_time_res[12] = True
        elif self.ccn_cb_output_time_resolution.get() == '12 hours':
            output_time_res[13] = True
        elif self.ccn_cb_output_time_resolution.get() == '1 day':
            output_time_res[14] = True

        if self.ccn_cb_file_freq.get() == 'Single file':
            concat_file_freq = 'all'
        elif self.ccn_cb_file_freq.get() == 'Daily files':
            concat_file_freq = 'daily'
        elif self.ccn_cb_file_freq.get() == 'Weekly files':
            concat_file_freq = 'weekly'
        elif self.ccn_cb_file_freq.get() == 'Monthly files':
            concat_file_freq = 'monthly'
        else:
            print('Something has gone terribly wrong here...')
            self.destroy()

        try:
            flow_cal_df = CCNC.load_flow_cals(file_FULLPATH=self.ccn_flowcal_file)
        except:
            flow_cal_df = None

        try:
            mask_df = CCNC.load_manual_mask(file_FULLPATH=self.ccn_mask_file)
        except:
            mask_df = None

        if self.ccn_cb_output_filetype.get() == 'netcdf':
            output_filetype = 'nc'
        elif self.ccn_cb_output_filetype.get() == 'hdf':
            output_filetype = 'h5'
        else:
            output_filetype = 'csv'

        print('Loading data from file')

        thread = threading.Thread(target=self.loadAndProcess_Multithread,
                             	  args=(output_filetype,
                                  output_time_res,
                                  concat_file_freq,
                                  mask_df,
                                  flow_cal_df))
        thread.start()
        # thread.join() stalls app FOREVER


    def loadAndProcess_Multithread(self,
                                   output_filetype,
                                   output_time_res,
                                   concat_file_freq,
                                   mask_df,
                                   flow_cal_df):

        # Call processing function.
        # When this function calls return at its end, the thread is terminated automatically.
        CCNC.LoadAndProcess(ccn_raw_path=self.ccn_raw_path,
                            ccn_output_path=self.ccn_output_path,
                            ccn_output_filetype=output_filetype,
                            filename_base='CCN',
                            force_reload_from_source=self.forceReload.get(),
                            split_by_supersaturation=self.ccn_split_SS.get(),
                            QC=self.qc.get(),
                            output_time_resolution=output_time_res,
                            concat_file_frequency=concat_file_freq,
                            mask_period_timestamp_df=mask_df,
                            flow_cal_df=flow_cal_df,
                            flow_setpt=float(self.ccn_tb_flow_rate_set.get())*1000,
                            flow_polyDeg=float(self.ccn_tb_flow_rate_fit.get()),
                            calibrate_for_pressure=self.ccn_cb_pressCal,
                            press_cal=float(self.ccn_tb_calPress.get()),
                            press_meas=float(self.ccn_tb_measPress.get()),
                            input_filelist=list(self.ccn_files_raw),
                            gui_mode=True,
                            gui_mainloop=self.w_status)

        self.finished_window()  # draw Data Processing Complete! window

        # Get all the output files
        FILE_PATH = self.ccn_output_path
        FILE_LIST = []
        PLOTS = []
        for root, directories, filenames in os.walk(FILE_PATH):
            for filename in filenames:
                FILE_LIST.append(filename)

        for filename in FILE_LIST:
            # Find weekly, daily, monthly, single only files
            if re.match('CCN_raw_[0-9]{4}_wk[0-9]{2}.csv', filename) or \
                re.match('CCN_raw_[0-9]{6}.csv', filename) or \
                re.match('CCN_raw[0-9]{4}.csv', filename) or \
                re.match('CCN_raw.csv', filename):
                    final_file = {'path': self.ccn_output_path + '/' + filename, 'type': output_filetype}
                    print('final_file is ', final_file)
                    self.plot_list.append(final_file)

        print('number of threads = ', threading.enumerate())    # number = returns 2 objects - main and Thread1
        # Plot all the output files.
        # self.create_plot_ccn(PLOTS)   # << Move this out of the thread.  GUIs do not like threads!

#-----------------------------------------------------------
# GUI Widgets
#-----------------------------------------------------------
    def create_input_frame_ccn(self, mainFrame):
        """
        Draw the gui frame for data input options
        KJ - new version using grid
        """
        self.ccn_f1 = tk.LabelFrame(mainFrame, text='Input data')
        self.ccn_b_open = tk.Button(self.ccn_f1, text='Select raw files', command=self.raw_file_dialog)
        self.ccn_lb_openFiles = tk.Listbox(self.ccn_f1) # original listbox had a scroll bar added
        self.ccn_forceReload = tk.IntVar()
        self.ccn_cb_forceReload = tk.Checkbutton(self.ccn_f1,
                                             text='Force reload from source',
                                             variable=self.ccn_forceReload)
        self.ccn_cb_forceReload.select()

        # place all Input Frame elements using grid
        self.ccn_f1.grid(row=0, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.ccn_b_open.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_lb_openFiles.grid(column=1, row=2, columnspan=3, rowspan=1, sticky=tk.NSEW, padx=5, pady=5)
        self.ccn_cb_forceReload.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)

    def create_output_frame_ccn(self, mainFrame):
        """
        Draw the gui frame for data output options
        KJ - new version using grid
        """
        print('ccnc.py create_output_frame')
        # create output path dialog
        self.ccn_f2 = tk.LabelFrame(mainFrame, text='Output data')
        self.ccn_b_output = tk.Button(self.ccn_f2,
                                  text='Change output directory',
                                  command=self.output_path_dialog)
        self.ccn_t_outputPath = tk.Entry(self.ccn_f2)

        # Create output filetype combobox
        filetypes = ['netcdf', 'hdf', 'csv']
        self.ccn_lb1 = tk.Label(self.ccn_f2, text='Select output filetype')
        self.ccn_cb_output_filetype = ttk.Combobox(self.ccn_f2,
                                               values=filetypes,
                                               state='readonly',
                                               width=10)
        self.ccn_cb_output_filetype.current(1)  # set selection
        self.ccn_cb_output_filetype.bind('<<ComboboxSelected>>', self.launch_netcdf_input)

        # Create output file frequency combobox
        file_freq = ['Single file', 'Daily files', 'Weekly files', 'Monthly files']
        self.ccn_lb2 = tk.Label(self.ccn_f2, text='Select output frequency')
        self.ccn_cb_file_freq = ttk.Combobox(self.ccn_f2,
                                         values=file_freq,
                                         state='readonly',
                                         width=15)
        self.ccn_cb_file_freq.current(2)  # set selection

        # Create output output time resolution combobox
        output_time_resolution = ['1 second', '5 seconds', '10 seconds', '15 seconds',
                                  '30 seconds', '1 minute', '5 minutes', '10 minutes',
                                  '15 minutes', '30 minutes', '1 hour', '6 hours',
                                  '12 hours', '1 day']
        self.ccn_lb3 = tk.Label(self.ccn_f2, text='Select output time resolution')
        self.ccn_cb_output_time_resolution = ttk.Combobox(self.ccn_f2,
                                                      values=output_time_resolution,
                                                      state='readonly',
                                                      width=15)
        self.ccn_cb_output_time_resolution.current(0)  # set selection to 1 second

        # Create output supersaturation checkbox
        self.ccn_split_SS = tk.IntVar()
        self.ccn_cb_SS = tk.Checkbutton(self.ccn_f2,
                                    text='Split by supersaturation',
                                    variable=self.ccn_split_SS)
        self.ccn_cb_SS.select()

        # place all Output Frame elements using grid
        self.ccn_f2.grid(row=2, column=0, rowspan=4, columnspan=3, sticky=tk.NSEW, padx=5)
        self.ccn_b_output.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_t_outputPath.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.ccn_lb1.grid(column=1, row=2, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_cb_output_filetype.grid(column=2, row=2, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.ccn_lb2.grid(column=1, row=3, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_cb_file_freq.grid(column=2, row=3, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.ccn_lb3.grid(column=1, row=4, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_cb_output_time_resolution.grid(column=2, row=4, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.ccn_cb_SS.grid(column=1, row=5, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)

    def create_processing_frame_ccn(self, mainFrame):
        """
        Draw the gui frame for data processing options
        KJ - new version using grid
        """
        self.globalMainFrame = mainFrame
        self.ccn_f3 = tk.LabelFrame(mainFrame, text='Processing options')

        # Data mask/removal frame
        self.ccn_f31 = tk.LabelFrame(self.ccn_f3, text='Data masking/removal')
        self.qc = tk.IntVar()
        self.ccn_cb_qc = tk.Checkbutton(self.ccn_f31,
                                    text='QC for internal parameters',
                                    variable=self.qc)
        self.ccn_cb_qc.select()
        self.ccn_f311 = tk.LabelFrame(self.ccn_f31, text='Select file with mask events (optional)')
        self.ccn_tb2 = tk.Entry(self.ccn_f311, width=40)
        self.ccn_b311 = tk.Button(self.ccn_f311,
                              text='Browse',
                              command=self.ask_mask_file)
        # help tooltip
        self.ccn_l311 = tk.Label(self.ccn_f311, text=u'\u2754')
        ToolTip.ToolTip(self.ccn_l311,
                        'Choose an ASCII file where the 1st and 2nd columns \
                        are the start and end timestamps of the period to be \
                        removed. Any additional columns (such as description \
                        columns) will be ignored.')

        self.ccn_f32 = tk.LabelFrame(self.ccn_f3, text='Flow calibration')
        self.ccn_f321 = tk.LabelFrame(self.ccn_f32, text='Select file with flow calibration data (optional)')
        self.ccn_tb3 = tk.Entry(self.ccn_f321, width=40)
        self.ccn_b321 = tk.Button(self.ccn_f321,
                              text='Browse',
                              command=self.ask_flowcal_file)
         # help tooltip
        self.ccn_l321 = tk.Label(self.ccn_f321, text=u'\u2754')
        ToolTip.ToolTip(self.ccn_l321,
                        'Choose an ASCII file where the 1st column is the  \
                        timestamp of the flow measurement, and the second \
                        column is the measured flow rate in units of \
                        L/min or LPM')

        self.ccn_lb_flow_rate_set = tk.Label(self.ccn_f32, text='Set flow rate (LPM)')
        self.ccn_tb_flow_rate_set = tk.Entry(self.ccn_f32, width=10)
        self.ccn_tb_flow_rate_set.insert(tk.END, 0.5)
        self.ccn_lb_flow_rate_fit = tk.Label(self.ccn_f32, text='Polynomial degree for flow rate fit')
        self.ccn_tb_flow_rate_fit = tk.Entry(self.ccn_f32, width=10)
        self.ccn_tb_flow_rate_fit.insert(tk.END, 2)

        self.ccn_f322 = tk.LabelFrame(self.ccn_f3, text='Supersaturation calibration for atmospheric pressure')
        self.ccn_lb322 = tk.Label(self.ccn_f322, text='Corrects reported SS for changes in atm. pressure between cal. site & measurement site. If calibrated by DMT, cal. pressure is 830 hPa. Sea level pressure is 1010 hPa.', wraplength=350)
        self.correct4pressure = tk.IntVar()
        self.ccn_cb_pressCal = tk.Checkbutton(self.ccn_f322,
                                          text='Correct for pressure',
                                          variable=self.correct4pressure,
                                          onvalue=1, offvalue=0,
                                          command=self.grey_press_input)
        self.ccn_cb_pressCal.select()
        self.ccn_lb_calPress = tk.Label(self.ccn_f322, text='Cal. Pressure')
        self.ccn_tb_calPress = tk.Entry(self.ccn_f322, width=5)
        self.ccn_tb_calPress.insert(tk.END, 830)
        self.ccn_lb_units1 = tk.Label(self.ccn_f322, text='hPa')

        self.ccn_lb_measPress = tk.Label(self.ccn_f322, text='Meas. Pressure')
        self.ccn_tb_measPress = tk.Entry(self.ccn_f322, width=5)
        self.ccn_tb_measPress.insert(tk.END, 1010)
        self.ccn_lb_units2 = tk.Label(self.ccn_f322, text='hPa')

        self.ccn_bt_go = tk.Button(self.ccn_f3,
                               text='GO',
                               command=self.load_and_process,
                               font='Times 18 bold',
                               width=15)

        # place all Processing Frame elements using grid
        self.ccn_f3.grid(row=7, column=0, rowspan=30, columnspan=3, sticky=tk.NSEW, padx=5)
        self.ccn_f31.grid(row=10, column=0, rowspan=7, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.ccn_cb_qc.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_f311.grid(row=2, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_tb2.grid(row=3, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_b311.grid(row=3, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_l311.grid(row=3, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.ccn_f32.grid(row=18, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.ccn_f321.grid(row=18, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.ccn_tb3.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_b321.grid(row=1, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_l321.grid(row=1, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.ccn_lb_flow_rate_set.grid(row=20, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_tb_flow_rate_set.grid(row=20, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_lb_flow_rate_fit.grid(row=21, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_tb_flow_rate_fit.grid(row=21, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.ccn_f322.grid(row=22, column=1, rowspan=6, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.ccn_lb322.grid(row=22, column=1, rowspan=4, columnspan=3, sticky=tk.NW, padx=5, pady=5)
        self.ccn_cb_pressCal.grid(row=26, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_lb_calPress.grid(row=27, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_tb_calPress.grid(row=27, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_lb_units1.grid(row=27, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.ccn_lb_measPress.grid(row=28, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_tb_measPress.grid(row=28, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.ccn_lb_units2.grid(row=28, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.ccn_bt_go.grid(row=29, column=1, columnspan=3, rowspan=1, sticky=tk.S, padx=5, pady=5)

#-----------------------------------------------------------
# Plot
#-----------------------------------------------------------
    def create_plot_ccn(self, data_list):
        '''
        plot data!
        '''
        # Combine multiple files into one DataFrame.
        frames = []
        for d in data_list:
            tmp_frame = pd.read_csv(d['path'])
            frames.append(tmp_frame)

        df = pd.concat(frames)

        df.columns = [c.replace(' ', '_') for c in df.columns]  # remove spaces in column names
        # print list of all the column names
        # print('all columns:', df.columns.tolist())

        # time for X axis
        # get 24/04/2016 from df['timestamp']
        # get 23:00:01 from df['Time']
        dates = pd.Series(df['timestamp'])
        times = pd.Series(df['Time'])
        dates = dates.str.split().str.get(0)            # get just the date part of timestamp
        new_time = pd.to_datetime(dates + ' ' + times)  # create new datetime dataframe

        # define test columns for the Y axis
        columns = [df['T1_Read'], df['T_Inlet'], df['Laser_Current']]
        names = ['T1_Read', 'T_Inlet', 'Laser Current']

        self.ccn_f4 = tk.LabelFrame(self.globalMainFrame, text='Data Plot')
        self.ccn_f4.grid(row=0, column=5, rowspan=20, columnspan=20, sticky=(tk.NSEW), padx=20)

        PLOT = AnnotateablePlot(self.ccn_f4, new_time, columns, names)

#-----------------------------------------------------------
# GUI Functionality
#-----------------------------------------------------------
    def raw_file_dialog(self):
        '''Prompts user to select input files'''
        self.ccn_files_raw = filedialog.askopenfilenames()
        self.ccn_raw_path = os.path.dirname(self.ccn_files_raw[0])

        # Update the text box
        self.ccn_lb_openFiles.delete(0, tk.END)
        for i in range(0, len(self.ccn_files_raw)):
            self.ccn_lb_openFiles.insert(tk.END, self.ccn_files_raw[i])
        try:
            if self.ccn_output_path == '':
                self.update_output_path()
        except AttributeError:
            self.update_output_path()
        return

    def update_output_path(self):
        self.ccn_t_outputPath.insert(tk.END, self.ccn_raw_path)
        self.ccn_output_path = self.ccn_raw_path

    def browse_for_file(self):
        '''Prompts user to select input file'''
        file = filedialog.askopenfilename()
        return file

    def ask_mask_file(self):
        ''' Asks for the mask file input and shows it in the gui'''
        self.ccn_mask_file = self.browse_for_file()
        self.ccn_tb2.insert(tk.END, self.ccn_mask_file)
        return

    def ask_flowcal_file(self):
        ''' Asks for the flow cal file input and shows it in the gui'''
        self.ccn_flowcal_file = self.browse_for_file()
        self.ccn_tb3.insert(tk.END, self.ccn_flowcal_file)
        return

    def output_path_dialog(self):
        '''Selecting output path, if not chosen, use the input directory'''
        self.ccn_output_path = filedialog.askdirectory()
        self.ccn_t_outputPath.delete(0, tk.END)
        self.ccn_t_outputPath.insert(tk.END, self.ccn_output_path)

    def launch_netcdf_input(self, event):
        '''
        Launches netcdf input when the combobox option is selected
        '''
        if self.ccn_cb_output_filetype.get() == 'netcdf':
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

    def grey_press_input(self):
        '''
        Disables input into the pressure fields if the checkbox isn't ticked.
        '''
        if self.correct4pressure.get() == 0:
            self.ccn_tb_calPress.configure(state='disabled')
            self.ccn_tb_measPress.configure(state='disabled')
        elif self.correct4pressure.get() == 1:
            self.ccn_tb_calPress.configure(state='normal')
            self.ccn_tb_measPress.configure(state='normal')

if __name__ == '__main__':
    ccn_processing().mainloop()
