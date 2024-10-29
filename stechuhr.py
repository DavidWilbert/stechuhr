import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from datetime import datetime
from os import path
import csv
import re
import yaml

class time_log():
    csv_file = []
    def __init__(self, parent, file_name='time_log.csv', delimiter=',', date_format='%Y.%m.%d', time_format='%H:%M:%S', custom_columns=None, custom_headers=None):
        self.parent = parent
        self.csv_file_name = file_name
        self.csv_delimiter = delimiter
        self.save_date_format = date_format
        self.save_time_format = time_format
        self.custom_columns = custom_columns if custom_columns else []
        self.custom_headers = custom_headers if custom_headers else ['CW', 'Date', 'Start Time', 'End Time']
        self.start_time = datetime.now()
        self.read_csv_file()
    
    def read_csv_file(self):
        try:
            if not path.exists(self.csv_file_name):
                self.write_csv_header()
            with open(self.csv_file_name, mode='r', newline='') as file:
                reader = csv.reader(file, delimiter=self.csv_delimiter)
                self.csv_file = list(reader)
            file.close()
            if len(self.csv_file) == 0:
                self.write_csv_header()
            else:
                self.correct_formats()
        except FileNotFoundError:
            self.write_csv_header()
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def correct_formats(self):
        try:
            if len(self.csv_file) > 0:
                first_row = self.csv_file[0]
                if len(first_row) == 1: # means it has the wrong delimiter
                    if re.match(r'^Format:[' + ''.join(self.delimiters) + ']', first_row[0]): # starts with 'Format:'
                        with open(self.csv_file_name, mode='r', newline='') as file:
                            self.csv_file = list(csv.reader(file, delimiter = re.search(r'^Format:(.)', first_row[0]).group(1))) # get the symbol after 'Format:' as delimiter
                        file.close()
                        return self.correct_formats() # check for the other formats
                    elif re.match(r'^\d{2}[' + ''.join(self.delimiters) + ']', first_row[0]): # starts with calendar week (2 digits followed by a delimiter)
                        with open(self.csv_file_name, mode='r', newline='') as file:
                            self.csv_file = list(csv.reader(file, delimiter = re.search(r'^\d{2}(.)', first_row[0]).group(1))) # get the symbol after the calendar week as delimiter
                        file.close()
                        return self.correct_formats() # check for the other formats
                    else: # check if the first row is a header row
                        raise Exception('format corrupted, try another delimiter')
                else:
                    format_row = ['Format:', self.save_date_format, self.save_time_format, self.save_time_format]
                    for row in self.csv_file:
                        if row[0] == 'Format:' and row != format_row:
                            if row[1] in self.date_formats:
                                self.save_date_format = row[1]
                                self.change_date_format(format_row[1])
                            if row[2] == row[3] and row[2] in self.time_formats:
                                self.save_time_format = row[2]
                                self.change_time_format(format_row[2])
        except Exception as e:
            print(f"An error occurred: {e}")

    def write_csv_header(self):
        try:
            if len(self.csv_file) == 0:
                format_row = ['Format:', self.save_date_format, self.save_time_format, self.save_time_format]
                self.csv_file.append(format_row)
                self.csv_file.append(self.custom_headers)
            if not path.exists(self.csv_file_name):
                with open(self.csv_file_name, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=self.csv_delimiter)
                    writer.writerows(self.csv_file)
                file.close()
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def write_csv(self):
        try:
            if not path.exists(self.csv_file_name):
                self.write_csv_header()
            with open(self.csv_file_name, mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=self.csv_delimiter)
                writer.writerows(self.csv_file)
            file.close()
        except FileNotFoundError:
            self.write_csv_header()
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def change_eveything(self, file_name, delimiter, date_format, time_format, custom_columns, custom_headers):
        if self.csv_file_name != file_name:
            self.change_csv_file_name(file_name)
        if self.csv_delimiter != delimiter:
            self.change_csv_delimiter(delimiter)
        if self.save_date_format != date_format:
            self.change_date_format(date_format)
        if self.save_time_format != time_format:
            self.change_time_format(time_format)
        if self.custom_columns != custom_columns:
            self.custom_columns = custom_columns
        if self.custom_headers != custom_headers:
            self.custom_headers = custom_headers

    def change_csv_file_name(self, file_name):
        if file_name == '': # empty string means no change
            raise Exception('file name cannot be empty')
        if not re.match(r'.*\.csv$', file_name): # if file_name does not end with .csv, add it
            file_name += '.csv'
        if self.csv_file_name == file_name:
            return
        if path.exists(file_name):
            raise Exception('file already exists')
        self.csv_file_name = file_name
        self.write_csv()

    def change_csv_delimiter(self, delimiter):
        if self.csv_delimiter == delimiter:
            return
        self.csv_delimiter = delimiter
        self.write_csv()
    
    def change_date_format(self, date_format):
        if self.save_date_format == date_format:
            return
        # iterate over all rows and change the date format
        for row in self.csv_file:
            if len(row) > 1 and re.match(r'^\d', row[1]): # starts with a digit (so no format row or header)
                row[1] = datetime.strptime(row[1], self.save_date_format).strftime(date_format)
            elif len(row) > 1 and row[0] == 'Format:': # format row
                row[1] = date_format
        self.save_date_format = date_format
        self.write_csv()
    
    def change_time_format(self, time_format):
        if self.save_time_format == time_format:
            return
        # iterate over all rows and change the time format
        for row in self.csv_file:
            if len(row) > 2 and re.match(r'^\d', row[2]): # starts with a digit (so no format row or header)
                row[2] = datetime.strptime(row[2], self.save_time_format).strftime(time_format)
                row[3] = datetime.strptime(row[3], self.save_time_format).strftime(time_format)
            elif len(row) > 2 and row[0] == 'Format:':
                row[2] = time_format
                row[3] = time_format
        self.save_time_format = time_format
        self.write_csv()

    def time_this_day(self):
        format = f'{self.save_date_format} {self.save_time_format}'
        date = datetime.now().strftime(self.save_date_format)
        time_this_day = 0
        for row in self.csv_file[::-1]:
            if row[1] == date:
                past_start_time = datetime.strptime(f'{row[1]} {row[2]}', format)
                past_end_time = datetime.strptime(f'{row[1]} {row[3]}', format)
                time_this_day += (past_end_time - past_start_time).total_seconds()
            else: break
        return time_this_day

    def time_this_week(self):
        format = f'{self.save_date_format} {self.save_time_format}'
        calendar_week = str(datetime.now().isocalendar()[1])
        year = datetime.now().year
        time_this_week = 0
        for row in self.csv_file[::-1]:
            if row[0] == calendar_week:
                if year == datetime.strptime(row[1], self.save_date_format).year:
                    past_start_time = datetime.strptime(f'{row[1]} {row[2]}', format)
                    past_end_time = datetime.strptime(f'{row[1]} {row[3]}', format)
                    time_this_week += (past_end_time - past_start_time).total_seconds()
                else: break
            else: break
        return time_this_week
    
    def time_this_month(self):
        format = f'{self.save_date_format} {self.save_time_format}'
        year, month = datetime.now().year, datetime.now().month
        time_this_month = 0
        for row in self.csv_file[::-1]:
            if re.match(r'\d{2}', row[0]):
                date = datetime.strptime(row[1], self.save_date_format)
                if month == date.month and year == date.year:
                    past_start_time = datetime.strptime(f'{row[1]} {row[2]}', format)
                    past_end_time = datetime.strptime(f'{row[1]} {row[3]}', format)
                    time_this_month += (past_end_time - past_start_time).total_seconds()
                else: break
            else: break
        return time_this_month

    def update_csv(self):
        calendar_week = str(datetime.now().isocalendar()[1])
        date = datetime.now().strftime(self.save_date_format)
        current_time = datetime.now().strftime(self.save_time_format)
        
        # For when the day changes
        if self.start_time.strftime(self.save_date_format) == date:
            # Check if the last row has the same start date and start time
            if self.csv_file and self.csv_file[-1][1] == date and self.csv_file[-1][2] == self.start_time.strftime(self.save_time_format):
                self.csv_file[-1][3] = current_time
            elif self.start_time.strftime(self.save_time_format) != current_time:
                self.csv_file.append([calendar_week, date, self.start_time.strftime(self.save_time_format), current_time])
        else:
            if self.csv_file and self.csv_file[-1][1] == self.start_time.strftime(self.save_date_format) and self.csv_file[-1][2] == self.start_time.strftime(self.save_time_format):
                self.csv_file[-1][3] = datetime(2000, 1, 1, 23, 59, 59).strftime(self.save_time_format)
                self.csv_file.append([calendar_week, date, datetime(2000, 1, 1, 0, 0, 0).strftime(self.save_time_format), current_time])
                self.start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                self.start_time = datetime.now()
                self.csv_file.append([calendar_week, date, self.start_time, current_time])
        self.write_csv()

