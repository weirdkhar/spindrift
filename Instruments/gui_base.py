'''
Generic gui base classes
Common classes to be inherited by ccn_proccesing and cpc_processing
Author: Kristina Johnson, Ruhi Humphries
'''

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import Instruments.CCNC

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import atmoscripts

class GenericBaseGui(tk.Frame):
    '''
    Common gui class to be inherited by ccn_proccesing and cpc_processing
    '''

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
            print('self.files_raw = ', self.files_raw)
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

        output_time_res = []
        for i in range(0, 15):
            output_time_res.append(False)

        if self.cb_output_time_resolution.get() == '1 second':
            output_time_res[0] = True
        elif self.cb_output_time_resolution.get() == '5 seconds':
            output_time_res[1] = True
        elif self.cb_output_time_resolution.get() == '10 seconds':
            output_time_res[2] = True
        elif self.cb_output_time_resolution.get() == '15 seconds':
            output_time_res[3] = True
        elif self.cb_output_time_resolution.get() == '30 seconds':
            output_time_res[4] = True
        elif self.cb_output_time_resolution.get() == '1 minute':
            output_time_res[5] = True
        elif self.cb_output_time_resolution.get() == '5 minutes':
            output_time_res[6] = True
        elif self.cb_output_time_resolution.get() == '10 minutes':
            output_time_res[7] = True
        elif self.cb_output_time_resolution.get() == '15 minutes':
            output_time_res[8] = True
        elif self.cb_output_time_resolution.get() == '30 minutes':
            output_time_res[9] = True
        elif self.cb_output_time_resolution.get() == '1 hour':
            output_time_res[10] = True
        elif self.cb_output_time_resolution.get() == '3 hours':
            output_time_res[11] = True
        elif self.cb_output_time_resolution.get() == '6 hours':
            output_time_res[12] = True
        elif self.cb_output_time_resolution.get() == '12 hours':
            output_time_res[13] = True
        elif self.cb_output_time_resolution.get() == '1 day':
            output_time_res[14] = True

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

        print('Loading data from file')

        thread = threading.Thread(target=self.loadAndProcess_Multithread,
                             	  args=(output_filetype,
                                  output_time_res,
                                  concat_file_freq,
                                  mask_df,
                                  flow_cal_df))
        thread.start()

#-----------------------------------------------------------
# GUI Functionality
#-----------------------------------------------------------
    def raw_file_dialog(self):
        '''Prompts user to select input files'''
        self.files_raw = filedialog.askopenfilenames()
        self.raw_path = os.path.dirname(self.files_raw[0])

        # Update the text box
        self.lb_openFiles.delete(0, tk.END)
        for i in range(0, len(self.files_raw)):
            self.lb_openFiles.insert(tk.END, self.files_raw[i])
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
# GUI Widgets
#-----------------------------------------------------------
    def build_widgets(self):
        """
        Draw the main grid for the gui, and place the frames for input, output and processing in it
        KJ - new version using grid
        """
        mainFrame = tk.Frame(self)
        mainFrame.grid(row=0, column=0, sticky=tk.NSEW)
        self.create_input_frame(mainFrame)
        self.create_output_frame(mainFrame)
        self.create_processing_frame(mainFrame)
        self.create_plot(mainFrame)

    def create_input_frame(self, mainFrame):
        """
        Draw the gui frame for data input options
        KJ - new version using grid
        """
        self.f1 = tk.LabelFrame(mainFrame, text='Input data')
        self.b_open = tk.Button(self.f1, text='Select raw files', command=self.raw_file_dialog)
        self.lb_openFiles = tk.Listbox(self.f1) # original listbox had a scroll bar added
        self.forceReload = tk.IntVar()
        self.cb_forceReload = tk.Checkbutton(self.f1,
                                             text='Force reload from source',
                                             variable=self.forceReload)
        self.cb_forceReload.select()

        # place all Input Frame elements using grid
        self.f1.grid(row=0, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.b_open.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_openFiles.grid(column=1, row=2, columnspan=3, rowspan=1, sticky=tk.NSEW, padx=5, pady=5)
        self.cb_forceReload.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)

#-----------------------------------------------------------
# Variable check window
#-----------------------------------------------------------
    def _alert_bad_input(self, message='Nothing to see here...'):
        """
        Draw the gui for the bad input alert
        """
        self.top = tk.Toplevel()
        self.top.title('Bad input!')
        self.top.geometry('%dx%d' % (300, 200))
        txt = tk.Message(self.top,
                         text=message,
                         justify=tk.CENTER,
                         width=300)
        txt.pack(fill='x')

        bt_ok = tk.Button(self.top, text='OK', command=self.dismiss)
        bt_ok.pack(side=tk.BOTTOM)

    def dismiss(self):
        self.top.destroy()

#-----------------------------------------------------------
# NetCDF Description input window
#-----------------------------------------------------------
    def _build_netcdf_input_window(self):
        """
        Draw the gui for netcdf input options
        """
        self.w_netcdf_input = tk.Toplevel()
        self.w_netcdf_input.title('NetCDF Input')
        self.w_netcdf_input.geometry('300x310')

        self.w_netcdf_input.description = tk.Label(self.w_netcdf_input, text='Please provide global attributes to be included in the self-describing NetCDF file\n', wraplength=300)
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
                                  text='OK',
                                  width=30,
                                  command=self.close_netcdf_window)
        self.nc_bt_ok.pack()

#-----------------------------------------------------------
# Processing status window
#-----------------------------------------------------------
    def _build_status_window(self):
        self.w_status = tk.Toplevel()
        self.w_status.geometry('800x500')

        self.w_status.txt_status = tk.Text(self.w_status, wrap='word')
        self.w_status.sb_status = tk.Scrollbar(self.w_status)
        self.w_status.txt_status.pack(pady=5, side=tk.LEFT, fill='both', expand=True)
        self.w_status.sb_status.pack(pady=5, side=tk.LEFT, fill='y')

        # Attach listbox to scrollbar
        self.w_status.txt_status.config(yscrollcommand=self.w_status.sb_status.set)
        self.w_status.sb_status.config(command=self.w_status.txt_status.yview)

        self.w_status.txt_status.tag_configure('stderr', foreground='#b22222')
        sys.stdout = TextRedirector(self.w_status.txt_status, 'stdout')
        sys.stderr = TextRedirector(self.w_status.txt_status, 'stderr')

    def finished_window(self):
        self.w_finished = tk.Toplevel()
        self.w_finished.geometry('300x100')
        txt = tk.Message(self.w_finished,
                         text='Data processing complete!',
                         justify=tk.CENTER,
                         width=300)
        txt.pack()
        bt_ok = tk.Button(self.w_finished,
                          text='OK',
                          command=self.finish)
        bt_ok.pack()

    def finish(self):
        self.w_finished.destroy()
        self.w_status.destroy()

#-----------------------------------------------------------
# Redirect standard out
#-----------------------------------------------------------
class TextRedirector(object):
    '''
    Redirect standard out to graphical user interface
    '''
    def __init__(self, widget, tag='stdout'):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state='normal')
        self.widget.insert('end', str, (self.tag,))
        self.widget.configure(state='disabled')
        self.widget.see(tk.END) # Scroll with text
