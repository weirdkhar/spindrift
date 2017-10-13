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
import threading
import pandas as pd
import tkinter as tk
from tkinter import ttk
import numpy as np

import Instruments.CCNC as CCNC
from Instruments.gui_base import GenericBaseGui
import ToolTip

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class ccn_processing(GenericBaseGui):
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
        self.build_widgets()
        self.globalMainFrame = ''

    def __repr__(self):
        return 'ccn_processing()'

    def __str__(self):
        return 'member of ccn_processing'

    def loadAndProcess_Multithread(self,
                                   output_filetype,
                                   output_time_res,
                                   concat_file_freq,
                                   mask_df,
                                   flow_cal_df):

        # Call processing function
        final_file = CCNC.LoadAndProcess(ccn_raw_path=self.raw_path,
                            ccn_output_path=self.output_path,
                            ccn_output_filetype=output_filetype,
                            filename_base='CCN',
                            force_reload_from_source=self.forceReload.get(),
                            split_by_supersaturation=self.split_SS.get(),
                            QC=self.qc.get(),
                            output_time_resolution=output_time_res,
                            concat_file_frequency=concat_file_freq,
                            mask_period_timestamp_df=mask_df,
                            flow_cal_df=flow_cal_df,
                            flow_setpt=float(self.tb_flow_rate_set.get())*1000,
                            flow_polyDeg=float(self.tb_flow_rate_fit.get()),
                            calibrate_for_pressure=self.cb_pressCal,
                            press_cal=float(self.tb_calPress.get()),
                            press_meas=float(self.tb_measPress.get()),
                            input_filelist=list(self.files_raw),
                            gui_mode=True,
                            gui_mainloop=self.w_status)

        self.finished_window()  # draw Data Processing Complete! window
        self.create_plot_ccn(final_file)

#-----------------------------------------------------------
# GUI Functionality
#-----------------------------------------------------------
    def grey_press_input(self):
        '''
        Disables input into the pressure fields if the checkbox isn't ticked.
        '''
        if self.correct4pressure.get() == 0:
            self.tb_calPress.configure(state='disabled')
            self.tb_measPress.configure(state='disabled')
        elif self.correct4pressure.get() == 1:
            self.tb_calPress.configure(state='normal')
            self.tb_measPress.configure(state='normal')

