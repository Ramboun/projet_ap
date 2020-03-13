from enum import Enum

class STATE(Enum):
    # Etat possible d'une tâche
    NOT_DONE = '--'
    ON_GOING = '+/-' 
    DONE = '++'