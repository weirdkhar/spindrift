'''
Generic gui base classes
Common classes to be inherited by ccn_proccesing and cpc_processing
Author: Kristina Johnson, Ruhi Humphries
'''

import tkinter as tk
from tkinter import ttk

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GenericBaseGui(tk.Frame):
    '''
    Common gui class to be inherited by ccn_proccesing and cpc_processing
    '''
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