#-----------------------------------------------------------
# GUI Widgets
#-----------------------------------------------------------
    def create_output_frame_ccn(self, mainFrame):
        """
        Draw the gui frame for data output options
        KJ - new version using grid
        """
        print('ccnc.py create_output_frame')
        # create output path dialog
        self.f2 = tk.LabelFrame(mainFrame, text='Output data')
        self.b_output = tk.Button(self.f2,
                                  text='Change output directory',
                                  command=self.output_path_dialog)
        self.t_outputPath = tk.Entry(self.f2)

        # Create output filetype combobox
        filetypes = ['netcdf', 'hdf', 'csv']
        self.lb1 = tk.Label(self.f2, text='Select output filetype')
        self.cb_output_filetype = ttk.Combobox(self.f2,
                                               values=filetypes,
                                               state='readonly',
                                               width=10)
        self.cb_output_filetype.current(1)  # set selection
        self.cb_output_filetype.bind('<<ComboboxSelected>>', self.launch_netcdf_input)

        # Create output file frequency combobox
        file_freq = ['Single file', 'Daily files', 'Weekly files', 'Monthly files']
        self.lb2 = tk.Label(self.f2, text='Select output frequency')
        self.cb_file_freq = ttk.Combobox(self.f2,
                                         values=file_freq,
                                         state='readonly',
                                         width=15)
        self.cb_file_freq.current(2)  # set selection

        # Create output output time resolution combobox
        output_time_resolution = ['1 second', '5 seconds', '10 seconds', '15 seconds',
                                  '30 seconds', '1 minute', '5 minutes', '10 minutes',
                                  '15 minutes', '30 minutes', '1 hour', '6 hours',
                                  '12 hours', '1 day']
        self.lb3 = tk.Label(self.f2, text='Select output time resolution')
        self.cb_output_time_resolution = ttk.Combobox(self.f2,
                                                      values=output_time_resolution,
                                                      state='readonly',
                                                      width=15)
        self.cb_output_time_resolution.current(0)  # set selection to 1 second

        # Create output supersaturation checkbox
        self.split_SS = tk.IntVar()
        self.cb_SS = tk.Checkbutton(self.f2,
                                    text='Split by supersaturation',
                                    variable=self.split_SS)
        self.cb_SS.select()

        # place all Output Frame elements using grid
        self.f2.grid(row=2, column=0, rowspan=3, columnspan=3, sticky=tk.NSEW, padx=5)
        self.b_output.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.t_outputPath.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.lb1.grid(column=1, row=2, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_output_filetype.grid(column=2, row=2, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.lb2.grid(column=1, row=3, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_file_freq.grid(column=2, row=3, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.lb3.grid(column=1, row=3, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_output_time_resolution.grid(column=2, row=3, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.cb_SS.grid(column=1, row=4, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)

    def create_processing_frame_ccn(self, mainFrame):
        """
        Draw the gui frame for data processing options
        KJ - new version using grid
        """
        self.globalMainFrame = mainFrame
        self.f3 = tk.LabelFrame(mainFrame, text='Processing options')

        # Data mask/removal frame
        self.f31 = tk.LabelFrame(self.f3, text='Data masking/removal')
        self.qc = tk.IntVar()
        self.cb_qc = tk.Checkbutton(self.f31,
                                    text='QC for internal parameters',
                                    variable=self.qc)
        self.cb_qc.select()
        self.f311 = tk.LabelFrame(self.f31, text='Select file with mask events (optional)')
        self.tb2 = tk.Entry(self.f311, width=40)
        self.b311 = tk.Button(self.f311,
                              text='Browse',
                              command=self.ask_mask_file)
        # help tooltip
        self.l311 = tk.Label(self.f311, text=u'\u2754')
        ToolTip.ToolTip(self.l311,
                        'Choose an ASCII file where the 1st and 2nd columns \
                        are the start and end timestamps of the period to be \
                        removed. Any additional columns (such as description \
                        columns) will be ignored.')

        self.f32 = tk.LabelFrame(self.f3, text='Flow calibration')
        self.f321 = tk.LabelFrame(self.f32, text='Select file with flow calibration data (optional)')
        self.tb3 = tk.Entry(self.f321, width=40)
        self.b321 = tk.Button(self.f321,
                              text='Browse',
                              command=self.ask_flowcal_file)
         # help tooltip
        self.l321 = tk.Label(self.f321, text=u'\u2754')
        ToolTip.ToolTip(self.l321,
                        'Choose an ASCII file where the 1st column is the  \
                        timestamp of the flow measurement, and the second \
                        column is the measured flow rate in units of \
                        L/min or LPM')

        self.lb_flow_rate_set = tk.Label(self.f32, text='Set flow rate (LPM)')
        self.tb_flow_rate_set = tk.Entry(self.f32, width=10)
        self.tb_flow_rate_set.insert(tk.END, 0.5)
        self.lb_flow_rate_fit = tk.Label(self.f32, text='Polynomial degree for flow rate fit')
        self.tb_flow_rate_fit = tk.Entry(self.f32, width=10)
        self.tb_flow_rate_fit.insert(tk.END, 2)

        self.f322 = tk.LabelFrame(self.f3, text='Supersaturation calibration for atmospheric pressure')
        self.lb322 = tk.Label(self.f322, text='Corrects reported SS for changes in atm. pressure between cal. site & measurement site. If calibrated by DMT, cal. pressure is 830 hPa. Sea level pressure is 1010 hPa.', wraplength=350)
        self.correct4pressure = tk.IntVar()
        self.cb_pressCal = tk.Checkbutton(self.f322,
                                          text='Correct for pressure',
                                          variable=self.correct4pressure,
                                          onvalue=1, offvalue=0,
                                          command=self.grey_press_input)
        self.cb_pressCal.select()
        self.lb_calPress = tk.Label(self.f322, text='Cal. Pressure')
        self.tb_calPress = tk.Entry(self.f322, width=5)
        self.tb_calPress.insert(tk.END, 830)
        self.lb_units1 = tk.Label(self.f322, text='hPa')

        self.lb_measPress = tk.Label(self.f322, text='Meas. Pressure')
        self.tb_measPress = tk.Entry(self.f322, width=5)
        self.tb_measPress.insert(tk.END, 1010)
        self.lb_units2 = tk.Label(self.f322, text='hPa')

        self.bt_go = tk.Button(self.f3,
                               text='GO',
                               command=self.load_and_process,
                               font='Times 18 bold',
                               width=15)

        # place all Processing Frame elements using grid
        self.f3.grid(row=6, column=0, rowspan=18, columnspan=3, sticky=tk.NSEW, padx=5)
        self.f31.grid(row=10, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.cb_qc.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.tb2.grid(row=3, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.b311.grid(row=3, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.l311.grid(row=3, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.f32.grid(row=14, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.f321.grid(row=14, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.tb3.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.b321.grid(row=1, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.l321.grid(row=1, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.lb_flow_rate_set.grid(row=16, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_flow_rate_set.grid(row=16, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_flow_rate_fit.grid(row=17, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_flow_rate_fit.grid(row=17, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.f322.grid(row=18, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.lb322.grid(row=1, column=1, rowspan=2, columnspan=3, sticky=tk.NW, padx=5, pady=5)
        self.cb_pressCal.grid(row=3, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_calPress.grid(row=4, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_calPress.grid(row=4, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_units1.grid(row=4, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.lb_measPress.grid(row=5, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_measPress.grid(row=5, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_units2.grid(row=5, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.bt_go.grid(row=24, column=1, columnspan=3, rowspan=1, sticky=tk.S, padx=5, pady=5)

    def create_plot_ccn(self, data):
        '''
        plot data!
        '''
        df = pd.read_csv(data['path'])
        df.columns = [c.replace(' ', '_') for c in df.columns]  # remove spaces in column names
        print(df['T1_Read'])

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        requests = [5, 13, 18, 7, 8, 45, 54, 33, 12, 78, 99, 110]
        pages = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84]

        fig1 = Figure(figsize=(13, 11), dpi=100)
        ax = fig1.add_subplot(1, 1, 1)

        # create bar chart
        n = len(df['timestamp'])
        ind = np.arange(n)
        width = 5


        # plot1 = ax.bar(ind, requests, width, color="#ccdbfa")
        # plot2 = ax.bar(ind+width, pages, width, color="#3f537a")

        plot1 = ax.scatter(ind, df['T1_Read'], width, color="#ccdbfa")
        plot2 = ax.scatter(ind+width, df['T_Inlet'], width, color="#3f537a")

        # create labels & legend
        ax.set_ylabel('Value', color="#4F5561", fontsize=12)
        ax.set_xlabel('Hour', color="#4F5561", fontsize=12)
        ax.legend((plot1, plot2), ('T1 Read', 'T inlet'))

        self.f4 = tk.LabelFrame(self.globalMainFrame, text='Data Plot')
        self.f4.grid(row=0, column=5, rowspan=20, columnspan=20, sticky=(tk.NSEW), padx=20)

        canvas = FigureCanvasTkAgg(fig1, self.f4)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=20, rowspan=20, sticky=(tk.NSEW), padx=5, pady=5)

        self.f41 = tk.LabelFrame(self.f4, text='Navigation Tools')
        self.f41.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=(tk.SW), padx=5)

        toolbar = NavigationToolbar2TkAgg(canvas, self.f41)
        toolbar.update()
        canvas._tkcanvas.grid(row=0, column=0, rowspan=1, columnspan=2, padx=5, pady=5)

if __name__ == '__main__':
    ccn_processing().mainloop()
