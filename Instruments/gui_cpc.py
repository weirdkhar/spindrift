'''
Code for the gui of the processing of aerosol gear

Written by Ruhi Humphries
2017

Useful documentation:
    http://www.tkdocs.com/tutorial/widgets.html
    http://pyinmyeye.blogspot.com.au/2012/08/tkinter-combobox-demo.html
    http://www.python-course.eu/tkinter_layout_management.php
'''
import re
import os
import threading
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from Instruments.gui_base import GenericBaseGui

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import atmoscripts
import ToolTip
import Instruments.CPC_TSI as CPC_TSI

class cpc_processing(GenericBaseGui):
    '''
    CPC processing
    '''
    def __init__(self, isapp=True):
        """
        Initialise the gui
        KJ - new version using grid
        """
        tk.Frame.__init__(self, name='cpcprocessing')
        print('init cpc processing')
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.master.title('CPC TSI Processing')
        self.master.geometry('1760x1160')    # original 880x560
        self.isapp = isapp
        self.globalMainFrame = ''

    def __repr__(self):
        return 'cpc_processing()'

    def __str__(self):
        return 'member of cpc_processing'

    def load_and_process(self):
        '''
        Once all parameters have been chosen, checks all the input values and
        begins the processing.
        '''

        # Initialise
        msg = 'There is an error with your input! \n'
        # Check input variables
        try:
            self.cpc_files_raw
            print('self.cpc_files_raw = ', self.cpc_files_raw)
        except AttributeError:
        	# if self.cpc_files_raw is None:
            msg = msg + '\n Please select raw input files'

        try:
            self.cpc_output_path
            if not os.path.exists(self.cpc_output_path):
                msg = msg + '\n Chosen output path does not exist'
        except AttributeError:
            msg = msg + '\n Please select output path'

        if msg != 'There is an error with your input! \n':
            self._alert_bad_input(msg)
            return

        if self.cpc_cb_output_filetype.get() == 'netcdf':
            if os.path.exists(self.cpc_output_path):
                os.chdir(self.cpc_output_path)

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

        if self.cpc_cb_output_time_resolution.get() == '1 second':
            output_time_res[0] = True
        elif self.cpc_cb_output_time_resolution.get() == '5 seconds':
            output_time_res[1] = True
        elif self.cpc_cb_output_time_resolution.get() == '10 seconds':
            output_time_res[2] = True
        elif self.cpc_cb_output_time_resolution.get() == '15 seconds':
            output_time_res[3] = True
        elif self.cpc_cb_output_time_resolution.get() == '30 seconds':
            output_time_res[4] = True
        elif self.cpc_cb_output_time_resolution.get() == '1 minute':
            output_time_res[5] = True
        elif self.cpc_cb_output_time_resolution.get() == '5 minutes':
            output_time_res[6] = True
        elif self.cpc_cb_output_time_resolution.get() == '10 minutes':
            output_time_res[7] = True
        elif self.cpc_cb_output_time_resolution.get() == '15 minutes':
            output_time_res[8] = True
        elif self.cpc_cb_output_time_resolution.get() == '30 minutes':
            output_time_res[9] = True
        elif self.cpc_cb_output_time_resolution.get() == '1 hour':
            output_time_res[10] = True
        elif self.cpc_cb_output_time_resolution.get() == '3 hours':
            output_time_res[11] = True
        elif self.cpc_cb_output_time_resolution.get() == '6 hours':
            output_time_res[12] = True
        elif self.cpc_cb_output_time_resolution.get() == '12 hours':
            output_time_res[13] = True
        elif self.cpc_cb_output_time_resolution.get() == '1 day':
            output_time_res[14] = True

        if self.cpc_cb_file_freq.get() == 'Single file':
            concat_file_freq = 'all'
        elif self.cpc_cb_file_freq.get() == 'Daily files':
            concat_file_freq = 'daily'
        elif self.cpc_cb_file_freq.get() == 'Weekly files':
            concat_file_freq = 'weekly'
        elif self.cpc_cb_file_freq.get() == 'Monthly files':
            concat_file_freq = 'monthly'
        else:
            print('Something has gone terribly wrong here...')
            self.destroy()

        try:
            flow_cal_df = CPC_TSI.load_flow_cals(file_FULLPATH=self.flowcal_file)
        except:
            flow_cal_df = None

        try:
            mask_df = CPC_TSI.load_manual_mask(file_FULLPATH=self.mask_file)
        except:
            mask_df = None

        if self.cpc_cb_output_filetype.get() == 'netcdf':
            output_filetype = 'nc'
        elif self.cpc_cb_output_filetype.get() == 'hdf':
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

    def loadAndProcess_Multithread(self,
                                   output_filetype,
                                   output_time_res,
                                   concat_file_freq,
                                   mask_df,
                                   flow_cal_df):

        # Call processing function
        CPC_TSI.LoadAndProcess(cn_raw_path=self.cpc_raw_path,
                               cn_output_path=self.cpc_output_path,
                               cn_output_filetype=output_filetype,
                               filename_base='CN3',
                               force_reload_from_source=self.cpc_forceReload.get(),
                               output_time_resolution=output_time_res,
                               concat_file_frequency=concat_file_freq,
                               input_filelist=list(self.cpc_files_raw),
                               NeedsTZCorrection=self.cpc_correct4TZ.get(),
                               CurrentTZ=float(self.cpc_tb_TZcurrent.get()),
                               OutputTZ=float(self.cpc_tb_TZdesired.get()),
                               mask_period_timestamp_df=mask_df,
                               flow_cal_df=flow_cal_df,
                               CN_flow_setpt=float(self.cpc_tb_flow_rate_set.get())*1000,
                               CN_flow_polyDeg=float(self.cpc_tb_flow_rate_fit.get()),
                               gui_mode=True,
                               gui_mainloop=self.w_status)

        self.finished_window()