class settings_window():
    time_log_delimiters = [',', ';']
    time_log_date_formats = ['%Y-%m-%d', '%Y.%m.%d', '%d.%m.%Y', '%m.%d.%Y']
    time_log_time_formats = ['%H:%M:%S', '%H:%M', '%H']
    custom_columns_options = ['calendar week', 'date', 'start time', 'end time', 'time this day', 'time this week', 'time this month']
    def __init__(self, parent):
        self.parent = parent
        self.fonts = tkfont.families()
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title('Settings')
        self.settings_window.geometry('400x400')
        
        self.settings_frame = tk.Frame(self.settings_window)
        self.settings_frame.pack()

        self.time_log_frame = tk.LabelFrame(self.settings_frame, text='Time Log')
        self.time_log_frame.pack(fill='both', expand=True)
        self.time_log_file_name_label = tk.Label(self.time_log_frame, text='File Name:')
        self.time_log_file_name_label.pack()
        self.time_log_file_name_entry = tk.Entry(self.time_log_frame)
        self.time_log_file_name_entry.pack()
        self.time_log_delimiter_label = tk.Label(self.time_log_frame, text='Delimiter:')
        self.time_log_delimiter_label.pack()
        self.time_log_delimiter_combobox = ttk.Combobox(self.time_log_frame, values=self.time_log_delimiters)
        self.time_log_delimiter_combobox.pack()
        self.time_log_date_format_label = tk.Label(self.time_log_frame, text='Date Format:')
        self.time_log_date_format_label.pack()
        self.time_log_date_format_combobox = ttk.Combobox(self.time_log_frame, values=self.time_log_date_formats)
        self.time_log_date_format_combobox.pack()
        self.time_log_time_format_label = tk.Label(self.time_log_frame, text='Time Format:')
        self.time_log_time_format_label.pack()
        self.time_log_time_format_combobox = ttk.Combobox(self.time_log_frame, values=self.time_log_time_formats)
        self.time_log_time_format_combobox.pack()
        self.time_log_save_button = tk.Button(self.time_log_frame, text='Save', command=lambda: self.save_time_log_settings())
        self.time_log_save_button.pack()
        
        self.custom_columns_label = tk.Label(self.time_log_frame, text='Custom Columns:')
        self.custom_columns_label.pack()
        self.custom_columns_listbox = tk.Listbox(self.time_log_frame, selectmode=tk.MULTIPLE)
        for option in self.custom_columns_options:
            self.custom_columns_listbox.insert(tk.END, option)
        self.custom_columns_listbox.pack()
        
        self.add_column_button = tk.Button(self.time_log_frame, text='Add New Column', command=self.add_new_column)
        self.add_column_button.pack()
        
        self.custom_headers_label = tk.Label(self.time_log_frame, text='Custom Headers:')
        self.custom_headers_label.pack()
        self.custom_headers_entry = tk.Entry(self.time_log_frame)
        self.custom_headers_entry.pack()

        self.settings_frame.pack()
        self.show_settings()

    def show_settings(self):
        self.time_log_file_name_entry.insert(0, self.parent.settings['time_log_file_name'])
        self.time_log_delimiter_combobox.set(self.parent.settings['time_log_delimiter'])
        self.time_log_date_format_combobox.set(self.parent.settings['time_log_date_format'])
        self.time_log_time_format_combobox.set(self.parent.settings['time_log_time_format'])
        for column in self.parent.settings.get('custom_columns', []):
            index = self.custom_columns_options.index(column)
            self.custom_columns_listbox.select_set(index)
        self.custom_headers_entry.insert(0, ','.join(self.parent.settings.get('custom_headers', [])))

    def save_time_log_settings(self):
        self.parent.settings['time_log_file_name'] = self.time_log_file_name_entry.get()
        self.parent.settings['time_log_delimiter'] = self.time_log_delimiter_combobox.get()
        self.parent.settings['time_log_date_format'] = self.time_log_date_format_combobox.get()
        self.parent.settings['time_log_time_format'] = self.time_log_time_format_combobox.get()
        self.parent.settings['custom_columns'] = [self.custom_columns_listbox.get(i) for i in self.custom_columns_listbox.curselection()]
        self.parent.settings['custom_headers'] = self.custom_headers_entry.get().split(',')
        self.write_settings()
        self.parent.time_log.change_everything(self.parent.settings['time_log_file_name'], self.parent.settings['time_log_delimiter'], self.parent.settings['time_log_date_format'], self.parent.settings['time_log_time_format'], self.parent.settings['custom_columns'], self.parent.settings['custom_headers'])
        self.settings_window.destroy()
        self.write_settings()

    def add_new_column(self):
        new_column_window = tk.Toplevel(self.settings_window)
        new_column_window.title('Add New Column')
        new_column_window.geometry('300x200')
        
        new_column_label = tk.Label(new_column_window, text='Column Name:')
        new_column_label.pack()
        new_column_entry = tk.Entry(new_column_window)
        new_column_entry.pack()
        
        new_header_label = tk.Label(new_column_window, text='Header:')
        new_header_label.pack()
        new_header_entry = tk.Entry(new_column_window)
        new_header_entry.pack()
        
        def save_new_column():
            column_name = new_column_entry.get()
            header = new_header_entry.get()
            if column_name and header:
                self.custom_columns_options.append(column_name)
                self.custom_columns_listbox.insert(tk.END, column_name)
                self.parent.settings['custom_headers'].append(header)
                new_column_window.destroy()
        
        save_button = tk.Button(new_column_window, text='Save', command=save_new_column)
        save_button.pack()

    def write_settings(self):
        try:
            settings_file = open('settings.yml', 'w')
            yaml.dump(self.parent.settings, settings_file)
            settings_file.close()
        except Exception as e:
            print(f"An error occurred: {e}")

