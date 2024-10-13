import os
import tkinter as tk
import csv
from datetime import datetime


class Stechuhr(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.overrideredirect(True)
        self.geometry('+0+0')
        self.label = tk.Label(self, font=('Helvetica', 48), bg='black', fg='white')
        self.label.pack()
        self.move_enabled = tk.BooleanVar(value=False)
        self.label.bind('<Button-2>', self.halt_resume)
        self.label.bind('<Button-3>', self.show_context_menu)
        self.start_time = datetime.now()
        self.running = True
        self.update_interval = 60 # in seconds
        self.elapsed_time = 0
        self.csv_file = 'time_log.csv'
        self.time_this_week = self.calcue_time_this_week()
        self.time_this_day = self.calculate_time_this_day()
        self.write_csv_header()
        self.update_clock()

    def open_settings(self, event):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        
        tk.Label(settings_window, text="Settings", font=('Helvetica', 14)).pack(pady=10)
        
        # Example setting: Update interval
        tk.Label(settings_window, text="Update Interval (seconds):").pack(pady=5)
        update_interval_entry = tk.Entry(settings_window)
        update_interval_entry.pack(pady=5)
        update_interval_entry.insert(0, str(self.update_interval))
        
        def save_settings():
            self.update_interval = int(update_interval_entry.get())
            settings_window.destroy()
        
        tk.Button(settings_window, text="Save", command=save_settings).pack(pady=20)
    
    def show_context_menu(self, event):
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Halt/Resume", command=lambda: self.halt_resume(event))
        context_menu.add_checkbutton(label="Move", variable=self.move_enabled, command=lambda: self.toggle_move(event))
        context_menu.add_command(label="Settings", command=lambda: self.open_settings(event))
        context_menu.add_command(label="Quit", command=lambda: self.quit())
        context_menu.post(event.x_root, event.y_root)
    
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

    def write_csv_header(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['KW', 'Datum', 'Start Zeit', 'End Zeit'])
    
    def calculate_time_this_day(self):
        date = datetime.now().strftime('%Y.%m.%d')
        time_this_day = 0
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[1] == date:
                        past_start_time = datetime.strptime(f'{row[1]} {row[2]}', '%Y.%m.%d %H:%M')
                        past_end_time = datetime.strptime(f'{row[1]} {row[3]}', '%Y.%m.%d %H:%M')
                        time_this_day += (past_end_time - past_start_time).total_seconds()
        return time_this_day

    def calcue_time_this_week(self):
        calendar_week = datetime.now().isocalendar()[1]
        time_this_week = 0
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == str(calendar_week) and row[1].split('.')[0] == str(datetime.now().year):
                        past_start_time = datetime.strptime(f'{row[1]} {row[2]}', '%Y.%m.%d %H:%M')
                        past_end_time = datetime.strptime(f'{row[1]} {row[3]}', '%Y.%m.%d %H:%M')
                        time_this_week += (past_end_time - past_start_time).total_seconds()
        return time_this_week

    def update_csv(self):
        calendar_week = datetime.now().isocalendar()[1]
        date = datetime.now().strftime('%Y.%m.%d')
        current_time = datetime.now().strftime('%H:%M')

        # Read the existing rows
        rows = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
        
        # For when the day changes
        if self.start_time.strftime('%Y.%m.%d') != date:
            if rows and rows[-1][1] == self.start_time.strftime('%Y.%m.%d') and rows[-1][2] == self.start_time.strftime('%H:%M'):
                rows[-1][3] = '23:59'
                rows.append([calendar_week, date, '00:00', current_time])
                self.start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                self.elapsed_time = datetime.now().strftime('%H:%M')
                with open(self.csv_file, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)
                self.time_this_day = 0
                self.time_this_week = self.calcue_time_this_week() - self.calculate_time_this_day()
            else:
                self.time_this_day = 0
                self.time_this_week = self.calcue_time_this_week()
                self.start_time = datetime.now()
                self.elapsed_time = 0
                rows.append([calendar_week, date, self.start_time, current_time])
        else:
            # Check if the last row has the same start date and start time
            if rows and rows[-1][1] == date and rows[-1][2] == self.start_time.strftime('%H:%M'):
                rows[-1][3] = current_time
            elif self.start_time.strftime('%H:%M') != current_time:
                rows.append([calendar_week, date, self.start_time.strftime('%H:%M'), current_time])
            else:
                return
            
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
    
    def week_time(self):
        total_time_this_week = self.time_this_week + self.elapsed_time.total_seconds()
        week_hours, week_remainder = divmod(int(total_time_this_week), 3600)
        week_minutes, week_seconds = divmod(week_remainder, 60)
        week_time_str = f'{week_hours:02}:{week_minutes:02}' #:{week_seconds:02}'
        return week_time_str

    def day_time(self):
        total_time_this_day = self.time_this_day + self.elapsed_time.total_seconds()
        day_hours, day_remainder = divmod(int(total_time_this_day), 3600)
        day_minutes, day_seconds = divmod(day_remainder, 60)
        day_time_str = f'{day_hours:02}:{day_minutes:02}' #:{day_seconds:02}'
        return day_time_str

    def update_clock(self):
        if self.running:
            self.elapsed_time = datetime.now() - self.start_time
            
            self.label.config(text=f'{self.week_time()}\n{self.day_time()}')
            self.update_csv()
        self.after(self.update_interval * 1000, self.update_clock)  # Update every second

    def halt_resume(self, event):
        if self.running:
            self.running = False
            self.label.config(fg='red')
        else:
            self.start_time = datetime.now()
            self.time_this_week = self.calcue_time_this_week()
            self.time_this_day = self.calculate_time_this_day()
            self.running = True
            self.label.config(fg='white')

if __name__ == '__main__':
    Stechuhr().mainloop()