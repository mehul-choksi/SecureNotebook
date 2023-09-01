from PyQt6.QtWidgets import QCalendarWidget
from PyQt6.QtCore import QDate
import time

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(200)
        self.fix_calendar_view_issue()
    
    # This function would fix the 'Saturday missing from calendar view' issue
    def fix_calendar_view_issue(self):
        ''' The calendar is rendered with week num column replacing the saturday col.
        This fix finds the next saturday and sets it in focus. By doing this the weeknum col is pushed out of view. 
        '''
        today = QDate.currentDate()
        days_to_next_saturday = (6 - today.dayOfWeek())%7
        print('Days to next saturday ', days_to_next_saturday)
        next_saturday = today.addDays(days_to_next_saturday)
        self.setSelectedDate(next_saturday)