class widget(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.settings = {}
        self.read_settings()
        self.time_log = time_log(self, file_name=self.settings['time_log_file_name'], delimiter=self.settings['time_log_delimiter'], date_format=self.settings['time_log_date_format'], time_format=self.settings['time_log_time_format'], custom_columns=self.settings.get('custom_columns', []), custom_headers=self.settings.get('custom_headers', []))
        self.overrideredirect(True)
        self.geometry('+0+0')
        self.label = tk.Label(self, font=('Helvetica', 48), bg='black', fg='white')
        self.label.pack()
        self.move_enabled = tk.BooleanVar(value=False)
        self.label.bind('<Button-2>', self.halt_resume)
        self.label.bind('<Button-3>', self.show_context_menu)
        self.running = True
        self.update_interval = 60 # in seconds
        self.elapsed_time = 0
        self.update_clock()
    
    def read_settings(self):
        try:
            if path.exists('settings.yml'):
                settings_file = open('settings.yml', 'r')
                self.settings = yaml.safe_load(settings_file)
                settings_file.close()
            else:
                self.settings = {'time_log_file_name': 'time_log.csv', 'time_log_delimiter': ';', 'time_log_date_format': '%Y.%m.%d', 'time_log_time_format': '%H:%M'}
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def show_context_menu(self, event):
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Halt/Resume", command=lambda: self.halt_resume(event))
        context_menu.add_checkbutton(label="Move", variable=self.move_enabled, command=lambda: self.toggle_move(event))
        context_menu.add_command(label="Settings", command=lambda: settings_window(self))
        context_menu.add_command(label="Quit", command=lambda: self.quit())
        context_menu.post(event.x_root, event.y_root)
    
    def halt_resume(self, event):
        if self.running:
            self.running = False
            self.label.config(fg='red')
        else:
            self.time_log.start_time = datetime.now()
            self.running = True
            self.label.config(fg='white')
    
    def toggle_move(self, event):
        if self.move_enabled.get():
            self.bind("<Button-1>", self.start_move)
            self.bind("<B1-Motion>", self.do_move)
        else:
            self.unbind("<Button-1>")
            self.unbind("<B1-Motion>")

    def start_move(self, event):
        if self.move_enabled.get():
            self.x = event.x
            self.y = event.y

    def do_move(self, event):
        if self.move_enabled.get():
            deltax = event.x - self.x
            deltay = event.y - self.y
            new_x = self.winfo_x() + deltax
            new_y = self.winfo_y() + deltay
            self.geometry(f"+{new_x}+{new_y}")
    
    def calculete_time_string(self, total_seconds):
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f'{hours:02}:{minutes:02}:{seconds:02}'
        return time_str
    
    def update_clock(self):
        if self.running:
            self.label.config(text=f'{self.calculete_time_string(self.time_log.time_this_day())}\n{self.calculete_time_string(self.time_log.time_this_week())}\n{self.calculete_time_string(self.time_log.time_this_month())}')
            self.time_log.update_csv()
        self.after(self.update_interval * 1000, self.update_clock)  # Update every second

if __name__ == '__main__':
    widget().mainloop()
