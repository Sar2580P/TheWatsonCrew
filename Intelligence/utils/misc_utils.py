class Colored_Text:
    def __init__(self):
        self.tick , self.cross = '\u2713' , '\u2717'

    def red(self, skk, delimiter = '\n'): print("\033[91m {}\033[00m" .format(skk), end = delimiter)
    def green(self, skk, delimiter = '\n'): print("\033[92m {}\033[00m" .format(skk), end = delimiter)
    def yellow(self, skk,  delimiter = '\n'): print("\033[93m {}\033[00m" .format(skk) ,end = delimiter)
    def lightpurple(self, skk,  delimiter = '\n'): print("\033[94m {}\033[00m" .format(skk),end = delimiter)
    def purple(self, skk, delimiter = '\n'): print("\033[95m {}\033[00m" .format(skk),end = delimiter)
    def cyan(self, skk, delimiter = '\n'): print("\033[96m {}\033[00m" .format(skk),end = delimiter)
    def lightgray(self, skk, delimiter = '\n'): print("\033[97m {}\033[00m" .format(skk), end = delimiter)
    def black(self, skk, delimiter = '\n'): print("\033[98m {}\033[00m" .format(skk), end = delimiter)


pr = Colored_Text()
# import ast
# pr.red(ast.literal_eval('[\n("Disease" , "heart_muscle_inflammation_disease__Myocarditis"),\n("Disease" , "irregular_heart_rhythm_disease__Atrial_Fibrillation"),\n("Disease" , "blood_sugar_disease__Type_2_Diabetes_Mellitus"),\n("Disease" , "lung_disease__Chronic_Obstructive_Pulmonary_Disease"),\n("Disease" , "joint_inflammation_disease__Rheumatoid_Arthritis"),\n("Disease" , "high_blood_pressure_disease__Hypertension"),\n("Disease" , "blood_clot_disease__Deep_Vein_Thrombosis"),\n("Disease" , "stomach_acid_disease__Gastroesophageal_Reflux_Disease"),\n("Medicine" , "heart_rhythm_medicine__Amiodarone"),\n("Medicine" , "diabetes_medicine__Metformin"),\n("Medicine" , "diabetes_medicine__Insulin_Glargine"),\n("Medicine" , "lung_medicine__Tiotropium"),\n("Medicine" , "arthritis_medicine__Methotrexate"),\n("Medicine" , "arthritis_medicine__Etanercept"),\n("Medicine" , "blood_pressure_medicine__Amlodipine"),\n("Medicine" , "blood_pressure_medicine__Lisinopril"),\n("Medicine" , "blood_clot_medicine__Warfarin"),\n("Medicine" , "stomach_acid_medicine__Omeprazole")\n]'))
# pr.red(f"Hello  {pr.cross}", delimiter='\t')
# pr.green(f'Hello {pr.tick}', delimiter='\n')
# pr.yellow('Hello')

from colorama import Fore, Style
def assert_(condition: bool , message: str):
    assert condition, Fore.RED + message + Style.RESET_ALL
    
import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Create a custom logger
logger = logging.getLogger('custom_logger')
logger.setLevel(logging.DEBUG)  # Set the default logging level

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the logging level for the handler

# Create a formatter that includes the level name, message, and emoji
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
    }
    EMOJIS = {
        'DEBUG': '🐛',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        emoji = self.EMOJIS.get(record.levelname, '')
        record.msg = f"{log_color}{emoji} {record.msg}{Style.RESET_ALL}"
        return super().format(record)

formatter = ColoredFormatter('%(levelname)s: %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Log messages in various modes
# logger.debug("This is a debug message.")
# logger.info("This is an info message.")
# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.critical("This is a critical message.")
