# CAB libraries
from cab.cab_system import ComplexAutomaton
from cab.cab_global_constants import GlobalConstants

# External libraries
import unittest

class GeneralTestCase(unittest.TestCase):
    """Tests for CAB System"""

    def test_startup(self):
        gc = GlobalConstants()
        simulation = ComplexAutomaton(gc)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
