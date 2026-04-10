import sys
import traceback
from typing import Optional, cast

"""What it does in simple words:
Finds the Crime Scene: It automatically looks through the "Traceback" (the history of the crash) to find the exact filename and line number where the mistake actually happened.
Cleans the Message: It takes whatever error happened (like a "File Not Found" error) and turns it into a simple string.
Formats the Output: It rearranges the messy error into a neat, readable format:
Error in [myfile.py] at line [42] | Message: something went wrong
Keeps the Evidence: It stores the full, "pretty" version of the crash details (the traceback) so you can print it later if you need to debug."""

class DocumentPortalException(Exception): # this line makes sure python treats your exception class as a real error 
    def __init__(self, error_message, error_details: Optional[object] = None):
        # Normalize message
        if isinstance(error_message, BaseException): # it safely handles other errors to be passed inside yours
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        # Resolve exc_info (supports: sys module, Exception object, or current context)
        #This block of code is basically a detective trying to find out exactly what went wrong and where. It’s looking for the "Traceback" (the list of file lines that led to the error)
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):  # e.g., sys
                #exc_type, exc_value, exc_tb = error_details.exc_info()
                exc_info_obj = cast(sys, error_details)
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk to the last frame to report the most relevant location
        #This final section of the code is the "Record Keeper." It takes all the raw error data found earlier and cleans it up so you can actually read it.

        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        # Full pretty traceback (if available)
        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self):
        # Compact, logger-friendly message (no leading spaces)
        base = f"Error in [{self.file_name}] at line [{self.lineno}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self):
        return f"DocumentPortalException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"