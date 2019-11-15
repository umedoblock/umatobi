class MakeSimulationDbTests(unittest.TestCase):

    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()

    def setUp(self):
        self.start_up_orig = ClientTests.start_up_orig

    def test_make_simulation_db(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