#-----------------------------------------------------------
# GUI Widgets
#-----------------------------------------------------------
    def create_input_frame_cpc(self, mainFrame):
        """
        Draw the gui frame for data input options
        KJ - new version using grid
        """
        self.cpc_f1 = tk.LabelFrame(mainFrame, text='Input data')
        self.cpc_b_open = tk.Button(self.cpc_f1, text='Select raw files', command=self.raw_file_dialog_cpc)
        self.cpc_lb_openFiles = tk.Listbox(self.cpc_f1) # original listbox had a scroll bar added
        self.cpc_forceReload = tk.IntVar()
        self.cpc_cb_forceReload = tk.Checkbutton(self.cpc_f1,
                                             text='Force reload from source',
                                             variable=self.cpc_forceReload)
        self.cpc_cb_forceReload.select()

        # place all Input Frame elements using grid
        self.cpc_f1.grid(row=0, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.cpc_b_open.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_lb_openFiles.grid(column=1, row=2, columnspan=3, rowspan=1, sticky=tk.NSEW, padx=5, pady=5)
        self.cpc_cb_forceReload.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)

    def create_output_frame_cpc(self, mainFrame):
        """
        Draw the gui frame for data output options
        KJ - new version using grid
        """
        print('cpc.py create_output_frame')
        # create output path dialog
        self.cpc_f2 = tk.LabelFrame(mainFrame, text='Output data')
        self.cpc_b_output = tk.Button(self.cpc_f2,
                                  text='Change output directory',
                                  command=self.output_path_dialog_cpc)
        self.cpc_t_outputPath = tk.Entry(self.cpc_f2)

         # Create output filetype combobox
        filetypes = ['netcdf', 'hdf', 'csv']
        self.cpc_lb1 = tk.Label(self.cpc_f2, text='Select output filetype')
        self.cpc_cb_output_filetype = ttk.Combobox(self.cpc_f2,
                                               values=filetypes,
                                               state='readonly',
                                               width=10)
        self.cpc_cb_output_filetype.current(1)  # set selection
        self.cpc_cb_output_filetype.bind('<<ComboboxSelected>>', self.launch_netcdf_input_cpc)

        file_freq=['Single file', 'Daily files', 'Weekly files', 'Monthly files']
        self.cpc_lb2 = tk.Label(self.cpc_f2, text='Select output frequency')
        self.cpc_cb_file_freq = ttk.Combobox(self.cpc_f2,
                                         values=file_freq,
                                         state='readonly',
                                         width=15)
        self.cpc_cb_file_freq.current(2)  # set selection

        # Create output output time resolution combobox
        output_time_resolution = ['1 second', '5 seconds', '10 seconds', '15 seconds',
                                  '30 seconds', '1 minute', '5 minutes', '10 minutes',
                                  '15 minutes', '30 minutes', '1 hour', '6 hours',
                                  '12 hours', '1 day']
        self.cpc_lb3 = tk.Label(self.cpc_f2, text='Select output time resolution')
        self.cpc_cb_output_time_resolution = ttk.Combobox(self.cpc_f2,
                                                      values=output_time_resolution,
                                                      state='readonly',
                                                      width=15)
        self.cpc_cb_output_time_resolution.current(0)  # set selection to 1 second

        # place all Output Frame elements using grid
        self.cpc_f2.grid(row=2, column=0, rowspan=4, columnspan=3, sticky=tk.NSEW, padx=5)
        self.cpc_b_output.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_t_outputPath.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.cpc_lb1.grid(column=1, row=2, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_cb_output_filetype.grid(column=2, row=2, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.cpc_lb2.grid(column=1, row=3, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_cb_file_freq.grid(column=2, row=3, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.cpc_lb3.grid(column=1, row=4, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_cb_output_time_resolution.grid(column=2, row=4, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)

    def create_processing_frame_cpc(self, mainFrame):
        """
        Draw the gui frame for data processing options
        KJ - new version using grid
        """
        self.cpc_f3 = tk.LabelFrame(mainFrame, text='Processing options')
        self.cpc_f31 = tk.LabelFrame(self.cpc_f3, text='Data masking/removal')
        self.cpc_f311 = tk.LabelFrame(self.cpc_f31, text='Select file with mask events (optional)')
        self.cpc_tb2 = tk.Entry(self.cpc_f311, width=40)
        self.cpc_b311 = tk.Button(self.cpc_f311,
                              text='Browse',
                              command=self.ask_mask_file_cpc)

        # help tooltip
        self.cpc_l311 = tk.Label(self.cpc_f311, text=u'\u2754')
        ToolTip.ToolTip(self.cpc_l311,
                        'Choose an ASCII file where the 1st and 2nd columns \
                        are the start and end timestamps of the period to be \
                        removed. Any additional columns (such as description \
                        columns) will be ignored.')

        self.cpc_f32 = tk.LabelFrame(self.cpc_f3, text='Flow calibration')
        self.cpc_f321 = tk.LabelFrame(self.cpc_f32, text='Select file with flow calibration data (optional)')
        self.cpc_tb3 = tk.Entry(self.cpc_f321, width=40)
        self.cpc_b321 = tk.Button(self.cpc_f321,
                              text='Browse',
                              command=self.ask_flowcal_file_cpc)
         # help tooltip
        self.cpc_l321 = tk.Label(self.cpc_f321, text=u'\u2754')
        ToolTip.ToolTip(self.cpc_l321,
                        'Choose an ASCII file where the 1st column is the  \
                        timestamp of the flow measurement, and the second \
                        column is the measured flow rate in units of \
                        L/min or LPM')

        self.cpc_lb_flow_rate_set = tk.Label(self.cpc_f32, text='Set flow rate (LPM)')
        self.cpc_tb_flow_rate_set = tk.Entry(self.cpc_f32, width=10)
        self.cpc_tb_flow_rate_set.insert(tk.END, 1.0)
        self.cpc_lb_flow_rate_fit = tk.Label(self.cpc_f32, text='Polynomial degree for flow rate fit')
        self.cpc_tb_flow_rate_fit = tk.Entry(self.cpc_f32, width=10)
        self.cpc_tb_flow_rate_fit.insert(tk.END, 2.0)

        self.cpc_lb_flow_rate_set.grid(row=16, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_tb_flow_rate_set.grid(row=16, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_lb_flow_rate_fit.grid(row=17, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_tb_flow_rate_fit.grid(row=17, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cpc_f322 = tk.LabelFrame(self.cpc_f3, text='Time Zone Correction')
        self.cpc_lb322 = tk.Label(self.cpc_f322, text = '''Corrects timestamp for offset created by AIM \
outputting the timestamps based on the export computer's settings, rather \
than the measurement computer's time zone settings.''', wraplength=350)

        self.cpc_correct4TZ = tk.IntVar()
        self.cpc_cb_TZcorrection = tk.Checkbutton(self.cpc_f322,
                                           text='Correct Time Zone',
                                           variable=self.cpc_correct4TZ,
                                           onvalue=1, offvalue=0,
                                           command=self.grey_press_input_cpc)

        self.cpc_lb_TZcurrent = tk.Label(self.cpc_f322, text='Export PCs TZ (current)')
        self.cpc_tb_TZcurrent = tk.Entry(self.cpc_f322, width=5)
        self.cpc_tb_TZcurrent.insert(tk.END, 0)
        self.cpc_lb_units1 = tk.Label(self.cpc_f322, text='hrs from UTC')

        self.cpc_lb_TZdesired = tk.Label(self.cpc_f322, text='Meas. PCs TZ (desired)')
        self.cpc_tb_TZdesired = tk.Entry(self.cpc_f322, width=5)
        self.cpc_tb_TZdesired.insert(tk.END, 0)
        self.cpc_lb_units2 = tk.Label(self.cpc_f322, text='hrs from UTC')

        self.cpc_bt_go = tk.Button(self.cpc_f3,
                               text='GO',
                               command=self.load_and_process,
                               font='Times 18 bold',
                               width=15)

         # place all Processing Frame elements using grid
        self.cpc_f3.grid(row=10, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5)
        self.cpc_f31.grid(row=10, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.cpc_f311.grid(row=2, column=0, rowspan=1, columnspan=3, sticky=tk.NW, padx=5, pady=5)
        self.cpc_tb2.grid(row=3, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_b311.grid(row=3, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_l311.grid(row=3, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cpc_f32.grid(row=14, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.cpc_f321.grid(row=14, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.cpc_tb3.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_b321.grid(row=1, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_l321.grid(row=1, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cpc_f322.grid(row=18, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.cpc_lb322.grid(row=20, column=1, rowspan=3, columnspan=3, sticky=tk.NW, padx=5, pady=5)
        self.cpc_cb_TZcorrection.grid(row=24, column=1, rowspan=2, columnspan=3, sticky=tk.N, padx=5, pady=5)

        self.cpc_lb_TZcurrent.grid(row=27, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_tb_TZcurrent.grid(row=27, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_lb_units1.grid(row=27, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cpc_lb_TZdesired.grid(row=28, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_tb_TZdesired.grid(row=28, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cpc_lb_units2.grid(row=28, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cpc_bt_go.grid(row=30, column=1, columnspan=3, rowspan=1, sticky=tk.S, padx=5, pady=5)

#-----------------------------------------------------------
# Plot!
#-----------------------------------------------------------
    def create_plot_cpc(self, mainFrame):
        '''
        test data - open web statistics data file and create a bar chart
        '''
        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        requests = [5, 13, 18, 7, 8, 45, 54, 33, 12, 78, 99, 110]
        pages = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84]

        fig1 = Figure(figsize=(12, 10), dpi=100)
        ax = fig1.add_subplot(1, 1, 1)

        # create bar chart
        n = len(hour)
        ind = np.arange(n)
        width = 0.5

        plot1 = ax.bar(ind, requests, width, color="#ccdbfa")
        plot2 = ax.bar(ind+width, pages, width, color="#3f537a")

        # create labels & legend
        ax.set_ylabel('Number', color="#4F5561", fontsize=12)
        ax.set_xlabel('Hour', color="#4F5561", fontsize=12)
        ax.legend((plot1[0], plot2[0]), ('Requests', 'Pages'))

        self.f4 = tk.LabelFrame(mainFrame, text='Data Plot')
        self.f4.grid(row=0, column=5, rowspan=30, columnspan=20, sticky=(tk.NSEW), padx=20)

        canvas = FigureCanvasTkAgg(fig1, self.f4)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=20, rowspan=30, sticky=(tk.NSEW), padx=5, pady=5)

        self.f41 = tk.LabelFrame(self.f4, text='Navigation Tools')
        self.f41.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=(tk.SW), padx=5)

        toolbar = NavigationToolbar2TkAgg(canvas, self.f41)
        toolbar.update()
        canvas._tkcanvas.grid(row=0, column=0, rowspan=1, columnspan=2, padx=5, pady=5)

#-----------------------------------------------------------
# GUI Functionality
#-----------------------------------------------------------
    def raw_file_dialog_cpc(self):
        '''Prompts user to select input files'''
        self.cpc_files_raw = filedialog.askopenfilenames()
        self.cpc_raw_path = os.path.dirname(self.cpc_files_raw[0])

        # Update the text box
        self.cpc_lb_openFiles.delete(0, tk.END)
        for i in range(0, len(self.cpc_files_raw)):
            self.cpc_lb_openFiles.insert(tk.END, self.cpc_files_raw[i])
        try:
            if self.cpc_output_path == '':
                self.update_output_path_cpc()
        except AttributeError:
            self.update_output_path_cpc()
        return

    def update_output_path_cpc(self):
        self.cpc_t_outputPath.insert(tk.END, self.cpc_raw_path)
        self.cpc_output_path = self.cpc_raw_path

    def browse_for_file_cpc(self):
        '''Prompts user to select input file'''
        file_cpc = filedialog.askopenfilename()
        return file_cpc

    def ask_mask_file_cpc(self):
        ''' Asks for the mask file input and shows it in the gui'''
        self.mask_file = self.browse_for_file_cpc()
        self.cpc_tb2.insert(tk.END, self.cpc_mask_file)
        return

    def ask_flowcal_file_cpc(self):
        ''' Asks for the flow cal file input and shows it in the gui'''
        self.cpc_flowcal_file = self.browse_for_file_cpc()
        self.cpc_tb3.insert(tk.END, self.cpc_flowcal_file)
        return

    def output_path_dialog_cpc(self):
        '''Selecting output path, if not chosen, use the input directory'''
        self.cpc_output_path = filedialog.askdirectory()
        self.cpc_t_outputPath.delete(0, tk.END)
        self.cpc_t_outputPath.insert(tk.END, self.cpc_output_path)

    def launch_netcdf_input_cpc(self, event):
        '''
        Launches netcdf input when the combobox option is selected
        '''
        if self.cpc_cb_output_filetype.get() == 'netcdf':
            self._build_netcdf_input_window()

    def close_netcdf_window_cpc(self):
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

    def grey_press_input_cpc(self):
        '''
        Disables input into the pressure fields if the checkbox isn't ticked.
        '''
        self.cpc_correct4TZ
        if self.cpc_correct4TZ.get() == 0:
            self.cpc_tb_TZcurrent.configure(state='disabled')
            self.cpc_tb_TZdesired.configure(state='disabled')
        elif self.cpc_correct4TZ.get() == 1:
            self.cpc_tb_TZcurrent.configure(state='normal')
            self.cpc_tb_TZdesired.configure(state='normal')

if __name__ == '__main__':
    cpc_processing().mainloop()
